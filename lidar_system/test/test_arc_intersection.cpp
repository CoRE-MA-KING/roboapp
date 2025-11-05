#include <gtest/gtest.h>

#include "arc_intersection.hpp"

TEST(ArcIntersectionTest, InvalidRange) {
  auto result = intersection_points_from_arc(0, 0, 10, 0, 200);
  EXPECT_TRUE(std::isnan(result.first.x));
  EXPECT_TRUE(std::isnan(result.first.y));
  EXPECT_TRUE(std::isnan(result.second.x));
  EXPECT_TRUE(std::isnan(result.second.y));
}

TEST(ArcIntersectionTest, Basic) {
  auto result = intersection_points_from_arc(0, 0, 10, 0, 90);
  EXPECT_NEAR(result.first.x, 14.142, 1e-3);
  EXPECT_NEAR(result.first.y, 0, 1e-3);
  EXPECT_NEAR(result.second.x, 0, 1e-3);
  EXPECT_NEAR(result.second.y, -14.142, 1e-3);
}

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
