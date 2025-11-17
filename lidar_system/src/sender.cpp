#include <gflags/gflags.h>
#include <rplidar.h>
#include <signal.h>

#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <thread>

#include "config.hpp"
#include "lidar_device/random_lidar.hpp"
#include "lidar_device/rplidar_wrapper.hpp"
#include "lidar_types/lidar_data.hpp"
#include "zenoh.hxx"

DEFINE_string(
    c, "", "config file path: Default `$XDG_CONFIG_DIR/roboapp/config.toml`");
DEFINE_string(n, "", "LiDAR name in config file");

volatile sig_atomic_t ctrl_c_pressed = 0;

void ctrlc_handler(int) { ctrl_c_pressed = 1; }

int main(int argc, char* argv[]) {
  // Flag Setup
  gflags::SetUsageMessage("How To Use");
  gflags::SetVersionString("1.0.0");

  gflags::ParseCommandLineFlags(&argc, &argv, true);
  signal(SIGINT, ctrlc_handler);

  std::map<std::string, std::string> config_map;

  auto config_file = get_config_file(FLAGS_c);

  auto lidar_config = get_device_config(FLAGS_n);

  std::unique_ptr<MockLiDAR> lidar;

  if (lidar_config.at("backend").as_string() == "rplidar") {
    std::cout << "RPLIDAR selected" << std::endl;
    lidar = std::make_unique<RplidarWrapper>(
        lidar_config.at("device").as_string(),
        toml::find_or(lidar_config, "max_distance", 1000),
        toml::find_or(lidar_config, "min_degree", 0),
        toml::find_or(lidar_config, "max_degree", 360));
  } else if (lidar_config.at("backend").as_string() == "random") {
    std::cout << "RandomLiDAR selected" << std::endl;
    lidar = std::make_unique<RandomLiDAR>(
        toml::find_or(lidar_config, "max_distance", 1000),
        toml::find_or(lidar_config, "min_degree", 0),
        toml::find_or(lidar_config, "max_degree", 360));
  } else {
    std::cerr << "Unknown backend: " << lidar_config.at("backend").as_string()
              << std::endl;
    return 1;
  }

  // Zenoh Setup
  auto config = zenoh::Config::create_default();
  config.insert_json5(Z_CONFIG_ADD_TIMESTAMP_KEY, "true");

  auto session = zenoh::Session(std::move(config));
  auto publisher = session.declare_publisher(zenoh::KeyExpr("lidar/data"));

  auto data = LiDARDataWrapper(toml::find_or(lidar_config, "x", 0),
                               toml::find_or(lidar_config, "y", 0));

  while (!ctrl_c_pressed) {
    data.clear();

    if (lidar && lidar->get(data)) {
      publisher.put(data.dump());
    }
  }
  return 0;
}