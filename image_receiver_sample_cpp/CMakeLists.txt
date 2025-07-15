cmake_minimum_required(VERSION 3.10)

project(image_receiver_sample_cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include_directories(include)

find_package(zenohc REQUIRED)
find_package(zenohcxx REQUIRED)
find_package(OpenCV REQUIRED)

add_executable(image_receiver_sample_cpp src/main.cpp)
target_link_libraries(image_receiver_sample_cpp PRIVATE zenohcxx::zenohc ${OpenCV_LIBS})
