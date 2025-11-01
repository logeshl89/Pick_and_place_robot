#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Package Directories
    pkg_pick_place_robot = FindPackageShare(package='pick_place_robot').find('pick_place_robot')
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')
    
    # Paths
    urdf_file = os.path.join(pkg_pick_place_robot, 'urdf', 'pick_place_robot.urdf.xacro')
    world_file = os.path.join(pkg_pick_place_robot, 'worlds', 'pick_place_world.world')
    controllers_file = os.path.join(pkg_pick_place_robot, 'config', 'controllers.yaml')
    
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')
    
    # Robot description
    robot_description_content = Command(['xacro ', urdf_file])
    robot_description = {'robot_description': robot_description_content}
    
    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )
    
    # Joint state publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )
    
    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                  '-entity', 'pick_place_robot',
                  '-x', '0.0',
                  '-y', '0.0',
                  '-z', '1.1'],
        output='screen'
    )
    
    # Controller manager is handled by gazebo_ros2_control plugin
    # No separate controller_manager node needed
    
    # Load controllers
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )
    
    load_joint_trajectory_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_trajectory_controller'],
        output='screen'
    )
    
    load_gripper_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'gripper_controller'],
        output='screen'
    )
    
    # Pick and place controller
    pick_place_controller = Node(
        package='pick_place_robot',
        executable='pick_place_controller',
        name='pick_place_controller',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    return LaunchDescription([
        declare_use_sim_time_cmd,
        gazebo,
        robot_state_publisher_node,
        joint_state_publisher_node,
        spawn_entity,
        load_joint_state_broadcaster,
        load_joint_trajectory_controller,
        load_gripper_controller,
        pick_place_controller
    ])