#include "collision_avoidance/collision_avoidance.hpp"
#include <gtest/gtest.h>
#include <vector>
#include <cmath>
#include <opencv2/core.hpp>

// TEST(CollisionAvoidanceTest, NoObstacle)
// {
//     CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
//     std::vector<Point2D> lidar_points; // 障害物なし
//     auto result = ca.calcRepulsiveForce(lidar_points);
//     EXPECT_NEAR(result.linear, 0.0, 1e-6);
//     EXPECT_NEAR(result.angular, 0.0, 1e-6);
// }

TEST(CollisionAvoidanceTest, ObstacleFront)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // 前方に障害物
    std::vector<cv::Point2d> lidar_points = { {0.22, 0.0} };
    auto result = ca.calcRepulsiveForce(lidar_points);
    // 後方に斥力が発生する
    EXPECT_GT(result.linear, 0.0);
    // angularが[π/2, π]または[-π, -π/2]の範囲にあることを確認
    EXPECT_TRUE((90 <= result.angular && result.angular <= 180) || 
                (180 <= result.angular && result.angular <= 270));
}

TEST(CollisionAvoidanceTest, ObstacleSide)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // 側方に障害物
    std::vector<cv::Point2d> lidar_points = { {0.0, 0.22} };
    auto result = ca.calcRepulsiveForce(lidar_points);
    // 側方に斥力が発生する
    EXPECT_GT(result.linear, 0.0);
    EXPECT_TRUE(180 <= result.angular && result.angular <= 360);
}

TEST(CollisionAvoidanceTest, ObstacleDiagonalFrontRight)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // 左前方斜め45度付近に障害物
    std::vector<cv::Point2d> lidar_points = { {0.22, 0.22} };
    auto result = ca.calcRepulsiveForce(lidar_points);
    // 右後方方向に斥力が発生する
    EXPECT_GT(result.linear, 0.0);
    // 角度は右後方（3象限）になるはず：-π < angular < -π/2
    EXPECT_TRUE(180 <= result.angular && result.angular <= 270);
}

TEST(CollisionAvoidanceTest, ObstacleNearFrontRightCorner)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // 右前コーナー内部付近に障害物
    std::vector<cv::Point2d> lidar_points = { {0.15, 0.15} };
    auto result = ca.calcRepulsiveForce(lidar_points);
    // 斥力発生しない
    EXPECT_NEAR(result.linear, 0.0, 1e-6);
}

std::vector<cv::Point2d> generateRectanglePoints(double x_min, double x_max, double y_min, double y_max, double spacing = 0.05)
{
    std::vector<cv::Point2d> points;
    // 上辺
    for (double x = x_min; x <= x_max; x += spacing) {
        points.push_back({x, y_max});
    }
    // 右辺
    for (double y = y_max - spacing; y >= y_min; y -= spacing) {
        points.push_back({x_max, y});
    }
    // 下辺
    for (double x = x_max - spacing; x >= x_min; x -= spacing) {
        points.push_back({x, y_min});
    }
    // 左辺
    for (double y = y_min + spacing; y <= y_max - spacing; y += spacing) {
        points.push_back({x_min, y});
    }
    return points;
}

TEST(CollisionAvoidanceTest, RobotInsideRectangle)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // ロボットを囲む四角い点群を生成 (1.0m x 1.0mの矩形)
    auto lidar_points = generateRectanglePoints(-0.5, 0.5, -0.5, 0.5, 0.05);
    auto result = ca.calcRepulsiveForce(lidar_points);
    
    // 四方から斥力を受けるため、合成斥力はほぼゼロになるはず
    EXPECT_NEAR(result.linear, 0.0, 0.1);
}

TEST(CollisionAvoidanceTest, RobotInsideRectangleOffCenter)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // ロボットが中心からずれた位置にいる想定 (右寄り)
    auto lidar_points = generateRectanglePoints(-0.3, 0.7, -0.5, 0.5, 0.05);
    auto result = ca.calcRepulsiveForce(lidar_points);
    
    // 右側の壁が近いため、左方向の斥力が発生
    EXPECT_GT(result.linear, 0.0);
    // 角度は左方向（0付近または±π付近）
    EXPECT_TRUE((315 <= result.angular && result.angular <= 360) || 
                (0 <= result.angular && result.angular <= 45) || 
                (std::abs(result.angular) >= 3*45));
}

TEST(CollisionAvoidanceTest, RobotInsideNarrowCorridor)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // 狭い通路（幅0.6m）を想定
    auto lidar_points = generateRectanglePoints(-0.3, 0.3, -1.0, 1.0, 0.05);
    auto result = ca.calcRepulsiveForce(lidar_points);
    
    // 左右から斥力を受けるが、前後は開いているため、合成はほぼゼロ
    EXPECT_LT(result.linear, 0.3);
}

TEST(CollisionAvoidanceTest, RobotNearCornerInside)
{
    CollisionAvoidance ca(0.4, 0.4, 0.7, 0.3);
    // ロボットが矩形の角付近にいる想定
    auto lidar_points = generateRectanglePoints(-0.6, 0.42, -0.6, 0.42, 0.05);
    auto result = ca.calcRepulsiveForce(lidar_points);
    
    // 左上の角が近いため、右上方向への斥力が発生
    EXPECT_GT(result.linear, 0.0);
    // 角度は右上方向（-π < angular < -π/2）
    EXPECT_TRUE(180 <= result.angular && result.angular <= 270);
}



int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

