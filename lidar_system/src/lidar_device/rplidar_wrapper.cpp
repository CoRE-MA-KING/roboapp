#include "rplidar_wrapper.hpp"

RplidarWrapper::RplidarWrapper(std::string device, float max_distance,
                               int min_degree, int max_degree)
    : MockLiDAR(max_distance, min_degree, max_degree) {
  auto channel_result = sl::createSerialPortChannel(device, 115200);
  channel = std::unique_ptr<sl::IChannel>(channel_result.value);
  lidar = std::unique_ptr<sl::ILidarDriver>(sl::createLidarDriver().value);

  auto op_result = lidar->connect(channel.get());

  if (!SL_IS_OK(op_result)) {
    fprintf(stderr, "Failed to connect to LIDAR %08x\r\n", op_result);
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

      data.insert(degree, dist);
    }
  }

  return true;
}

RplidarWrapper::~RplidarWrapper() {
  lidar->stop();
  lidar->setMotorSpeed(0);
}
