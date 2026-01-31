#ifndef NEAR_DISTANCES_HPP
#define NEAR_DISTANCES_HPP
#include <nlohmann/json.hpp>
#include <vector>

class LiDARRange {
 public:
  int min_degree;
  int max_degree;
  float distance;

  LiDARRange() = default;
  LiDARRange(int min_deg, int max_deg, float dist)
      : min_degree(min_deg), max_degree(max_deg), distance(dist) {}
};

inline void to_json(nlohmann::json& j, const LiDARRange& nr) {
  j = nlohmann::json{{"min_degree", nr.min_degree},
                     {"max_degree", nr.max_degree},
                     {"distance", nr.distance}};
}
inline void from_json(const nlohmann::json& j, LiDARRange& nr) {
  j.at("min_degree").get_to(nr.min_degree);
  j.at("max_degree").get_to(nr.max_degree);
  j.at("distance").get_to(nr.distance);
}

class LiDARRangeMessage {
 public:
  std::vector<LiDARRange> data;

  std::string dump() const {
    nlohmann::json j;
    j["data"] = data;
    return j.dump();
  }
};

inline void to_json(nlohmann::json& j, const LiDARRangeMessage& nd) {
  j = nlohmann::json{{"data", nd.data}};
}

inline void from_json(const nlohmann::json& j, LiDARRangeMessage& nd) {
  j.at("data").get_to(nd.data);
}

#endif  // NEAR_DISTANCES_HPP
