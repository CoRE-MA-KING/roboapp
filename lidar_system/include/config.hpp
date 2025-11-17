#include "gflags/gflags.h"
#include "toml.hpp"

DECLARE_string(c);

class GlobalConfig {
 public:
  std::optional<std::string> zenoh_prefix = std::nullopt;
  uint16_t websocket_port = 8080;

  GlobalConfig() = default;
  GlobalConfig(toml::value toml_config) {
    if (toml_config.contains("global")) {
      auto global_config = toml_config.at("global");
      if (global_config.contains("zenoh_prefix")) {
        zenoh_prefix = toml::find<std::optional<std::string>>(global_config,
                                                              "zenoh_prefix");
      }
      if (global_config.contains("websocket_port")) {
        websocket_port =
            toml::get<uint16_t>(global_config.at("websocket_port"));
      }
    }
  }
};

struct LiDARDeviceConfig {
  std::string device_name;
  std::string frame_id;
  uint32_t max_distance = 1000;
  uint32_t min_degree = 0;
  uint32_t max_degree = 360;
};

struct LiDARConfig {
  double robot_width = 0.4;
  double robot_length = 2.0;
  double repulsive_gain = 0.7;
  double influence_range = 0.2;
  std::vector<LiDARDeviceConfig> devices;
};

toml::value get_config_file(
    std::optional<std::string> config_path = std::nullopt) {
  std::filesystem::path config_file;

  if (config_path.has_value()) {
    config_file = std::filesystem::path(config_path.value());
  } else {
    if (const char* home = std::getenv("XDG_CONFIG_HOME")) {
      config_file = std::filesystem::path(home) / "roboapp/config.toml";
    } else if (const char* home = std::getenv("HOME")) {
      config_file = std::filesystem::path(home) / ".config/roboapp/config.toml";
    } else {
      throw std::runtime_error("Cannot determine config file path");
    }
  }

  if (!std::filesystem::exists(config_file)) {
    throw std::runtime_error("Config file not found");
  }
  return toml::parse(config_file);
}

// toml::value get_lidar_config(
//     std::optional<std::string> config_path = std::nullopt) {
//   auto lidar_config = get_config_file(config_path).at("lidar");

//   auto robot_width = toml::get<double>(lidar_config, "robot_width");
//   auto robot_length = toml::get<double>(lidar_config, "robot_length");
//   auto repulsive_gain = toml::get<double>(lidar_config, "repulsive_gain");
//   auto influence_range = toml::get<double>(lidar_config,
//   "influence_range");

//   LiDARConfig config{};
// }

// toml::value get_device_config(std::string name) {
//   return get_lidar_config().at("devices").at(name);
// }

// toml::value get_params_config() { return get_lidar_config().at("params"); }
