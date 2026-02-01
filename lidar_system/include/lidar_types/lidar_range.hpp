#ifndef NEAR_DISTANCES_HPP
#define NEAR_DISTANCES_HPP
#include <nlohmann/json.hpp>
#include <vector>

class LiDARRange {
 public:
  float left;
  float right;
  float rear_left;
  float rear_right;

  LiDARRange() = default;
  LiDARRange(float left_val, float right_val, float rear_left_val,
             float rear_right_val)
      : left(left_val),
        right(right_val),
        rear_left(rear_left_val),
        rear_right(rear_right_val) {}
};

inline void to_json(nlohmann::json& j, const LiDARRange& nr) {
  j = nlohmann::json{{"left", nr.left},
                     {"right", nr.right},
                     {"rear_left", nr.rear_left},
                     {"rear_right", nr.rear_right}};
}

#endif  // NEAR_DISTANCES_HPP
