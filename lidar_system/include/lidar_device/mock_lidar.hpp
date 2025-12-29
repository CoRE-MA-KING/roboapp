#ifndef MOCK_LIDAR_HPP
#define MOCK_LIDAR_HPP

#include "lidar_types/lidar_data.hpp"

class MockLiDAR {
 public:
  MockLiDAR(float max_distance = 1000.0, int32_t min_degree = 0,
            int32_t max_degree = 360, int32_t rotation = 0)
      : max_distance(max_distance),
        min_degree(min_degree),
        max_degree(max_degree),
        rotation(rotation) {
    this->min_degree = std::max(0, std::min(this->min_degree, 360));
    this->max_degree = std::max(0, std::min(this->max_degree, 360));
  }
  virtual bool get(LiDARDataWrapper &data) = 0;
  virtual ~MockLiDAR() = default;

 protected:
  float max_distance;
  int32_t min_degree;
  int32_t max_degree;
  int32_t rotation;
};

#endif  // MOCK_LIDAR_HPP
