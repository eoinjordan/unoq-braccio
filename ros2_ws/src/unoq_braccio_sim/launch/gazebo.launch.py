import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command


def generate_launch_description():
    share = get_package_share_directory("unoq_braccio_sim")
    xacro_path = os.path.join(share, "urdf", "braccio.urdf.xacro")
    world_path = os.path.join(share, "worlds", "empty.world")
    controllers_path = os.path.join(share, "config", "controllers.yaml")
    robot_description = {
        "robot_description": Command(
            ["xacro ", xacro_path, " controllers_file:=", controllers_path]
        )
    }

    return LaunchDescription(
        [
            ExecuteProcess(
                cmd=["gazebo", "--verbose", world_path, "-s", "libgazebo_ros_factory.so"],
                output="screen",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description],
                output="screen",
            ),
            Node(
                package="unoq_braccio_driver",
                executable="joint_state_simulator",
                name="unoq_braccio_joint_state_simulator",
                output="screen",
            ),
            Node(
                package="unoq_braccio_driver",
                executable="joint_trajectory_bridge",
                name="unoq_braccio_joint_trajectory_bridge",
                output="screen",
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-topic", "robot_description", "-entity", "unoq_braccio"],
                output="screen",
            ),
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
                output="screen",
            ),
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["arm_controller", "--controller-manager", "/controller_manager"],
                output="screen",
            ),
        ]
    )
