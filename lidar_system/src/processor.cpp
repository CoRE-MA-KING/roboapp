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
#include "proto/roboapp/lidar_range.pb.h"
#include "proto/roboapp/lidar_vector.pb.h"
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
  auto lidar_config_all = LiDARConfig(config_file);

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
  session.declare_background_subscriber(  //
      zenoh::KeyExpr("lidar/data"),       //
      [&timestamps, &updated, &mtx](const zenoh::Sample &sample) {
        try {
          auto timestamp =
              ntp64_to_timepoint(sample.get_timestamp()->get_time());

          auto data = sample.get_payload().as_vector();
          auto z = LiDARDataWrapper(data);

          std::lock_guard<std::mutex> lock(mtx);
          timestamps[z.name] = {
              timestamp,
              z,
          };

          updated = true;
        } catch (const std::exception &e) {
          std::cerr << "Error processing lidar data: " << e.what() << std::endl;
        }
      },
      zenoh::closures::none);

  auto vec_publisher =
      session.declare_publisher(zenoh::KeyExpr("lidar/force_vector"));
  auto range_publisher =
      session.declare_publisher(zenoh::KeyExpr("lidar/range"));

  while (true) {
    auto now = std::chrono::system_clock::now();
    std::vector<cv::Point2d> data;
    bool current_updated = false;

    {
      std::lock_guard<std::mutex> lock(mtx);
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
        for (auto &[id, pair] : timestamps) {
          auto &[timestamp, lidar_data] = pair;
          auto p = lidar_data.getPoint();
          data.insert(data.end(), p.begin(), p.end());
        }
        updated = false;
      }
    }

    if (current_updated) {
      // Vectorを出力
      auto [lin, ang] = collision_avoidance.calcRepulsiveForce(data);
      roboapp::LiDARVector vec_msg;
      vec_msg.set_linear(lin);
      vec_msg.set_angular(std::fmod(360.f - ang, 360));
      vec_publisher.put(vec_msg.SerializeAsString());

      // Rangeを出力
      auto range_data = rangeSeparater(data);
      roboapp::LiDARRange range_pb;
      range_pb.set_left(range_data.left);
      range_pb.set_right(range_data.right);
      range_pb.set_rear_left(range_data.rear_left);
      range_pb.set_rear_right(range_data.rear_right);

      range_publisher.put(range_pb.SerializeAsString());
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
  return 0;
}
