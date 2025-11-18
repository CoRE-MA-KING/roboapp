#include <gflags/gflags.h>

#include <chrono>
#include <cstdint>
#include <iostream>
#include <lidar_types/lidar_data.hpp>
#include <opencv2/opencv.hpp>
#include <thread>

#include "collision_avoidance/collision_avoidance.hpp"
#include "config.hpp"
#include "degree2position.hpp"
#include "lidar_metadata.hpp"
#include "visualizer.hpp"
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
      timestamps;
  std::map<std::string, LidarMetadata> metadata_map;

  auto config_file = get_config_file(FLAGS_c);
  auto global_config = GlobalConfig(config_file);
  auto lidar_config_all = LiDARConfig(config_file);

  bool updated = false;

  // Collision Avoidance
  auto collision_avoidance = CollisionAvoidance(
      lidar_config_all.robot_width, lidar_config_all.robot_length,
      lidar_config_all.repulsive_gain, lidar_config_all.influence_range);

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
      [&timestamps, &updated](const zenoh::Sample &sample) {
        auto timestamp = ntp64_to_timepoint(sample.get_timestamp()->get_time());

        auto id = sample.get_timestamp()->get_id().to_string();
        auto data = sample.get_payload().as_vector();
        auto z = LiDARDataWrapper(data);

        timestamps[id] = {
            timestamp,
            z,
        };

        updated = true;
      },
      zenoh::closures::none);

  auto vec_publisher =
      session.declare_publisher(zenoh::KeyExpr(prefix + "lidar/force_vector"));

  while (true) {
    auto now = std::chrono::system_clock::now();

    for (auto it = timestamps.begin(); it != timestamps.end();) {
      if (now - std::get<0>(it->second) > std::chrono::seconds(5)) {
        cv::destroyWindow(it->first);
        it = timestamps.erase(it);
        metadata_map.erase(it->first);
      } else {
        ++it;
      }
    }

    if (updated) {
      std::vector<cv::Point2d> data;
      for (auto &[id, pair] : timestamps) {
        auto &[timestamp, lidar_data] = pair;
        for (auto &z : lidar_data.get()) {
          data.push_back(
              degree2position(lidar_data.x, lidar_data.y, z.first, z.second));
        }
      }
      auto vec = collision_avoidance.calcRepulsiveForce(data);

      vec_publisher.put("{\"linear\":" + std::to_string(vec.linear) +
                        ",\"angular\":" + std::to_string(vec.angular) + "}");

      cv::imshow("multiple", multipleVisualize(data, 600));
      cv::waitKey(1);
    }

    updated = false;

    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }

  return 0;
}