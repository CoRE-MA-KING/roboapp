#include "rplidar_wrapper.hpp"

RplidarWrapper::RplidarWrapper(std::string device, float max_distance,
                               int32_t min_degree, int32_t max_degree,
                               int32_t rotation)
    : MockLiDAR(max_distance, min_degree, max_degree, rotation) {
  auto channel_result = sl::createSerialPortChannel(device, 115200);
  if (!SL_IS_OK(channel_result)) {
    fprintf(stderr, "Failed to create serial port channel for LIDAR\r\n");
    return;
  }
  channel = std::unique_ptr<sl::IChannel>(channel_result.value);

  auto lidar_result = sl::createLidarDriver();
  if (!SL_IS_OK(lidar_result)) {
    fprintf(stderr, "Failed to create LIDAR driver\r\n");
    return;
  }
  lidar = std::unique_ptr<sl::ILidarDriver>(lidar_result.value);

  auto op_result = lidar->connect(channel.get());
  if (!SL_IS_OK(op_result)) {
    fprintf(stderr, "Failed to connect to LIDAR %08x\r\n", op_result);
    return;
  }
  lidar->setMotorSpeed();
  lidar->startScan(0, 1);
}

bool RplidarWrapper::get(LiDARDataWrapper &data) {
  sl_lidar_response_measurement_node_hq_t nodes[8192];
  size_t count = std::size(nodes);

  auto op_result = lidar->grabScanDataHq(nodes, count);

  if (!SL_IS_OK(op_result)) {
    return false;
  }
  lidar->ascendScanData(nodes, count);

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
    }
  }

  return true;
}

RplidarWrapper::~RplidarWrapper() {
  lidar->stop();
  lidar->setMotorSpeed(0);
}
