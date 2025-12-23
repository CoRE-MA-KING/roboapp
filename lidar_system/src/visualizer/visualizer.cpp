#include "visualizer.hpp"

#include <cstdint>

#include "collision_avoidance/collision_avoidance.hpp"

Visualizer::Visualizer(const LiDARConfig &lidar_config, uint32_t image_size)
    : lidar_config(lidar_config), image_size(image_size) {
  baseImage = cv::Mat::zeros(image_size, image_size, CV_8UC3);
  auto center = image_size / 2;

  // Visualization Range
  uint32_t min_x = lidar_config.robot_width / 2;
  uint32_t max_x = lidar_config.robot_width / 2;
  uint32_t min_y = lidar_config.robot_length / 2;
  uint32_t max_y = lidar_config.robot_length / 2;

  for (auto [name, d] : lidar_config.devices) {
    // Calculate Visualization Range
    min_x = std::min(min_x, (d.x + d.max_distance));
    max_x = std::max(max_x, (d.x + d.max_distance));
    min_y = std::min(min_y, (d.y + d.max_distance));
    max_y = std::max(max_y, (d.y + d.max_distance));
  }

  zoom = image_size /
         (double)std::max(std::max(max_x, min_x), std::max(max_y, min_y));

  // Draw Robot
  cv::rectangle(baseImage,
                cv::Point2d(center - lidar_config.robot_width / 2 * zoom,
                            center - lidar_config.robot_length / 2 * zoom),
                cv::Point2d(center + lidar_config.robot_width / 2 * zoom,
                            center + lidar_config.robot_length / 2 * zoom),
                cv::Scalar(0, 255, 0), 1);

  // Draw LiDAR Position
  for (auto [name, d] : lidar_config.devices) {
    cv::circle(baseImage, cv::Point2d(center + d.x * zoom, center + d.y * zoom),
               5, cv::Scalar(0, 0, 255), -1);
  }

  // Draw Influence Range

  cv::ellipse(baseImage,
              cv::Point2d(center + lidar_config.robot_width / 2 * zoom,
                          center + lidar_config.robot_length / 2 * zoom),
              cv::Size(lidar_config.influence_range * zoom,
                       lidar_config.influence_range * zoom),
              0, 0, 90, cv::Scalar(255, 0, 0), 1);

  cv::line(baseImage,
           cv::Point2d(center - (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom,
                       center - lidar_config.robot_length / 2 * zoom),
           cv::Point2d(center - (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom,
                       center + lidar_config.robot_length / 2 * zoom),
           cv::Scalar(255, 0, 0), 1);

  cv::ellipse(baseImage,
              cv::Point2d(center - lidar_config.robot_width / 2 * zoom,
                          center + lidar_config.robot_length / 2 * zoom),
              cv::Size(lidar_config.influence_range * zoom,
                       lidar_config.influence_range * zoom),
              0, 90, 180, cv::Scalar(255, 0, 0), 1);

  cv::line(baseImage,
           cv::Point2d(center - lidar_config.robot_length / 2 * zoom,
                       center + (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom),
           cv::Point2d(center + (lidar_config.robot_length / 2) * zoom,
                       center + (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom),
           cv::Scalar(255, 0, 0), 1);

  cv::ellipse(baseImage,
              cv::Point2d(center - lidar_config.robot_width / 2 * zoom,
                          center - lidar_config.robot_length / 2 * zoom),
              cv::Size(lidar_config.influence_range * zoom,
                       lidar_config.influence_range * zoom),
              0, 180, 270, cv::Scalar(255, 0, 0), 1);

  cv::line(baseImage,
           cv::Point2d(center - lidar_config.robot_length / 2 * zoom,
                       center - (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom),
           cv::Point2d(center + (lidar_config.robot_length / 2) * zoom,
                       center - (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom),
           cv::Scalar(255, 0, 0), 1);

  cv::ellipse(baseImage,
              cv::Point2d(center + lidar_config.robot_width / 2 * zoom,
                          center - lidar_config.robot_length / 2 * zoom),
              cv::Size(lidar_config.influence_range * zoom,
                       lidar_config.influence_range * zoom),
              0, 270, 360, cv::Scalar(255, 0, 0), 1);

  cv::line(baseImage,
           cv::Point2d(center + (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom,
                       center - lidar_config.robot_length / 2 * zoom),
           cv::Point2d(center + (lidar_config.robot_width / 2 +
                                 lidar_config.influence_range) *
                                    zoom,
                       center + lidar_config.robot_length / 2 * zoom),
           cv::Scalar(255, 0, 0), 1);

  // cv::rotate(baseImage, baseImage, cv::ROTATE_180);
}

cv::Mat Visualizer::multipleVisualize(const std::vector<cv::Point2d> &data,
                                      const RepulsiveForceVector &vec) {
  cv::Mat img = baseImage.clone();
  auto center = image_size / 2;

  for (const auto p : data) {
    cv::circle(img, cv::Point2d(center + p.x * zoom, center + p.y * zoom), 2,
               cv::Scalar(255, 255, 255), -1);
  }

  cv::arrowedLine(
      img, cv::Point2d(center, center),
      cv::Point2d(center + vec.linear * 100 * zoom *
                               std::cos(vec.angular * CV_PI / 180.0),
                  center - vec.linear * 100 * zoom *
                               std::sin(vec.angular * CV_PI / 180.0)),
      cv::Scalar(0, 255, 255), 2);

  //  cv::flip(img, img, 0);
  // cv::rotate(img, img, cv::ROTATE_180);
  return img;
}
