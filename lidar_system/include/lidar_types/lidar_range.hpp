#ifndef NEAR_DISTANCES_HPP
#define NEAR_DISTANCES_HPP
#include <limits>
#include <nlohmann/json.hpp>
#include <vector>

class LiDARRange {
 public:
  float left;
  float right;
  float rear_left;
  float rear_right;

  LiDARRange()
      : left(std::numeric_limits<float>::max()),
        rear_left(std::numeric_limits<float>::max()),
        rear_right(std::numeric_limits<float>::max()),
        right(std::numeric_limits<float>::max()){};
};

inline void to_json(nlohmann::json& j, const LiDARRange& nr) {
  j = nlohmann::json{{"left", nr.left},
                     {"right", nr.right},
                     {"rear_left", nr.rear_left},
                     {"rear_right", nr.rear_right}};
}

#endif  // NEAR_DISTANCES_HPP
