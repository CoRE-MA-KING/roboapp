#ifndef RPLIDAR_WRAPPER_HPP
#define RPLIDAR_WRAPPER_HPP

#include <cmath>
#include <limits>
#include <memory>
#include <random>

#include "mock_lidar.hpp"
#include "rplidar.h"

class RplidarWrapper : public MockLiDAR {
 private:
  std::unique_ptr<sl::IChannel> channel;
  std::unique_ptr<sl::ILidarDriver> lidar;

 public:
  RplidarWrapper(std::string device, float max_distance = 1000.0,
                 int32_t min_degree = 0, int32_t max_degree = 360,
                 int32_t rotation = 0);
  // : MockLiDAR(max_distance, min_degree, max_degree);
  bool get(LiDARDataWrapper &data);
  ~RplidarWrapper();
};

#endif  // RPLIDAR_WRAPPER_HPP
