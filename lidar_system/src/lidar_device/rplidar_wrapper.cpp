#include "rplidar_wrapper.hpp"

#include <cmath>
#include <cstdio>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <thread>

RplidarWrapper::RplidarWrapper(std::string device, float max_distance,
                               int32_t min_degree, int32_t max_degree,
                               int32_t rotation)
    : ILiDAR(max_distance, min_degree, max_degree, rotation) {
  if (!std::filesystem::exists(device)) {
    throw std::runtime_error("Device file does not exist: " + device);
  }

  auto channel_result = sl::createSerialPortChannel(device, 115200);
  if (!channel_result.value) {
    throw std::runtime_error("Failed to create serial port channel");
  }
  channel = std::unique_ptr<sl::IChannel>(channel_result.value);

  auto lidar_result = sl::createLidarDriver();
  if (!lidar_result.value) {
    channel.reset();
    throw std::runtime_error("Failed to create LIDAR driver");
  }
  lidar = std::unique_ptr<sl::ILidarDriver>(lidar_result.value);

  auto op_result = lidar->connect(channel.get());

  if (!SL_IS_OK(op_result)) {
    std::cerr << "Failed to connect to LIDAR " << std::hex << op_result
              << std::dec << std::endl;
    lidar.reset();
    channel.reset();
    throw std::runtime_error("Failed to connect to LIDAR");
  }

  // Reset device on startup
  lidar->reset();
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  lidar->setMotorSpeed();
  op_result = lidar->startScan(0, 1);

  if (!SL_IS_OK(op_result)) {
    std::cerr << "Failed to start scan: " << std::hex << op_result << std::dec
              << std::endl;
    channel.reset();
    throw std::runtime_error("Failed to start scan");
  }
}

bool RplidarWrapper::get(LiDARDataWrapper &data) {
  if (!lidar) {
    return false;
  }
  sl_lidar_response_measurement_node_hq_t nodes[8192];
  size_t count = std::size(nodes);

  // Set timeout to 500ms to detect disconnection faster
  auto op_result = lidar->grabScanDataHq(nodes, count, 500);

  if (!SL_IS_OK(op_result)) {
    return false;
  }
  lidar->ascendScanData(nodes, count);
  int valid_points = 0;
  for (int pos = 0; pos < (int)count; ++pos) {
    if (nodes[pos].quality >> SL_LIDAR_RESP_MEASUREMENT_QUALITY_SHIFT != 47) {
      continue;
    }
    float degree = (nodes[pos].angle_z_q14 * 90.f) / 16384.f;

    if (((min_degree <= max_degree) &&
         (min_degree <= degree && degree < max_degree)) ||
        (min_degree > max_degree &&
         ((min_degree <= degree) || (degree < max_degree)))) {
      float dist = std::min(max_distance, nodes[pos].dist_mm_q2 / 4.0f);

      data.insert(std::fmod(degree + rotation, 360.0f), dist);
      valid_points++;
    }
  }
  // printf("Raw: %zu, Valid: %d\n", count, valid_points);

  return true;
}
RplidarWrapper::~RplidarWrapper() {
  if (lidar) {
    lidar->stop();
    lidar->setMotorSpeed(0);
    lidar->disconnect();
  }
  lidar.reset();
  channel.reset();
}
