#include "zenoh.hxx"
#include <chrono>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <thread>

class ZenohReceiver {
 private:
  std::unique_ptr<zenoh::Session> session;

 public:
  cv::Mat image;
  uint64_t timestamp;

  ZenohReceiver() : image(), timestamp(0) {
    session = std::make_unique<zenoh::Session>(zenoh::Config::create_default());
    session->declare_background_subscriber(
        zenoh::KeyExpr("cam/jpg"),
        [this](const zenoh::Sample &sample) { this->callback(sample); },
        zenoh::closures::none);
  }

  void callback(const zenoh::Sample &sample) {
    cv::imdecode(sample.get_payload().as_vector(), cv::IMREAD_COLOR, &image);
    timestamp = sample.get_timestamp()->get_time();
  }
};

int main() {
  ZenohReceiver z;

  uint64_t timestamp = 0;

  while (true) {
    if (z.timestamp != timestamp) {
      timestamp = z.timestamp;
      cv::imshow("Image", z.image);
      cv::waitKey(1);
    } else {
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
  }
}