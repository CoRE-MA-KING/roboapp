#include "lidar_types/lidar_metadata.hpp"

void to_json(nlohmann::json &j, const LidarMetadata &t) {
  j = nlohmann::json{{"x", t.x},
                     {"y", t.y},
                     {"min_degree", t.min_degree},
                     {"max_degree", t.max_degree},
                     {"max_distance", t.max_distance}};
}

void from_json(const nlohmann::json &j, LidarMetadata &t) {
  j.at("x").get_to(t.x);
  j.at("y").get_to(t.y);
  j.at("min_degree").get_to(t.min_degree);
  j.at("max_degree").get_to(t.max_degree);
  j.at("max_distance").get_to(t.max_distance);
}

std::vector<uint8_t> LidarMetadata::dump() {
  return nlohmann::json::to_msgpack(*this);
}

LidarMetadata::LidarMetadata(const std::vector<uint8_t> bin_data) {
  auto j = nlohmann::json::from_msgpack(bin_data);
  j.get_to(*this);
}
