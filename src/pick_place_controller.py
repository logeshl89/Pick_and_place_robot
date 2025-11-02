#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float64MultiArray
import time

class PickPlaceController(Node):
    def __init__(self):
        super().__init__('pick_place_controller')
        
        # Publishers
        self.joint_trajectory_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        self.gripper_pub = self.create_publisher(
            Float64MultiArray,
            '/gripper_controller/commands',
            10
        )
        
        # Subscriber
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # Initialize variables
        self.joint_names = ['joint1', 'joint2', 'joint3']
        self.current_joint_positions = [0.0, 0.0, 0.0]
        self.sequence_step = 0
        self.gripper_closed = False
        
        # Timer for pick and place sequence (every 3 seconds)
        self.timer = self.create_timer(3.0, self.execute_pick_place_sequence)
        
        self.get_logger().info('Pick and Place Controller (Python) initialized')
        
        # Define the pick and place sequence
        self.sequence = [
            {'name': 'Home Position', 'joints': [0.0, 0.0, 0.0], 'gripper': False},
            {'name': 'Approach Red Box', 'joints': [0.4, -0.3, 0.5], 'gripper': False},
            {'name': 'Lower to Pick', 'joints': [0.4, -0.1, 0.3], 'gripper': False},
            {'name': 'Close Gripper', 'joints': [0.4, -0.1, 0.3], 'gripper': True},
            {'name': 'Lift Object', 'joints': [0.4, -0.3, 0.5], 'gripper': True},
            {'name': 'Move to Target', 'joints': [-0.8, -0.3, 0.5], 'gripper': True},
            {'name': 'Lower to Place', 'joints': [-0.8, -0.1, 0.3], 'gripper': True},
            {'name': 'Open Gripper', 'joints': [-0.8, -0.1, 0.3], 'gripper': False},
            {'name': 'Retract', 'joints': [-0.8, -0.3, 0.5], 'gripper': False},
            {'name': 'Return Home', 'joints': [0.0, 0.0, 0.0], 'gripper': False}
        ]
    
    def joint_state_callback(self, msg):
        """Update current joint positions from joint state feedback"""
        for i, name in enumerate(msg.name):
            if name in self.joint_names:
                joint_index = self.joint_names.index(name)
                self.current_joint_positions[joint_index] = msg.position[i]
    
    def move_to_joint_positions(self, target_positions, duration=2.0):
        """Send joint trajectory command to move robot arm"""
        trajectory_msg = JointTrajectory()
        trajectory_msg.header.stamp = self.get_clock().now().to_msg()
        trajectory_msg.joint_names = self.joint_names
        
        # Create trajectory point
        point = JointTrajectoryPoint()
        point.positions = target_positions
        point.time_from_start = Duration(seconds=duration).to_msg()
        
        trajectory_msg.points = [point]
        self.joint_trajectory_pub.publish(trajectory_msg)
        
        self.get_logger().info(
            f'Moving to joint positions: [{target_positions[0]:.2f}, '
            f'{target_positions[1]:.2f}, {target_positions[2]:.2f}]'
        )
    
    def control_gripper(self, close):
        """Control gripper open/close"""
        gripper_msg = Float64MultiArray()
        if close:
            gripper_msg.data = [0.04, 0.04]  # Close gripper
            self.get_logger().info('🤏 Closing gripper')
        else:
            gripper_msg.data = [0.0, 0.0]   # Open gripper
            self.get_logger().info('✋ Opening gripper')
        
        self.gripper_pub.publish(gripper_msg)
        self.gripper_closed = close
    
    def execute_pick_place_sequence(self):
        """Execute the pick and place sequence step by step"""
        if self.sequence_step >= len(self.sequence):
            self.sequence_step = 0  # Reset sequence
            self.get_logger().info('🔄 Pick and place sequence completed! Restarting...')
            return
        
        current_step = self.sequence[self.sequence_step]
        step_num = self.sequence_step + 1
        
        self.get_logger().info(
            f'📍 Step {step_num}/10: {current_step["name"]}'
        )
        
        # Move joints
        self.move_to_joint_positions(current_step['joints'])
        
        # Control gripper if needed
        if current_step['gripper'] != self.gripper_closed:
            self.control_gripper(current_step['gripper'])
        
        self.sequence_step += 1

def main(args=None):
    rclpy.init(args=args)
    
    try:
        controller = PickPlaceController()
        rclpy.spin(controller)
    except KeyboardInterrupt:
        print('\n🛑 Pick and Place Controller stopped by user')
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()