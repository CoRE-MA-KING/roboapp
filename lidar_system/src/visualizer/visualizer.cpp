#include "visualizer.hpp"
#include <cstdint>

Visualizer::Visualizer(const LiDARConfig &lidar_config, uint32_t image_size)
    : lidar_config(lidar_config), image_size(image_size) {

// Visualization Range
  uint32_t min_x = -lidar_config.robot_width /2;
  uint32_t max_x = lidar_config.robot_width /2;
  uint32_t min_y = -lidar_config.robot_length /2;
  uint32_t max_y = lidar_config.robot_length /2;

  for ( auto [name, d] : lidar_config.devices) {
    min_x = std::min(min_x, d.x - d.max_distance);
    max_x = std::max(max_x, d.x + d.max_distance);
    min_y = std::min(min_y, d.y - d.max_distance);
    max_y = std::max(max_y, d.y + d.max_distance);
  }

  require_length = std::max(max_x - min_x, max_y - min_y);

}
