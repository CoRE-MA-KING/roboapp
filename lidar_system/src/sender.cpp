#include <gflags/gflags.h>
#include <rplidar.h>
#include <signal.h>

#include <chrono>
#include <future>
#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include "lidar_device/lidar_device_manager.hpp"
#include "lidar_types/lidar_data.hpp"
#include "zenoh.hxx"

DEFINE_string(
    c, "", "config file path: Default `$XDG_CONFIG_DIR/roboapp/config.toml`");

volatile sig_atomic_t ctrl_c_pressed = 0;

void ctrlc_handler(int) { ctrl_c_pressed = 1; }

void run_lidar_thread(std::string name, LiDARDeviceConfig config,
                      zenoh::Session& session) {
  auto publisher = session.declare_publisher(  //
      zenoh::KeyExpr("lidar/data"));

  auto data = LiDARDataWrapper(name, config.x, config.y);
  const int max_consecutive_errors = 3;

  LiDARDeviceManager manager(name, config);

  std::cout << "LiDAR " << name << " initialized successfully." << std::endl;

  int consecutive_errors = 0;
  while (!ctrl_c_pressed) {
    data.clear();

    try {
      if (manager.get(data)) {
        publisher.put(data.dump());
        consecutive_errors = 0;
        std::this_thread::yield();
      } else {
        consecutive_errors++;
        if (consecutive_errors >= max_consecutive_errors) {
          std::cerr << "LiDAR " << name << " timed out " << consecutive_errors
                    << " times in a row. Restarting..." << std::endl;
          throw std::runtime_error("Too many consecutive errors");
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
      }
    } catch (const std::exception& e) {
      // Re-throw to be caught by the supervisor
      throw;
    }
  }
}

struct LidarTask {
  std::string name;
  LiDARDeviceConfig config;
  std::future<void> handle;
};

int main(int argc, char* argv[]) {
  // Flag Setup
  gflags::SetUsageMessage("How To Use");
  gflags::SetVersionString("1.0.0");

  gflags::ParseCommandLineFlags(&argc, &argv, true);
  signal(SIGINT, ctrlc_handler);

  auto config_file = get_config_file(FLAGS_c);
  auto lidar_config_all = LiDARConfig(config_file);

  // Zenoh Setup
  auto zenoh_config =
      zenoh::Config::from_file((get_default_path() / "zenoh.json5").string());
  auto session = zenoh::Session(std::move(zenoh_config));

  // Initialize tasks
  std::vector<LidarTask> tasks;
  for (const auto& [name, config] : lidar_config_all.devices) {
    tasks.push_back({name, config,
                     std::async(std::launch::async, run_lidar_thread, name,
                                config, std::ref(session))});
  }

  std::cout << "Started " << tasks.size() << " LiDAR threads." << std::endl;

  // Supervisor Loop
  while (!ctrl_c_pressed) {
    for (auto& task : tasks) {
      if (task.handle.valid() && task.handle.wait_for(std::chrono::seconds(
                                     0)) == std::future_status::ready) {
        try {
          task.handle.get();  // Retrieve potential exceptions
        } catch (const std::exception& e) {
          std::cerr << "Task " << task.name << " failed: " << e.what()
                    << std::endl;
        } catch (...) {
          std::cerr << "Task " << task.name << " failed with unknown error."
                    << std::endl;
        }

        std::cout << "Restarting task: " << task.name << " in 1 second..."
                  << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(1));

        // Respawn
        task.handle = std::async(std::launch::async, run_lidar_thread,
                                 task.name, task.config, std::ref(session));
      }
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  }

  std::cout << "Stopping..." << std::endl;
  for (auto& task : tasks) {
    if (task.handle.valid()) {
      try {
        task.handle.get();  // Ensure any pending exceptions are rethrown and
                            // handled
      } catch (const std::exception& e) {
        std::cerr << "Task " << task.name
                  << " finished with exception: " << e.what() << std::endl;
      } catch (...) {
        std::cerr << "Task " << task.name << " finished with unknown error."
                  << std::endl;
      }
    }
  }
  return 0;
}
