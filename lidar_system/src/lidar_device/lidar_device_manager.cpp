#include "lidar_device/lidar_device_manager.hpp"

#include <iostream>

#include "lidar_device/random_lidar.hpp"
#include "lidar_device/rplidar_wrapper.hpp"

LiDARDeviceManager::LiDARDeviceManager(const std::string& name,
                                       const LiDARDeviceConfig& config)
    : name(name), config(config) {
  initialize();
}

void LiDARDeviceManager::initialize() {
  if (config.backend == "rplidar") {
    std::cout << "Starting RPLIDAR: " << name << std::endl;
    lidar = std::make_unique<RplidarWrapper>(
        config.device.value(), config.max_distance, config.min_degree,
        config.max_degree, config.rotation);
  } else if (config.backend == "random") {
    std::cout << "Starting RandomLiDAR: " << name << std::endl;
    lidar =
        std::make_unique<RandomLiDAR>(config.max_distance, config.min_degree,
                                      config.max_degree, config.rotation);
  } else {
    throw std::runtime_error("Unknown backend: " + config.backend);
  }
}

bool LiDARDeviceManager::get(LiDARDataWrapper& data) {
  if (!lidar) return false;
  return lidar->get(data);
}

void LiDARDeviceManager::restart() {
  lidar.reset();
  initialize();
}
