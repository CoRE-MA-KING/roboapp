#ifndef RANGE_SEPARATER_HPP_
#define RANGE_SEPARATER_HPP_

#include <opencv2/opencv.hpp>
#include <vector>

#include "lidar_types/near_distances.hpp"

inline NearDistances rangeSeparater(const std::vector<cv::Point2d> &data,
                                    const uint32_t num = 4,
                                    const float max_distance = 5000.0) {
  float angle_step = 360.0f / num;

  NearDistances near;

  for (auto i = 0; i < num; ++i) {
    near.data.push_back(
        NearRange(i * angle_step, (i + 1) * angle_step, max_distance));
  }

  for (const auto &point : data) {
    float distance = std::sqrt(point.x * point.x + point.y * point.y);
    float degree = std::fmod(
        (std::atan2(point.y, point.x) * 180.0f / CV_PI) + 360.0f, 360.0f);
    int index = static_cast<int>(degree / angle_step);

    if (distance == 0.0f || distance > near.data[index].distance) {
      continue;
    } else {
      near.data[index].distance = distance;
    }
  }
  return near;
}

#endif  // RANGE_SEPARATER_HPP_
