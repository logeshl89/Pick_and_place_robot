#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Package Directories
    pkg_pick_place_robot = FindPackageShare(package='pick_place_robot').find('pick_place_robot')
    
    # Paths
    urdf_file = os.path.join(pkg_pick_place_robot, 'urdf', 'pick_place_robot.urdf.xacro')
    rviz_config_file = os.path.join(pkg_pick_place_robot, 'config', 'robot_display.rviz')
    
    # Robot description
    robot_description_content = Command(['xacro ', urdf_file])
    robot_description = {'robot_description': robot_description_content}
    
    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )
    
    # Joint state publisher GUI
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )
    
    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else []
    )
    
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])