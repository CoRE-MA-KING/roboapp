#ifndef LIDAR_VECTOR_HPP
#define LIDAR_VECTOR_HPP
#include <cmath>
#include <nlohmann/json.hpp>
#include <opencv2/core.hpp>
#include <string>
struct lidar_vector {
  double linear;
  double angular;

  lidar_vector(double lin = 0.0, double ang = 0.0)
      : linear(lin), angular(ang) {}

  lidar_vector(const std::string& str) {
    auto j = nlohmann::json::parse(str);
    j.at("linear").get_to(this->linear);
    j.at("angular").get_to(this->angular);
  }

  std::string dump() const {
    nlohmann::json j;
    j["linear"] = linear;
    j["angular"] = angular;
    return j.dump();
  }
};

inline void to_json(nlohmann::json& j, const lidar_vector& rfv) {
  j = nlohmann::json{{"linear", rfv.linear}, {"angular", rfv.angular}};
}

#endif  // LIDAR_VECTOR_HPP
