#include <gflags/gflags.h>

#include <chrono>
#include <cstdint>
#include <iostream>
#include <lidar_types/lidar_data.hpp>
#include <opencv2/opencv.hpp>
#include <thread>

#include "collision_avoidance/collision_avoidance.hpp"
#include "config.hpp"
#include "lidar_metadata.hpp"
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

  RepulsiveForceVector vec;
  auto config_file = get_config_file(FLAGS_c);
  auto global_config = GlobalConfig(config_file);
  auto lidar_config_all = LiDARConfig(config_file);

  bool updated = true;

  auto visualizer = Visualizer(lidar_config_all, 600);

  // Zenoh Setup
  auto prefix = std::string("");
  if (global_config.zenoh_prefix.has_value()) {
    prefix = global_config.zenoh_prefix.value() + "/";
  }

  auto zenoh_config = zenoh::Config::create_default();
  zenoh_config.insert_json5(Z_CONFIG_ADD_TIMESTAMP_KEY, "true");

  auto session = zenoh::Session(std::move(zenoh_config));
  session.declare_background_subscriber(      //
      zenoh::KeyExpr(prefix + "lidar/data"),  //
      [&lidar_timestamps, &updated](const zenoh::Sample &sample) {
        auto timestamp = ntp64_to_timepoint(sample.get_timestamp()->get_time());

        auto id = sample.get_timestamp()->get_id().to_string();
        auto data = sample.get_payload().as_vector();
        auto z = LiDARDataWrapper(data);

        lidar_timestamps[id] = {
            timestamp,
            z,
        };

        updated = true;
      },
      zenoh::closures::none);

  session.declare_background_subscriber(              //
      zenoh::KeyExpr(prefix + "lidar/force_vector"),  //
      [&vec, &updated](const zenoh::Sample &sample) {
        auto timestamp = ntp64_to_timepoint(sample.get_timestamp()->get_time());

        auto id = sample.get_timestamp()->get_id().to_string();
        auto data = sample.get_payload().as_string();
        vec = RepulsiveForceVector(data);

        updated = true;
      },
      zenoh::closures::none);
  while (true) {
    auto now = std::chrono::system_clock::now();
    std::vector<cv::Point2d> data;

    for (auto it = lidar_timestamps.begin(); it != lidar_timestamps.end();) {
      if (now - std::get<0>(it->second) >
          std::chrono::seconds(lidar_config_all.duration_seconds)) {
        updated = true;
        it = lidar_timestamps.erase(it);
      } else {
        ++it;
      }
    }

    if (updated) {
      for (auto &[id, pair] : lidar_timestamps) {
        auto &[timestamp, lidar_data] = pair;
        auto p = lidar_data.getPoint();
        data.insert(data.end(), p.begin(), p.end());
      }

      cv::imshow("multiple", visualizer.multipleVisualize(data, vec));
      cv::waitKey(1);
    } else {
      std::this_thread::sleep_for(std::chrono::microseconds(1));
    }

    updated = false;
  }

  return 0;
}
