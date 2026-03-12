#include <gflags/gflags.h>

#include <chrono>
#include <cstdint>
#include <iostream>
#include <lidar_types/lidar_data.hpp>
#include <mutex>
#include <opencv2/opencv.hpp>
#include <thread>

#include "collision_avoidance/collision_avoidance.hpp"
#include "config.hpp"
#include "lidar_metadata.hpp"
#include "proto/roboapp/lidar_vector.pb.h"
#include "visualizer/visualizer.hpp"
#include "zenoh.hxx"

DEFINE_string(
    c, "", "config file path: Default `$XDG_CONFIG_DIR/roboapp/config.toml`");

std::chrono::system_clock::time_point ntp64_to_timepoint(uint64_t ntp64) {
  uint32_t seconds = (ntp64 >> 32);  // NTPエポックからの秒数
  uint32_t fraction = ntp64 & 0xFFFFFFFF;

  // 小数部をナノ秒に変換
  uint64_t nanos = (static_cast<uint64_t>(fraction) * 1000000000ULL) >> 32;

  return std::chrono::system_clock::time_point{std::chrono::seconds(seconds) +
                                               std::chrono::nanoseconds(nanos)};
}

int main(int argc, char **argv) {
  // Flag Setup
  gflags::SetUsageMessage("How To Use");
  gflags::SetVersionString("1.0.0");

  gflags::ParseCommandLineFlags(&argc, &argv, true);

  std::map<std::string,
           std::tuple<std::chrono::system_clock::time_point, LiDARDataWrapper>>
      lidar_timestamps;

  lidar_vector vec;
  std::mutex mtx;
  auto config_file = get_config_file(FLAGS_c);
  auto lidar_config_all = LiDARConfig(config_file);

  bool updated = true;

  auto visualizer = Visualizer(lidar_config_all, 600);

  // Zenoh Setup
  auto zenoh_config =
      zenoh::Config::from_file((get_default_path() / "zenoh.json5").string());

  auto session = zenoh::Session(std::move(zenoh_config));
  session.declare_background_subscriber(  //
      zenoh::KeyExpr("lidar/data"),       //
      [&lidar_timestamps, &updated, &mtx](const zenoh::Sample &sample) {
        auto timestamp = ntp64_to_timepoint(sample.get_timestamp()->get_time());

        auto data = sample.get_payload().as_vector();
        auto z = LiDARDataWrapper(data);

        {
          std::lock_guard<std::mutex> lock(mtx);
          lidar_timestamps[z.name] = {
              timestamp,
              z,
          };

          updated = true;
        }
      },
      zenoh::closures::none);

  session.declare_background_subscriber(     //
      zenoh::KeyExpr("lidar/force_vector"),  //
      [&vec, &updated, &mtx](const zenoh::Sample &sample) {
        auto timestamp = ntp64_to_timepoint(sample.get_timestamp()->get_time());

        auto id = sample.get_timestamp()->get_id().to_string();

        auto payload = sample.get_payload().as_vector();

        roboapp::LiDARVector vec_msg;

        if (!vec_msg.ParseFromArray(payload.data(), payload.size())) {
          std::cerr << "Failed to parse LiDARVector message." << std::endl;

          return;
        }

        {
          std::lock_guard<std::mutex> lock(mtx);
          vec.linear = vec_msg.linear();
          vec.angular = vec_msg.angular();

          updated = true;
        }
      },
      zenoh::closures::none);

  while (true) {
    auto now = std::chrono::system_clock::now();
    std::vector<cv::Point2d> data;
    lidar_vector current_vec;
    bool current_updated = false;

    {
      std::lock_guard<std::mutex> lock(mtx);
      for (auto it = lidar_timestamps.begin(); it != lidar_timestamps.end();) {
        if (now - std::get<0>(it->second) >
            std::chrono::seconds(lidar_config_all.duration_seconds)) {
          updated = true;
          it = lidar_timestamps.erase(it);
        } else {
          ++it;
        }
      }

      current_updated = updated;
      if (current_updated) {
        for (auto &[id, pair] : lidar_timestamps) {
          auto &[timestamp, lidar_data] = pair;
          auto p = lidar_data.getPoint();
          data.insert(data.end(), p.begin(), p.end());
        }
        current_vec = vec;
        updated = false;
      }
    }

    if (current_updated) {
      cv::imshow("multiple",
                 visualizer.multipleVisualize(data, current_vec.linear,
                                              current_vec.angular));
      cv::waitKey(1);
    } else {
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
  }

  return 0;
}
