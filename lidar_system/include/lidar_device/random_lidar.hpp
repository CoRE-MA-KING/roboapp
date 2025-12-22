#ifndef RANDOM_LIDAR_HPP
#define RANDOM_LIDAR_HPP

#include <memory>
#include <random>
#include <thread>

#include "mock_lidar.hpp"

class RandomLiDAR : public MockLiDAR {
 private:
  std::unique_ptr<std::mt19937> random_engine;
  std::unique_ptr<std::uniform_int_distribution<int>> random_distance;
  std::unique_ptr<std::uniform_real_distribution<float>> random_rate;
  std::unique_ptr<std::uniform_real_distribution<float>> random_skip;

 public:
  inline RandomLiDAR(float max_distance = 1000.0, int32_t min_degree = 0,
                     int32_t max_degree = 360, int32_t rotation = 0)
      : MockLiDAR(max_distance, min_degree, max_degree, rotation) {
    random_engine = std::make_unique<std::mt19937>(std::random_device{}());
    random_distance = std::make_unique<std::uniform_int_distribution<int>>(
        max_distance * 0.01, max_distance * 0.2);
    random_rate =
        std::make_unique<std::uniform_real_distribution<float>>(0.8, 1.2);
  };

  inline bool get(LiDARDataWrapper &data) override {
    auto base = (*random_distance)(*random_engine);

    if (min_degree <= max_degree) {
      for (int degree = min_degree; degree < max_degree; degree++) {
        int dist = base * (*random_rate)(*random_engine);
        data.insert((degree + rotation) % 360, dist);
      }
    } else {
      for (int degree = min_degree; degree < 360; degree++) {
        int dist = base * (*random_rate)(*random_engine);
        data.insert((degree + rotation) % 360, dist);
      }
      for (int degree = 0; degree < max_degree; degree++) {
        int dist = base * (*random_rate)(*random_engine);
        data.insert((degree + rotation) % 360, dist);
      }
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    return true;
  }

  inline ~RandomLiDAR() {};
};

#endif  // RANDOM_LIDAR_HPP