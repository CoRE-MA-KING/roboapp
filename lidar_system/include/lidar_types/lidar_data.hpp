#ifndef LIDAR_DATA_HPP_
#define LIDAR_DATA_HPP_

#include <cstdint>
#include <cstring>
#include <map>
#include <nlohmann/json.hpp>
#include <opencv2/core.hpp>
#include <string>
#include <vector>

using LiDARData = std::map<float, float>;

class LiDARDataWrapper {
 private:
 public:
  LiDARData data;
  int x;
  int y;

  LiDARDataWrapper(int x = 0, int y = 0) : x(x), y(y) {};
  LiDARDataWrapper(const LiDARData &new_data) : data(new_data) {};
  LiDARDataWrapper(const std::vector<uint8_t> bin_data);

  void insert(float degree, float value);

  void clear();
  const LiDARData get();
  const std::vector<cv::Point2d> getPoint();
  void get(LiDARData &s);
  void set(LiDARData new_data) { data = new_data; };
  std::vector<uint8_t> dump();
};

#endif  // LIDAR_DATA_HPP_