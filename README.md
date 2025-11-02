# Pick and Place Robot Simulation 🤖

A complete ROS 2 simulation of a 3-DOF robotic arm with gripper performing autonomous pick and place operations in Gazebo. **Now implemented in Python for easier understanding and modification!**

## Features

- **🐍 Python Implementation**: Easy to read, modify, and extend
- **3-DOF Robotic Arm**: Base rotation + 2 arm joints with realistic joint limits
- **2-Finger Gripper**: Prismatic joints for object grasping
- **Gazebo Simulation**: Complete environment with table, objects, and target area
- **Autonomous Operation**: 10-step pick and place sequence with state machine
- **ROS 2 Control Integration**: Uses ros2_control framework with proper hardware interfaces
- **Real-time Visualization**: RViz support for robot state monitoring
- **Modular Design**: Easy to customize and extend

## Prerequisites

- **ROS 2 Humble** (or later)
- **Gazebo Classic** (comes with ROS 2)
- **Ubuntu 22.04** (recommended)

### Install Required Dependencies

```bash
# Core ROS 2 packages
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs \
                 ros-humble-joint-state-publisher-gui \
                 ros-humble-robot-state-publisher \
                 ros-humble-xacro

# ROS 2 Control packages
sudo apt install ros-humble-ros2-control \
                 ros-humble-ros2-controllers \
                 ros-humble-gazebo-ros2-control \
                 ros-humble-controller-manager

# Python ROS 2 packages
sudo apt install ros-humble-rclpy

# Additional utilities
sudo apt install ros-humble-rviz2
```

## Quick Start

### 1. Create Workspace and Build
```bash
# Create workspace
mkdir -p ~/pick_place_ws/src
cd ~/pick_place_ws/src

# Copy this package to src directory
# (assuming you have the pick_place_robot folder here)

# Build the package
cd ~/pick_place_ws
colcon build --packages-select pick_place_robot

# Source the workspace
source install/setup.bash
```

### 2. Launch Simulation
```bash
# Launch the complete simulation
ros2 launch pick_place_robot pick_place_simulation.launch.py
```

**That's it!** The robot will automatically start the pick and place sequence.

## Launch Options

### 🚀 Full Simulation (Recommended)
```bash
ros2 launch pick_place_robot pick_place_simulation.launch.py
```
**What it does:**
- Launches Gazebo with the complete environment
- Spawns the robot with physics simulation
- Loads all controllers (joint trajectory + gripper)
- Starts the autonomous pick and place sequence
- Robot automatically picks up the red box and places it in the green target area

### 🔍 Robot Visualization Only
```bash
ros2 launch pick_place_robot robot_display.launch.py
```
**What it does:**
- Opens RViz with the robot model
- Provides joint sliders for manual control
- No physics simulation (visualization only)

## System Architecture

### 🤖 Robot Design
```
Base Link (Blue Box)
    ↓ Joint1 (Z-rotation: ±180°)
Link1 (Red Cylinder)
    ↓ Joint2 (Y-rotation: ±90°)
Link2 (Green Cylinder)
    ↓ Joint3 (Y-rotation: ±90°)
Link3 (Yellow Cylinder)
    ↓ Fixed Joint
End Effector (Orange Box)
    ↓ Prismatic Joints
Gripper Fingers (Gray)
```

### 🔄 Autonomous Pick and Place Sequence
The robot executes a 10-step sequence every 3 seconds:

| Step | Action | Description |
|------|--------|-------------|
| 1 | **Home** | Move to initial position [0, 0, 0] |
| 2 | **Approach** | Move above red box [0.4, -0.3, 0.5] |
| 3 | **Lower** | Descend to picking height [0.4, -0.1, 0.3] |
| 4 | **Grasp** | Close gripper to pick object |
| 5 | **Lift** | Raise object [0.4, -0.3, 0.5] |
| 6 | **Transport** | Move to target area [-0.8, -0.3, 0.5] |
| 7 | **Lower** | Descend to place height [-0.8, -0.1, 0.3] |
| 8 | **Release** | Open gripper to drop object |
| 9 | **Retract** | Move away from placed object [-0.8, -0.3, 0.5] |
| 10 | **Return** | Go back to home position [0, 0, 0] |

### ⚙️ Control System
- **🐍 Python Controller**: Main logic implemented in Python for easy modification
- **ros2_control**: Hardware abstraction layer
- **Joint Trajectory Controller**: Smooth arm movement with position control
- **Forward Command Controller**: Direct gripper position control
- **Gazebo Integration**: Physics simulation with ros2_control plugin

## Customization

### 🐍 Modify Pick and Place Positions (Python)
Edit the sequence in `src/pick_place_controller.py`:
```python
# Example: Modify the sequence
self.sequence = [
    {'name': 'Home Position', 'joints': [0.0, 0.0, 0.0], 'gripper': False},
    {'name': 'Custom Position', 'joints': [0.5, -0.2, 0.4], 'gripper': False},
    # Add more steps...
]
```

### 🎯 Change Timing
Modify the timer interval:
```python
# In __init__ method, change from 3.0 to desired seconds
self.timer = self.create_timer(2.0, self.execute_pick_place_sequence)
```

### 📦 Add More Objects
Edit `worlds/pick_place_world.world` to add more objects to pick and place.

### 🔧 Adjust Robot Dimensions
Modify `urdf/pick_place_robot.urdf.xacro` to change link lengths, joint limits, etc.

## Troubleshooting

### ❌ Build Errors

**Problem**: `Could not find a package configuration file provided by "moveit_core"`
```bash
# Solution: MoveIt2 dependencies have been removed - rebuild
cd ~/pick_place_ws
colcon build --packages-select pick_place_robot
```

**Problem**: Missing ros2_control packages
```bash
# Solution: Install missing dependencies
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-gazebo-ros2-control
```

### ⚠️ Runtime Issues

**Problem**: Controllers not loading
```bash
# Check if controllers are loaded
ros2 control list_controllers

# Manually load if needed
ros2 control load_controller joint_trajectory_controller
ros2 control set_controller_state joint_trajectory_controller active
```

**Problem**: Robot not moving
```bash
# Check joint states
ros2 topic echo /joint_states

# Check controller status
ros2 control list_controllers
```

**Problem**: Gazebo physics issues (objects falling through table)
- Check collision geometries in URDF
- Verify physics parameters in world file
- Ensure proper mass and inertia values

### 🔧 Common Fixes
```bash
# Restart Gazebo if physics acting strange
pkill -f gazebo
ros2 launch pick_place_robot pick_place_simulation.launch.py

# Check ROS 2 environment
echo $ROS_DOMAIN_ID  # Should be same across terminals
source ~/pick_place_ws/install/setup.bash
```

## ROS 2 Interface

### 📡 Key Topics
```bash
# Joint states (published by robot)
/joint_states                                    # Current joint positions/velocities

# Control commands (published by controllers)
/joint_trajectory_controller/joint_trajectory    # Arm movement commands
/gripper_controller/commands                     # Gripper position commands

# Controller status
/joint_trajectory_controller/state              # Controller execution status
/controller_manager/robot_description           # Robot URDF
```

### 🛠️ Useful Commands
```bash
# Monitor joint positions
ros2 topic echo /joint_states

# List all active controllers
ros2 control list_controllers

# Send manual joint command
ros2 topic pub /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "..."

# Check robot description
ros2 param get /robot_state_publisher robot_description
```

## Future Enhancements

- Add vision-based object detection
- Implement MoveIt2 integration for path planning
- Add force/torque sensing for better grasping
- Multiple object types and sorting
- Collision avoidance
- Real robot hardware interface#
