#ifndef LIDAR_DEVICE_MANAGER_HPP
#define LIDAR_DEVICE_MANAGER_HPP

#include <memory>
#include <string>

#include "config.hpp"
#include "lidar_device/mock_lidar.hpp"
#include "lidar_types/lidar_data.hpp"

class LiDARDeviceManager {
 public:
  LiDARDeviceManager(const std::string& name, const LiDARDeviceConfig& config);
  bool get(LiDARDataWrapper& data);
  const std::string& getName() const { return name; }
  void restart();

 private:
  std::string name;
  LiDARDeviceConfig config;
  std::unique_ptr<MockLiDAR> lidar;
  void initialize();
};

#endif  // LIDAR_DEVICE_MANAGER_HPP
