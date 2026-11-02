#ifndef LIDAR_METADATA_HPP_
#define LIDAR_METADATA_HPP_

#include <cstdint>
#include <cstring>
#include <map>
#include <nlohmann/json.hpp>
#include <string>
#include <vector>

class LidarMetadata {
 public:
  int x;
  int y;
  int min_degree;
  int max_degree;
  int max_distance;

  LidarMetadata(const std::vector<uint8_t> bin_data);
  LidarMetadata(int x = 0, int y = 0, int min_degree = 0, int max_degree = 360,
                int max_distance = 1000)
      : x(x),
        y(y),
        min_degree(min_degree),
        max_degree(max_degree),
        max_distance(max_distance){};
  std::vector<uint8_t> dump();
};

#endif  // LIDAR_METADATA_HPP_
