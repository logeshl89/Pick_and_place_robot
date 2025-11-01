cmake_minimum_required(VERSION 3.8)
project(pick_place_robot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(control_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)

# Add executable
add_executable(pick_place_controller src/pick_place_controller.cpp)
ament_target_dependencies(pick_place_controller
  rclcpp
  std_msgs
  geometry_msgs
  sensor_msgs
  trajectory_msgs
  control_msgs
  tf2
  tf2_ros
)

# Install targets
install(TARGETS
  pick_place_controller
  DESTINATION lib/${PROJECT_NAME}
)

# Install directories
install(DIRECTORY
  launch
  urdf
  worlds
  config
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()