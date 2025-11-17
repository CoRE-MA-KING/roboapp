#include "collision_avoidance/collision_avoidance.hpp"
#include <cmath>
#include <algorithm>

CollisionAvoidance::CollisionAvoidance(
    double robot_width,
    double robot_length,
    double repulsive_gain,
    double influence_range
) : robot_width_(robot_width),
    robot_length_(robot_length),
    repulsive_gain_(repulsive_gain),
    influence_range_(influence_range)
{
    corners_ = {
        cv::Point2d(-robot_width_ / 2.0, -robot_length_ / 2.0),
        cv::Point2d( robot_width_ / 2.0, -robot_length_ / 2.0),
        cv::Point2d( robot_width_ / 2.0,  robot_length_ / 2.0),
        cv::Point2d(-robot_width_ / 2.0,  robot_length_ / 2.0)
    };
}

RepulsiveForceVector CollisionAvoidance::calcRepulsiveForce(
    const std::vector<cv::Point2d>& lidar_points
) {
    // 合成斥力
    cv::Point2d total_force{0.0, 0.0};
    // 各コーナーの斥力
    cv::Point2d corner_force[4]{{0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}};

    const double eps = 1e-6;
    for (int i = 0; i < 4; ++i) {
        const auto& corner = corners_[i];
        for (const auto& pt : lidar_points) {
            //1点分の斥力計算
            double dx = pt.x - corner.x;
            double dy = pt.y - corner.y;
            double dist = std::hypot(dx, dy);
            // 影響範囲内の点のみ処理
            // 距離と斥力の関係はガウス関数でモデル化
            // ほんとは傾きを求める必要があるが、衝突回避であれば高さでも良いと思われる
            if (dist < influence_range_ + eps) {
                double safe_dist = std::max(dist, eps);
                double sigma = influence_range_ / 2.0;
                double repulsive_force = repulsive_gain_ * std::exp(-pow(safe_dist, 2) / (2 * pow(sigma, 2)));

                if (dist <= eps) {
                    // ほぼ衝突している場合は大きな斥力
                    repulsive_force = repulsive_gain_ * 10.0;
                }
                double fx = -repulsive_force * (dx / safe_dist);
                double fy = -repulsive_force * (dy / safe_dist);

                // 斥力は外側から角の方向に向かう成分のみ加算
                // 角と角の間に柱みたいなものが引っかかるのを防ぐ
                if(corner.x > 0 && fx > 0) fx = 0;
                if(corner.x < 0 && fx < 0) fx = 0;
                if(corner.y > 0 && fy > 0) fy = 0;
                if(corner.y < 0 && fy < 0) fy = 0;
                
                corner_force[i].x += fx;
                corner_force[i].y += fy;
            }
        }
        total_force.x += corner_force[i].x;
        total_force.y += corner_force[i].y;
    }
    
    double linear = std::hypot(total_force.x, total_force.y);
    double angular = 0.0;
    if (std::abs(total_force.x) > eps || std::abs(total_force.y) > eps) {
        angular = std::atan2(total_force.y, total_force.x);
    }else if(std::abs(total_force.y) > eps) {
        angular = (total_force.y > 0) ? M_PI / 2.0 : -M_PI / 2.0;
    }else if(std::abs(total_force.x) > eps) {
        angular = (total_force.x > 0) ? 0.0 : M_PI;
    }

    return RepulsiveForceVector(linear, angular);
}
