#include "lidar_types/lidar_data.hpp"

#include <iostream>
void to_json(nlohmann::json &j, const LiDARDataWrapper &p) {
  j = nlohmann::json{
      {"data", p.data},
      {"x", p.x},
      {"y", p.y},
  };
}

void from_json(const nlohmann::json &j, LiDARDataWrapper &p) {
  j.at("data").get_to(p.data);
  j.at("x").get_to(p.x);
  j.at("y").get_to(p.y);
}

LiDARDataWrapper::LiDARDataWrapper(const std::vector<uint8_t> bin_data) {
  auto j = nlohmann::json::from_msgpack(bin_data);
  j.get_to(*this);
}

void LiDARDataWrapper::insert(float degree, float value) {  //
  data[degree] = value;
}

void LiDARDataWrapper::clear() {  //
  data.clear();
}

const LiDARData LiDARDataWrapper::get() {  //
  return data;
}

void LiDARDataWrapper::get(LiDARData &s) { s = data; }

std::vector<uint8_t> LiDARDataWrapper::dump() {
  return nlohmann::json::to_msgpack(*this);
}

const std::vector<cv::Point2d> LiDARDataWrapper::getPoint() {
  std::vector<cv::Point2d> points;
  for (const auto &item : data) {
    float distance = item.second;
    float radian = item.first * CV_PI / 180.0f;
    points.push_back(cv::Point2d((x + distance * std::cos(radian)),
                                 (y + distance * std::sin(radian))));
  }
  return points;
}
