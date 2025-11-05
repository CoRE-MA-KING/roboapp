#include <toml.hpp>

#include "gflags/gflags.h"

DECLARE_string(c);

toml::value get_lidar_config() {
  std::filesystem::path environment_file = std::filesystem::path(FLAGS_c);

  if (environment_file.empty()) {
    if (const char* home = std::getenv("XDG_CONFIG_HOME")) {
      environment_file = std::filesystem::path(home) / "roboapp/config.toml";
    } else if (const char* home = std::getenv("HOME")) {
      environment_file =
          std::filesystem::path(home) / ".config/roboapp/config.toml";
    } else {
      throw std::runtime_error("Cannot determine config file path");
    }
  }

  if (!std::filesystem::exists(environment_file)) {
    throw std::runtime_error("Config file not found");
  }
  return toml::parse(environment_file).at("lidar");
}

toml::value get_device_config(std::string name) {
  return get_lidar_config().at("devices").at(name);
}

toml::value get_params_config() { return get_lidar_config().at("params"); }