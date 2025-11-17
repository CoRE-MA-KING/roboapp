cmake_minimum_required(VERSION 3.10)
project(collision_avoidance)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# デバッグビルドの設定
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")

# Google Testのダウンロードと設定
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.12.1
)
# Windows向けに共有CRTを使用
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_library(collision_avoidance
    collision_avoidance.cpp
)

target_include_directories(collision_avoidance PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

enable_testing()
add_executable(test_collision_avoidance test_collision_avoidance.cpp)
target_link_libraries(test_collision_avoidance 
    collision_avoidance 
    gtest_main
    gtest
    pthread
)
add_test(NAME collision_avoidance_test COMMAND test_collision_avoidance)

