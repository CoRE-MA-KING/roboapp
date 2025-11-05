#ifndef MOCK_LIDAR_HPP
#define MOCK_LIDAR_HPP

#include "lidar_types/lidar_data.hpp"

class MockLiDAR {
 public:
  MockLiDAR(float max_distance = 1000.0, int min_degree = 0,
            int max_degree = 360)
      : max_distance(max_distance),
        min_degree(min_degree),
        max_degree(max_degree) {
    this->min_degree = std::max(0, std::min(this->min_degree, 360));
    this->max_degree = std::max(0, std::min(this->max_degree, 360));
  }
  virtual bool get(LiDARDataWrapper &data) = 0;
  virtual ~MockLiDAR() = default;

 protected:
  float max_distance;
  int min_degree;
  int max_degree;
};

#endif  // MOCK_LIDAR_HPP