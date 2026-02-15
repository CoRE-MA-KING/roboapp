#ifndef RANDOM_LIDAR_HPP
#define RANDOM_LIDAR_HPP

#include <chrono>
#include <memory>
#include <random>
#include <thread>

#include "ilidar.hpp"

class RandomLiDAR : public ILiDAR {
 private:
  std::mt19937 random_engine;
  std::uniform_int_distribution<int> random_distance;
  std::uniform_real_distribution<float> random_rate;

 public:
  inline RandomLiDAR(float max_distance = 1000.0, int32_t min_degree = 0,
                     int32_t max_degree = 360, int32_t rotation = 0)
      : ILiDAR(max_distance, min_degree, max_degree, rotation),
        random_distance(static_cast<int>(max_distance * 0.2),
                        static_cast<int>(max_distance * 1.0)),
        random_rate(0.8, 1.2) {
    std::random_device rd;
    auto seed =
        rd() ^ static_cast<unsigned int>(
                   std::chrono::system_clock::now().time_since_epoch().count());
    random_engine.seed(seed);
  };

  inline bool get(LiDARDataWrapper &data) override {
    auto base = random_distance(random_engine);

    if (min_degree <= max_degree) {
      for (int degree = min_degree; degree < max_degree; degree++) {
        int dist = base * random_rate(random_engine);
        data.insert((degree + rotation) % 360, dist);
      }
    } else {
      for (int degree = min_degree; degree < 360; degree++) {
        int dist = base * random_rate(random_engine);
        data.insert((degree + rotation) % 360, dist);
      }
      for (int degree = 0; degree < max_degree; degree++) {
        int dist = base * random_rate(random_engine);
        data.insert((degree + rotation) % 360, dist);
      }
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    return true;
  }

  inline ~RandomLiDAR(){};
};

#endif  // RANDOM_LIDAR_HPP
