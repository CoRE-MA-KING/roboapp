#include <gflags/gflags.h>
#include <signal.h>

#include <chrono>
#include <cstdint>
#include <future>
#include <iostream>
#include <map>
#include <mutex>
#include <thread>
#include <vector>

#include "collision_avoidance/collision_avoidance.hpp"
#include "config.hpp"
#include "lidar_device/lidar_device_manager.hpp"
#include "lidar_types/lidar_data.hpp"
#include "proto/roboapp/lidar_range.pb.h"
#include "proto/roboapp/lidar_vector.pb.h"
#include "visualizer/range_separater.hpp"
#include "zenoh.hxx"

DEFINE_string(
    c, "", "config file path: Default `$XDG_CONFIG_DIR/roboapp/config.toml`");

volatile sig_atomic_t ctrl_c_pressed = 0;

void ctrlc_handler(int) { ctrl_c_pressed = 1; }

using LidarSharedState =
    std::map<std::string, std::tuple<std::chrono::system_clock::time_point,
                                     LiDARDataWrapper>>;

void run_lidar_thread(std::string name, LiDARDeviceConfig config,
                      zenoh::Session& session, LidarSharedState& timestamps,
                      std::mutex& mtx, bool& updated) {
  auto publisher = session.declare_publisher(  //
      zenoh::KeyExpr("lidar/data"));

  auto data = LiDARDataWrapper(name, config.x, config.y);
  const int max_consecutive_errors = 3;

  std::unique_ptr<LiDARDeviceManager> manager;
  bool error_logged = false;
  int consecutive_errors = 0;

  while (!ctrl_c_pressed) {
    if (!manager) {
      try {
        manager = std::make_unique<LiDARDeviceManager>(name, config);
        std::cout << "LiDAR " << name << " initialized successfully."
                  << std::endl;
        error_logged = false;
      } catch (const std::exception& e) {
          if (!error_logged) {
            std::cerr << "LiDAR " << name << " initialization failed: " << e.what()
                      << ". Retrying every 5s..." << std::endl;
            error_logged = true;
          }
          // Check ctrl_c_pressed every 100ms for 5 seconds
          for (int i = 0; i < 50 && !ctrl_c_pressed; ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
          }
          continue;
        }
    }

    data.clear();

    try {
      if (manager->get(data)) {
        auto now = std::chrono::system_clock::now();
        {
          std::lock_guard<std::mutex> lock(mtx);
          timestamps[name] = {now, data};
          updated = true;
        }
        publisher.put(data.dump());
        consecutive_errors = 0;
        std::this_thread::yield();
      } else {
        consecutive_errors++;
        if (consecutive_errors >= max_consecutive_errors) {
          std::cerr << "LiDAR " << name << " timed out " << consecutive_errors
                    << " times in a row. Resetting manager..." << std::endl;
          manager.reset();
          consecutive_errors = 0;
          std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
      }
    } catch (const std::exception& e) {
      if (!error_logged) {
        std::cerr << "LiDAR " << name << " runtime error: " << e.what()
                  << ". Resetting manager..." << std::endl;
        error_logged = true;
      }
      manager.reset();
      std::this_thread::sleep_for(std::chrono::seconds(1));
    }
  }
}

struct LidarTask {
  std::string name;
  LiDARDeviceConfig config;
  std::future<void> handle;
  int restart_count = 0;
  std::chrono::system_clock::time_point next_restart_time =
      std::chrono::system_clock::now();
};

int main(int argc, char** argv) {
  // Flag Setup
  gflags::SetUsageMessage("LiDAR Processor (Integrated)");
  gflags::SetVersionString("1.0.0");

  gflags::ParseCommandLineFlags(&argc, &argv, true);
  signal(SIGINT, ctrlc_handler);

  auto config_file = get_config_file(FLAGS_c);
  auto lidar_config_all = LiDARConfig(config_file);

  LidarSharedState timestamps;
  std::mutex mtx;
  bool updated = true;

  // Collision Avoidance
  auto collision_avoidance = CollisionAvoidance(
      lidar_config_all.robot_width, lidar_config_all.robot_length,
      lidar_config_all.repulsive_gain, lidar_config_all.influence_range);

  // Zenoh Setup
  auto zenoh_config =
      zenoh::Config::from_file((get_default_path() / "zenoh.json5").string());
  auto session = zenoh::Session(std::move(zenoh_config));

  auto vec_publisher =
      session.declare_publisher(zenoh::KeyExpr("lidar/force_vector"));
  auto range_publisher =
      session.declare_publisher(zenoh::KeyExpr("lidar/range"));

  // Initialize LiDAR tasks
  std::vector<LidarTask> tasks;
  for (const auto& [name, config] : lidar_config_all.devices) {
    tasks.push_back({name, config,
                     std::async(std::launch::async, run_lidar_thread, name,
                                config, std::ref(session), std::ref(timestamps),
                                std::ref(mtx), std::ref(updated))});
  }

  // Supervisor Thread: Monitor and restart LiDAR tasks without blocking the
  // main loop
  std::thread supervisor([&tasks, &session, &timestamps, &mtx, &updated]() {
    while (!ctrl_c_pressed) {
      auto now = std::chrono::system_clock::now();
      for (auto& task : tasks) {
        if (task.handle.valid() && task.handle.wait_for(std::chrono::seconds(
                                       0)) == std::future_status::ready) {
          try {
            task.handle.get();  // Check for exceptions
            task.restart_count = 0;
          } catch (const std::exception& e) {
            std::cerr << "Task " << task.name << " crashed: " << e.what()
                      << std::endl;
            task.restart_count++;
          }

          // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s (max)
          int backoff_power = std::max(0, task.restart_count - 1);
          int delay = std::min(32, (1 << backoff_power));

          task.next_restart_time = now + std::chrono::seconds(delay);
          std::cerr << "Task " << task.name << " scheduled to restart in "
                    << delay
                    << " seconds (restart count: " << task.restart_count << ")."
                    << std::endl;

          task.handle = std::future<void>();
        }

        if (!task.handle.valid() && now >= task.next_restart_time &&
            !ctrl_c_pressed) {
          std::cerr << "Restarting task: " << task.name << std::endl;
          task.handle =
              std::async(std::launch::async, run_lidar_thread, task.name,
                         task.config, std::ref(session), std::ref(timestamps),
                         std::ref(mtx), std::ref(updated));
        }
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
  });

  std::cout << "Started " << tasks.size() << " LiDAR threads." << std::endl;

  // Main Calculation Loop
  while (!ctrl_c_pressed) {
    auto now = std::chrono::system_clock::now();
    std::vector<cv::Point2d> data;
    bool current_updated = false;

    {
      std::lock_guard<std::mutex> lock(mtx);
      // Remove stale data
      for (auto it = timestamps.begin(); it != timestamps.end();) {
        if (now - std::get<0>(it->second) >
            std::chrono::seconds(lidar_config_all.duration_seconds)) {
          updated = true;
          it = timestamps.erase(it);
        } else {
          ++it;
        }
      }

      current_updated = updated;
      if (current_updated) {
        for (auto& [id, pair] : timestamps) {
          auto& [timestamp, lidar_data] = pair;
          auto p = lidar_data.getPoint();
          data.insert(data.end(), p.begin(), p.end());
        }
        updated = false;
      }
    }

    if (current_updated) {
      // Calculate Repulsive Force
      auto [lin, ang] = collision_avoidance.calcRepulsiveForce(data);
      roboapp::LiDARVector vec_msg;
      vec_msg.set_linear(lin);
      vec_msg.set_angular(std::fmod(360.f - ang, 360));
      vec_publisher.put(vec_msg.SerializeAsString());

      // Calculate Range
      auto range_data = rangeSeparater(data);
      roboapp::LiDARRange range_pb;
      range_pb.set_left(range_data.left);
      range_pb.set_right(range_data.right);
      range_pb.set_rear_left(range_data.rear_left);
      range_pb.set_rear_right(range_data.rear_right);

      range_publisher.put(range_pb.SerializeAsString());
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }

  std::cout << "Stopping..." << std::endl;
  if (supervisor.joinable()) {
    supervisor.join();
  }

  for (auto& task : tasks) {
    if (task.handle.valid()) {
      try {
        task.handle.get();
      } catch (...) {
      }
    }
  }

  return 0;
}
