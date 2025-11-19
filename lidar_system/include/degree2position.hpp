#ifndef DEGREE2POSITION_HPP
#define DEGREE2POSITION_HPP

#include <opencv2/opencv.hpp>

cv::Point2f degree2position(int x, int y, float angle, float distance) {
  float radian = angle * CV_PI / 180.0f;
  return cv::Point2d((x + distance * std::cos(radian)) * 0.001,
                     (y + distance * std::sin(radian)) * 0.001);
}

#endif  // DEGREE2POSITION_HPP