#include <gflags/gflags.h>

#include <chrono>
#include <cstdint>
#include <iostream>
#include <lidar_types/lidar_data.hpp>
#include <opencv2/opencv.hpp>
#include <thread>

#include "collision_avoidance/collision_avoidance.hpp"
#include "config.hpp"
#include "visualizer/range_separater.hpp"
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

  auto config_file = get_config_file(FLAGS_c);
  auto global_config = GlobalConfig(config_file);
  auto lidar_config_all = LiDARConfig(config_file);

  bool updated = true;

  // Collision Avoidance
  auto collision_avoidance = CollisionAvoidance(
      lidar_config_all.robot_width, lidar_config_all.robot_length,
      lidar_config_all.repulsive_gain, lidar_config_all.influence_range);

  // Zenoh Setup
  auto zenoh_config =
      zenoh::Config::from_file((get_default_path() / "zenoh.json5").string());

  auto session = zenoh::Session(std::move(zenoh_config));
  session.declare_background_subscriber(  //
      zenoh::KeyExpr("lidar/data"),       //
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
      session.declare_publisher(zenoh::KeyExpr("lidar/force_vector"));
  auto range_publisher =
      session.declare_publisher(zenoh::KeyExpr("lidar/range"));

  while (true) {
    auto now = std::chrono::system_clock::now();
    std::vector<cv::Point2d> data;

    for (auto it = timestamps.begin(); it != timestamps.end();) {
      if (now - std::get<0>(it->second) >
          std::chrono::seconds(lidar_config_all.duration_seconds)) {
        updated = true;
        it = timestamps.erase(it);
      } else {
        ++it;
      }
    }

    if (updated) {
      for (auto &[id, pair] : timestamps) {
        auto &[timestamp, lidar_data] = pair;
        auto p = lidar_data.getPoint();
        data.insert(data.end(), p.begin(), p.end());
      }

      // Vectorを出力
      nlohmann::json vec = collision_avoidance.calcRepulsiveForce(data);
      // ロボット用に回転方向を反転
      vec["angular"] = std::fmod(360.f - vec["angular"].get<float>(), 360);
      vec_publisher.put(vec.dump());

      // Rangeを出力
      nlohmann::json range_msg =
          rangeSeparater(data, 32, lidar_config_all.influence_range);

      range_publisher.put(range_msg.dump());
    }

    updated = false;
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
  return 0;
}
