#ifndef RANGE_SEPARATER_HPP_
#define RANGE_SEPARATER_HPP_

#include <opencv2/opencv.hpp>
#include <vector>

#include "lidar_types/lidar_range.hpp"

inline LiDARRange rangeSeparater(const std::vector<cv::Point2d> &data,
                                 const float max_distance = 5000.0) {
  LiDARRange range(max_distance, max_distance, max_distance, max_distance);

  for (const auto &point : data) {
    float distance = std::sqrt(point.x * point.x + point.y * point.y);
    float degree = std::fmod(
        (std::atan2(point.y, point.x) * 180.0f / CV_PI) + 360.0f, 360.0f);

    if (135.0f <= degree && degree < 225.0f) {
      // Left
      range.left = std::min(range.left, distance);
    } else if (225.0f <= degree && degree < 270.0f) {
      // Rear Left
      range.rear_left = std::min(range.rear_left, distance);
    } else if (270.0f <= degree && degree < 315.0f) {
      // Rear Right
      range.rear_right = std::min(range.rear_right, distance);
    } else if (315.0f <= degree || degree < 45.0f) {
      // Right
      range.right = std::min(range.right, distance);
    }
  }
  return range;
}
#endif  // RANGE_SEPARATER_HPP_
