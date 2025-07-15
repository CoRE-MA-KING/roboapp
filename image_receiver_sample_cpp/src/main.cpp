#include "zenoh.hxx"
#include <chrono>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <thread>

void callback(const zenoh::Sample &sample) {
  std::cout << std::chrono::steady_clock::now().time_since_epoch().count()
            << "\t" << "Received sample: " << sample.get_payload().size()
            << std::endl;

  // cv::Mat image;
  // cv::imdecode(sample.get_payload().as_vector(), cv::IMREAD_COLOR, &image);
  // cv::imshow("Received Image", image);

  // auto key = cv::waitKey(1);
  // if (key == 'q') {
  //   exit(0);
  // }
}

int main() {
  auto session = zenoh::Session::open(zenoh::Config::create_default());

  session.declare_background_subscriber(zenoh::KeyExpr("cam/jpg"), &callback,
                                        zenoh::closures::none);

  while (true) {
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }

  return 0;
};