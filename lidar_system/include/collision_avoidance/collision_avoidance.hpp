#ifndef COLLISION_AVOIDANCE_HPP
#define COLLISION_AVOIDANCE_HPP

#include <vector>
#include <cmath>
#include <array>
#include <memory>

struct Point2D {
    double x;
    double y;
    
    Point2D(double x = 0.0, double y = 0.0) : x(x), y(y) {}
};

struct RepulsiveForceVector {
    double linear;
    double angular;
    
    RepulsiveForceVector(double lin = 0.0, double ang = 0.0) : linear(lin), angular(ang) {}
};

class CollisionAvoidance {
public:
    CollisionAvoidance(
        double robot_width = 0.4,
        double robot_height = 2.0,
        double repulsive_gain = 0.7,
        double influence_range = 0.2
    );

    // LiDARからの点群を入力として受け取り、回避命令を計算
    RepulsiveForceVector calcRepulsiveForce(const std::vector<Point2D>& lidar_points);

private:
    // パラメータ
    const double robot_width_;
    const double robot_height_;
    const double repulsive_gain_;
    const double influence_range_;
    std::array<Point2D, 4> corners_;  // ロボットの4隅の位置
};


#endif // COLLISION_AVOIDANCE_HPP