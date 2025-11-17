#include <gtest/gtest.h>

#include "config.hpp"

// Global Config
TEST(ConfigTest, LoadEmptyConfigFile) {
  auto root = get_config_file("../test/resources/global_config_empty.toml");
  auto config = GlobalConfig(root);

  EXPECT_EQ(config.zenoh_prefix, std::nullopt);
  EXPECT_EQ(config.websocket_port, 8080);
}

TEST(ConfigTest, LoadWebsocketPortFromToml) {
  auto root =
      get_config_file("../test/resources/global_config_websocket_port.toml");
  auto config = GlobalConfig(root);

  EXPECT_EQ(config.zenoh_prefix, std::nullopt);
  EXPECT_EQ(config.websocket_port, 9090);
}

TEST(ConfigTest, LoadZenohPrefixFromToml) {
  auto root =
      get_config_file("../test/resources/global_config_zenoh_prefix.toml");
  auto config = GlobalConfig(root);

  EXPECT_EQ(config.zenoh_prefix, std::optional<std::string>("roboapp"));
  EXPECT_EQ(config.websocket_port, 8080);
}

// LiDAR Config
// Parameter

TEST(LiDARConfigTest, DefaultValues) {
  auto root = get_config_file("../test/resources/lidar_config_default.toml");
  auto config = LiDARConfig(root);
  EXPECT_DOUBLE_EQ(config.robot_width, 0.4);
  EXPECT_DOUBLE_EQ(config.robot_length, 2.0);
  EXPECT_DOUBLE_EQ(config.repulsive_gain, 0.7);
  EXPECT_DOUBLE_EQ(config.influence_range, 0.2);
}

TEST(LiDARConfigTest, LoadRobotWidthFromToml) {
  auto root =
      get_config_file("../test/resources/lidar_config_robot_width.toml");
  auto config = LiDARConfig(root);
  EXPECT_DOUBLE_EQ(config.robot_width, 1.2);
  EXPECT_DOUBLE_EQ(config.robot_length, 2.0);
  EXPECT_DOUBLE_EQ(config.repulsive_gain, 0.7);
  EXPECT_DOUBLE_EQ(config.influence_range, 0.2);
}

TEST(LiDARConfigTest, LoadRobotLengthFromToml) {
  auto root =
      get_config_file("../test/resources/lidar_config_robot_length.toml");
  auto config = LiDARConfig(root);
  EXPECT_DOUBLE_EQ(config.robot_width, 0.4);
  EXPECT_DOUBLE_EQ(config.robot_length, 1.2);
  EXPECT_DOUBLE_EQ(config.repulsive_gain, 0.7);
  EXPECT_DOUBLE_EQ(config.influence_range, 0.2);
}

TEST(LiDARConfigTest, LoadRepulsiveGainFromToml) {
  auto root =
      get_config_file("../test/resources/lidar_config_repulsive_gain.toml");
  auto config = LiDARConfig(root);
  EXPECT_DOUBLE_EQ(config.robot_width, 0.4);
  EXPECT_DOUBLE_EQ(config.robot_length, 2.0);
  EXPECT_DOUBLE_EQ(config.influence_range, 0.2);
  EXPECT_DOUBLE_EQ(config.repulsive_gain, 1.2);
}

TEST(LiDARConfigTest, LoadInfluenceRangeFromToml) {
  auto root =
      get_config_file("../test/resources/lidar_config_influence_range.toml");
  auto config = LiDARConfig(root);
  EXPECT_DOUBLE_EQ(config.robot_width, 0.4);
  EXPECT_DOUBLE_EQ(config.robot_length, 2.0);
  EXPECT_DOUBLE_EQ(config.influence_range, 1.2);
  EXPECT_DOUBLE_EQ(config.repulsive_gain, 0.7);
}
