cmake_minimum_required(VERSION 3.12)
project(rplidar_test)

find_program(SCCACHE_PROGRAM sccache)
if(SCCACHE_PROGRAM)
    set(CMAKE_CXX_COMPILER_LAUNCHER "${SCCACHE_PROGRAM}")
    set(CMAKE_C_COMPILER_LAUNCHER "${SCCACHE_PROGRAM}")
endif()

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

include_directories(include)
include_directories(include/lidar_device)

# rplidar SDK include
include_directories(3rdparty/rplidar_sdk/sdk/include)
include_directories(3rdparty/rplidar_sdk/sdk/src)
include_directories(3rdparty/rplidar_sdk/sdk/src/hal)
include_directories(3rdparty/rplidar_sdk/sdk/src/arch/linux)

# Third party libraries
add_subdirectory(3rdparty/toml11)
include_directories(3rdparty/toml11/include)
find_package(gflags REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Protobuf REQUIRED)
find_package(zenohc REQUIRED)
find_package(zenohcxx REQUIRED)

# Protobuf generated files
include_directories(src/proto)
file(GLOB_RECURSE PROTO_SRCS CONFIGURE_DEPENDS src/proto/*.pb.cc)
add_library(RoboappProtoLib ${PROTO_SRCS})
target_link_libraries(RoboappProtoLib PUBLIC protobuf::libprotobuf)

# GoolgeTest
include(FetchContent)
cmake_policy(SET CMP0135 NEW)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
FetchContent_MakeAvailable(googletest)
include(GoogleTest)

enable_testing()

#テスト用ターゲット
file(GLOB TEST_SOURCES CONFIGURE_DEPENDS test/*.cpp)
foreach(test_src ${TEST_SOURCES})
  get_filename_component(test_name ${test_src} NAME_WE)
  add_executable(${test_name} ${test_src})
  target_include_directories(${test_name} PRIVATE include)
  target_link_libraries(${test_name} ${OpenCV_LIBS} gtest gtest_main)
  if(test_name STREQUAL "test_collision_avoidance")
    target_link_libraries(${test_name} CollisionAvoidanceLib)
  endif()
  add_test(NAME ${test_name} COMMAND ${test_name})
  gtest_discover_tests(${test_name})
endforeach()

include_directories (${gflags_INCLUDE_DIR})
include_directories(${OpenCV_INCLUDE_DIRS})

# rplidar SDK sources
file(GLOB RPLIDAR_SDK_SRC CONFIGURE_DEPENDS
    3rdparty/rplidar_sdk/sdk/src/*.cpp
    3rdparty/rplidar_sdk/sdk/src/arch/linux/*.cpp
    3rdparty/rplidar_sdk/sdk/src/dataunpacker/*.cpp
    3rdparty/rplidar_sdk/sdk/src/dataunpacker/unpacker/*.cpp
    3rdparty/rplidar_sdk/sdk/src/hal/thread.cpp
)

# My Libraries
set (LIDAR_TYPES_FILES
    src/lidar_types/lidar_data.cpp
    src/lidar_types/lidar_metadata.cpp
)

add_library(LidarTypesLib ${LIDAR_TYPES_FILES})
target_include_directories(LidarTypesLib PUBLIC include/lidar_types)
target_link_libraries(LidarTypesLib nlohmann_json::nlohmann_json)

set (LIDAR_DEVICE_FILES
    src/lidar_device/rplidar_wrapper.cpp
)

add_library(LidarDeviceLib ${LIDAR_DEVICE_FILES} ${RPLIDAR_SDK_SRC})
target_include_directories(LidarDeviceLib PUBLIC include/lidar_device 3rdparty/rplidar_sdk/sdk/include)
target_link_libraries(LidarDeviceLib nlohmann_json::nlohmann_json LidarTypesLib zenohcxx::zenohc)

set (COLLISION_AVOIDANCE_FILES
    src/collision_avoidance/collision_avoidance.cpp
)

add_library(CollisionAvoidanceLib ${COLLISION_AVOIDANCE_FILES})
target_include_directories(CollisionAvoidanceLib PUBLIC include/collision_avoidance)
target_link_libraries(CollisionAvoidanceLib nlohmann_json::nlohmann_json ${OpenCV_LIBS} pthread)

set (VISUALIZER_FILES
    src/visualizer/visualizer.cpp
)

add_library(VisualizerLib ${VISUALIZER_FILES})
target_include_directories(VisualizerLib PUBLIC include/visualizer)
target_link_libraries(VisualizerLib CollisionAvoidanceLib ${OpenCV_LIBS})


add_executable(sender src/sender.cpp)
target_link_libraries(sender gflags toml11::toml11 zenohcxx::zenohc RoboappProtoLib)
target_link_libraries(sender LidarDeviceLib)

add_executable(processor src/processor.cpp )
target_link_libraries(processor gflags ${OpenCV_LIBS} pthread toml11::toml11 zenohcxx::zenohc RoboappProtoLib)
target_link_libraries(processor CollisionAvoidanceLib LidarTypesLib)

add_executable(viewer src/viewer.cpp )
target_link_libraries(viewer gflags ${OpenCV_LIBS} pthread toml11::toml11 zenohcxx::zenohc RoboappProtoLib)
target_link_libraries(viewer CollisionAvoidanceLib LidarTypesLib VisualizerLib)
