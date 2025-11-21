#include "visualizer.hpp"

#include <cstdint>

Visualizer::Visualizer(const LiDARConfig &lidar_config, uint32_t image_size)
    : lidar_config(lidar_config), image_size(image_size) {
  // Visualization Range
  uint32_t min_x = lidar_config.robot_width / 2;
  uint32_t max_x = lidar_config.robot_width / 2;
  uint32_t min_y = lidar_config.robot_length / 2;
  uint32_t max_y = lidar_config.robot_length / 2;

  for (auto [name, d] : lidar_config.devices) {
    min_x = std::min(min_x, (d.x + d.max_distance));
    max_x = std::max(max_x, (d.x + d.max_distance));
    min_y = std::min(min_y, (d.y + d.max_distance));
    max_y = std::max(max_y, (d.y + d.max_distance));
  }

  zoom = image_size /
         (double)std::max(std::max(max_x, min_x), std::max(max_y, min_y));
}

cv::Mat Visualizer::multipleVisualize(const std::vector<cv::Point2d> &data) {
  cv::Mat img = cv::Mat::zeros(image_size, image_size, CV_8UC3);
  auto center = image_size / 2;
  cv::rectangle(img,
                cv::Point2d(center - lidar_config.robot_width / 2 * zoom,
                            center - lidar_config.robot_length / 2 * zoom),
                cv::Point2d(center + lidar_config.robot_width / 2 * zoom,
                            center + lidar_config.robot_length / 2 * zoom),
                cv::Scalar(0, 255, 0), 1);

  for (const auto p : data) {
    cv::circle(img, cv::Point2d(center + p.x * zoom, center + p.y * zoom), 2,
               cv::Scalar(255, 255, 255), -1);
  }

  return img;
}