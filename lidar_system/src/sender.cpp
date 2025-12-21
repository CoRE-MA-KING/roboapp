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
  auto global_config = GlobalConfig(config_file);
  auto lidar_config_all = LiDARConfig(config_file);

  auto lidar_config = lidar_config_all.devices.at(FLAGS_n);

  std::unique_ptr<MockLiDAR> lidar;

  if (lidar_config.backend == "rplidar") {
    std::cout << "RPLIDAR selected" << std::endl;
    lidar = std::make_unique<RplidarWrapper>(
        lidar_config.device.value(), lidar_config.max_distance,
        lidar_config.min_degree, lidar_config.max_degree,
        lidar_config.rotation);
  } else if (lidar_config.backend == "random") {
    std::cout << "RandomLiDAR selected" << std::endl;
    lidar = std::make_unique<RandomLiDAR>(
        lidar_config.max_distance, lidar_config.min_degree,
        lidar_config.max_degree, lidar_config.rotation);
  } else {
    std::cerr << "Unknown backend: " << lidar_config.backend << std::endl;
    return 1;
  }

  // Zenoh Setup
  auto zenoh_key = std::string("lidar/data");
  if (global_config.zenoh_prefix.has_value()) {
    zenoh_key = global_config.zenoh_prefix.value() + "/" + zenoh_key;
  }

  auto config = zenoh::Config::create_default();
  config.insert_json5(Z_CONFIG_ADD_TIMESTAMP_KEY, "true");

  auto session = zenoh::Session(std::move(config));
  auto publisher = session.declare_publisher(zenoh::KeyExpr(zenoh_key));

  auto data = LiDARDataWrapper(lidar_config.x, lidar_config.y);

  while (!ctrl_c_pressed) {
    data.clear();

    if (lidar && lidar->get(data)) {
      publisher.put(data.dump());
    }
  }
  return 0;
}