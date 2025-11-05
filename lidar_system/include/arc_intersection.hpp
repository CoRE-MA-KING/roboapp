#ifndef ARC_INTERSECTION_HPP
#define ARC_INTERSECTION_HPP

#include <cmath>
#include <opencv2/opencv.hpp>

// 中心(x, y), 半径r, 角度範囲[angle_min, angle_max]（度）
// 交点は2つ返す: (交点1, 交点2)
std::pair<cv::Point2f, cv::Point2f> intersection_points_from_arc(
    float x, float y, float r, float angle_min, float angle_max) {
  if (angle_min > angle_max) {
    std::swap(angle_min, angle_max);
  }

  if (angle_max - angle_min >= 180) {
    // 角度範囲が180度以上の場合、交点は無限に存在するため、特別な処理を行う
    return std::make_pair(cv::Point2f(NAN, NAN), cv::Point2f(NAN, NAN));
  }

  // 角度範囲の中心
  float angle_center = (angle_min + angle_max) / 2.0f;
  float rad_center = angle_center * CV_PI / 180.0f;

  // 円周上の中心角の点
  cv::Point2f center_on_circle(x + r * cos(rad_center),
                               y + r * sin(rad_center));

  // 垂線の角度（中心角+90度）
  float perp_angle1 = angle_center + 90.0f;
  float perp_angle2 = angle_center - 90.0f;
  float rad_perp1 = perp_angle1 * CV_PI / 180.0f;
  float rad_perp2 = perp_angle2 * CV_PI / 180.0f;

  // 上限・下限角の円周上の点
  float rad_min = angle_min * CV_PI / 180.0f;
  float rad_max = angle_max * CV_PI / 180.0f;
  cv::Point2f p_min(x + r * cos(rad_min), y + r * sin(rad_min));
  cv::Point2f p_max(x + r * cos(rad_max), y + r * sin(rad_max));

  // 直線: 中心→p_min, 中心→p_max
  // 垂線: center_on_circle, 方向ベクトル (cos(rad_perp1), sin(rad_perp1))

  // 交点計算（直線同士の交点）
  auto intersect = [](cv::Point2f p1, cv::Point2f d1, cv::Point2f p2,
                      cv::Point2f d2) {
    // p1 + t1*d1 = p2 + t2*d2
    float a = d1.x, b = -d2.x, c = d1.y, d = -d2.y;
    float det = a * d - b * c;
    if (std::abs(det) < 1e-6) return cv::Point2f(NAN, NAN);  // 平行
    float dx = p2.x - p1.x, dy = p2.y - p1.y;
    float t1 = (dx * d - b * dy) / det;
    return cv::Point2f(p1.x + t1 * d1.x, p1.y + t1 * d1.y);
  };

  // 方向ベクトル
  cv::Point2f dir_perp1(cos(rad_perp1), sin(rad_perp1));
  cv::Point2f dir_perp2(cos(rad_perp2), sin(rad_perp2));
  cv::Point2f dir_min(p_min.x - x, p_min.y - y);
  cv::Point2f dir_max(p_max.x - x, p_max.y - y);

  // 交点
  cv::Point2f cross1 =
      intersect(center_on_circle, dir_perp1, cv::Point2f(x, y), dir_min);
  cv::Point2f cross2 =
      intersect(center_on_circle, dir_perp1, cv::Point2f(x, y), dir_max);

  return std::make_pair(cross1, cross2);
}

#endif  // ARC_INTERSECTION_HPP
