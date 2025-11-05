#ifndef GENERATE_COLOR_HPP
#define GENERATE_COLOR_HPP

#include <opencv2/opencv.hpp>

cv::Scalar generate_color(int index, int num) {
  // 色相を0-180の範囲で分割
  float hue = 180.0f * index / num;  // OpenCVのHSVは0-180
  cv::Mat hsv(1, 1, CV_8UC3, cv::Scalar(hue, 255, 255));
  cv::Mat bgr;
  cv::cvtColor(hsv, bgr, cv::COLOR_HSV2BGR);
  cv::Vec3b c = bgr.at<cv::Vec3b>(0, 0);
  return cv::Scalar(c[0], c[1], c[2]);
}
#endif  // GENERATE_COLOR_HPP