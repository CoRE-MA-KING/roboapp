#include "gflags/gflags.h"
#include "toml.hpp"

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

class LiDARDeviceConfig {
 public:
  std::string backend;
  std::optional<std::string> device = std::nullopt;
  uint32_t max_distance = 1000;
  uint32_t min_degree = 0;
  uint32_t max_degree = 360;
  int32_t x = 0;
  int32_t y = 0;

  LiDARDeviceConfig(toml::value toml_config) {
    if (toml_config.contains("backend")) {
      backend = toml::get<std::string>(toml_config.at("backend"));
      if (backend != "rplidar" && backend != "dummy") {
        throw std::runtime_error("Unsupported LiDAR backend: " + backend);
      }
    } else {
      throw std::runtime_error("LiDAR device config must contain 'backend'");
    }

    if (toml_config.contains("device")) {
      device = toml::get<std::string>(toml_config.at("device"));
    } else {
      if (backend == "rplidar") {
        throw std::runtime_error(
            "LiDAR device config with 'rplidar' backend must contain 'device'");
      }
    }
    if (toml_config.contains("max_distance")) {
      max_distance = toml::get<uint32_t>(toml_config.at("max_distance"));
    }
    if (toml_config.contains("min_degree")) {
      min_degree = toml::get<uint32_t>(toml_config.at("min_degree"));
    };
    if (toml_config.contains("max_degree")) {
      max_degree = toml::get<uint32_t>(toml_config.at("max_degree"));
    };
    if (toml_config.contains("x")) {
      x = toml::get<int32_t>(toml_config.at("x"));
    }
    if (toml_config.contains("y")) {
      y = toml::get<int32_t>(toml_config.at("y"));
    }
  };
};

class LiDARConfig {
 public:
  double robot_width = 0.4;
  double robot_length = 2.0;
  double repulsive_gain = 0.7;
  double influence_range = 0.2;
  std::map<std::string, LiDARDeviceConfig> devices;

  LiDARConfig(toml::value toml_config) {
    if (toml_config.contains("lidar")) {
      auto lidar_config = toml_config.at("lidar");
      if (lidar_config.contains("robot_width")) {
        robot_width = toml::get<double>(lidar_config.at("robot_width"));
      }
      if (lidar_config.contains("robot_length")) {
        robot_length = toml::get<double>(lidar_config.at("robot_length"));
      }
      if (lidar_config.contains("repulsive_gain")) {
        repulsive_gain = toml::get<double>(lidar_config.at("repulsive_gain"));
      }
      if (lidar_config.contains("influence_range")) {
        influence_range = toml::get<double>(lidar_config.at("influence_range"));
      }

      for (const auto& [device_name, device_config] :
           toml::find<toml::table>(lidar_config, "devices")) {
        devices.emplace(device_name, LiDARDeviceConfig(device_config));
      }
    } else {
      throw std::runtime_error("LiDAR config must contain 'lidar' section");
    }
  };
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
