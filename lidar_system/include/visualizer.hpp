#ifndef VISUALIZER_HPP_
#define VISUALIZER_HPP_

#include <limits>
#include <opencv2/opencv.hpp>
#include <vector>

#include "generate_color.hpp"
#include "lidar_types/lidar_data.hpp"

cv::Mat singleVisualize(const LiDARDataWrapper &data,
                        const std::string window_name, const uint32_t num = 4,
                        const uint32_t image_size = 600,
                        const float max_distance = 1000.0) {
  float angle_step = 360.0f / num;

  float max_visual_distance = image_size / 2.0f;

  std::vector<float> near;

  for (auto i = 0; i < num; ++i) {
    near.push_back(max_visual_distance);
  }

  cv::Mat img = cv::Mat::zeros(image_size, image_size, CV_8UC3);

  for (auto &[degree, distance] : data.data) {
    if (distance == 0.0f || distance > max_distance) {
      continue;
    }

    int index = static_cast<int>(degree / angle_step);

    near[index] =
        std::min(near[index], distance * (max_visual_distance) / max_distance);
  }

  for (auto i = 0; i < num; ++i) {
    if (near[i] >= (max_visual_distance)) {
      continue;
    }
    cv::ellipse(img, cv::Point2d(image_size / 2, image_size / 2),
                cv::Size(near[i], near[i]), angle_step, angle_step * (i - 1),
                angle_step * i, generate_color(i, num), 2);
  }

  return img;
}

cv::Mat multipleVisualize(const std::vector<cv::Point2d> &data,
                          const uint32_t image_size = 600) {
  cv::Mat img = cv::Mat::zeros(image_size, image_size, CV_8UC3);
  for (const auto p : data) {
    cv::circle(img, cv::Point2d(p.x + image_size / 2, p.y + image_size / 2), 2,
               cv::Scalar(255, 255, 255), -1);
  }

  return img;
}

#endif  // VISUALIZER_HPP_