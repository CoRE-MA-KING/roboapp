#ifndef COLLISION_AVOIDANCE_HPP
#define COLLISION_AVOIDANCE_HPP

#include <array>
#include <cmath>
#include <nlohmann/json.hpp>
#include <opencv2/core.hpp>
#include <vector>
struct RepulsiveForceVector {
  double linear;
  double angular;

  RepulsiveForceVector(double lin = 0.0, double ang = 0.0)
      : linear(lin), angular(ang) {}

  RepulsiveForceVector(const std::string& str) {
    auto j = nlohmann::json(str);
    j.at("linear").get_to(this->linear);
    j.at("angular").get_to(this->angular);
  }
};

class CollisionAvoidance {
 public:
  CollisionAvoidance(double robot_width = 0.4, double robot_length = 2.0,
                     double repulsive_gain = 0.7, double influence_range = 0.2);

  // LiDARからの点群を入力として受け取り、回避命令を計算
  RepulsiveForceVector calcRepulsiveForce(
      const std::vector<cv::Point2d>& lidar_points);

 private:
  // パラメータ
  const double robot_width_;
  const double robot_length_;
  const double repulsive_gain_;
  const double influence_range_;
  std::array<cv::Point2d, 4> corners_;  // ロボットの4隅の位置
};

#endif  // COLLISION_AVOIDANCE_HPP
