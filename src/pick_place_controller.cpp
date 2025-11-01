#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <trajectory_msgs/msg/joint_trajectory_point.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <vector>
#include <chrono>

class PickPlaceController : public rclcpp::Node
{
public:
    PickPlaceController() : Node("pick_place_controller")
    {
        // Publishers
        joint_trajectory_pub_ = this->create_publisher<trajectory_msgs::msg::JointTrajectory>(
            "/pick_place_robot/joint_trajectory_controller/joint_trajectory", 10);
        
        gripper_pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/pick_place_robot/gripper_controller/commands", 10);

        // Subscriber
        joint_state_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "/pick_place_robot/joint_states", 10,
            std::bind(&PickPlaceController::joint_state_callback, this, std::placeholders::_1));

        // Initialize joint names
        joint_names_ = {"joint1", "joint2", "joint3"};
        current_joint_positions_.resize(3, 0.0);
        
        // Timer for pick and place sequence
        timer_ = this->create_wall_timer(
            std::chrono::seconds(2),
            std::bind(&PickPlaceController::execute_pick_place_sequence, this));

        RCLCPP_INFO(this->get_logger(), "Pick and Place Controller initialized");
        
        // Initialize sequence
        sequence_step_ = 0;
        gripper_closed_ = false;
    }

private:
    void joint_state_callback(const sensor_msgs::msg::JointState::SharedPtr msg)
    {
        for (size_t i = 0; i < msg->name.size(); ++i) {
            for (size_t j = 0; j < joint_names_.size(); ++j) {
                if (msg->name[i] == joint_names_[j]) {
                    current_joint_positions_[j] = msg->position[i];
                    break;
                }
            }
        }
    }

    void move_to_joint_positions(const std::vector<double>& target_positions, double duration = 3.0)
    {
        auto trajectory_msg = trajectory_msgs::msg::JointTrajectory();
        trajectory_msg.header.stamp = this->now();
        trajectory_msg.joint_names = joint_names_;

        auto point = trajectory_msgs::msg::JointTrajectoryPoint();
        point.positions = target_positions;
        point.time_from_start = rclcpp::Duration::from_seconds(duration);

        trajectory_msg.points.push_back(point);
        joint_trajectory_pub_->publish(trajectory_msg);
        
        RCLCPP_INFO(this->get_logger(), "Moving to joint positions: [%.2f, %.2f, %.2f]",
                    target_positions[0], target_positions[1], target_positions[2]);
    }

    void control_gripper(bool close)
    {
        auto gripper_msg = std_msgs::msg::Float64MultiArray();
        if (close) {
            gripper_msg.data = {0.04, 0.04}; // Close gripper
        } else {
            gripper_msg.data = {0.0, 0.0};   // Open gripper
        }
        gripper_pub_->publish(gripper_msg);
        gripper_closed_ = close;
        
        RCLCPP_INFO(this->get_logger(), "Gripper %s", close ? "closed" : "opened");
    }

    void execute_pick_place_sequence()
    {
        switch (sequence_step_) {
            case 0:
                RCLCPP_INFO(this->get_logger(), "Step 1: Moving to home position");
                move_to_joint_positions({0.0, 0.0, 0.0});
                control_gripper(false);
                break;
                
            case 1:
                RCLCPP_INFO(this->get_logger(), "Step 2: Moving to pick position (red box)");
                // Position above red box at (0.5, 0.2, 1.05)
                move_to_joint_positions({0.4, -0.3, 0.5});
                break;
                
            case 2:
                RCLCPP_INFO(this->get_logger(), "Step 3: Lowering to pick");
                move_to_joint_positions({0.4, -0.1, 0.3});
                break;
                
            case 3:
                RCLCPP_INFO(this->get_logger(), "Step 4: Closing gripper");
                control_gripper(true);
                break;
                
            case 4:
                RCLCPP_INFO(this->get_logger(), "Step 5: Lifting object");
                move_to_joint_positions({0.4, -0.3, 0.5});
                break;
                
            case 5:
                RCLCPP_INFO(this->get_logger(), "Step 6: Moving to place position");
                // Position above target area at (-0.5, 0, 1.025)
                move_to_joint_positions({-0.8, -0.3, 0.5});
                break;
                
            case 6:
                RCLCPP_INFO(this->get_logger(), "Step 7: Lowering to place");
                move_to_joint_positions({-0.8, -0.1, 0.3});
                break;
                
            case 7:
                RCLCPP_INFO(this->get_logger(), "Step 8: Opening gripper");
                control_gripper(false);
                break;
                
            case 8:
                RCLCPP_INFO(this->get_logger(), "Step 9: Retracting");
                move_to_joint_positions({-0.8, -0.3, 0.5});
                break;
                
            case 9:
                RCLCPP_INFO(this->get_logger(), "Step 10: Returning to home");
                move_to_joint_positions({0.0, 0.0, 0.0});
                break;
                
            case 10:
                RCLCPP_INFO(this->get_logger(), "Pick and place sequence completed!");
                // Reset sequence to repeat
                sequence_step_ = -1;
                break;
        }
        
        sequence_step_++;
    }

    // Member variables
    rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr joint_trajectory_pub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr gripper_pub_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    std::vector<std::string> joint_names_;
    std::vector<double> current_joint_positions_;
    int sequence_step_;
    bool gripper_closed_;
};

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<PickPlaceController>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}