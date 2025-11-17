#include <gtest/gtest.h>

#include "config.hpp"

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