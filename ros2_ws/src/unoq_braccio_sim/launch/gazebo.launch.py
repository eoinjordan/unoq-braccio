import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    share = get_package_share_directory("unoq_braccio_sim")
    xacro_path = os.path.join(share, "urdf", "braccio.urdf.xacro")
    world_path = os.path.join(share, "worlds", "empty.world")
    controllers_path = os.path.join(share, "config", "controllers.yaml")
    mesh_dir = os.path.join(share, "meshes", "braccio_stedden")
    robot_description = {
        "robot_description": Command(
            [
                "xacro ",
                xacro_path,
                " controllers_file:=",
                controllers_path,
                " mesh_dir:=",
                mesh_dir,
            ]
        )
    }

    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
                    )
                ),
                launch_arguments={"gz_args": f"-r {world_path}"}.items(),
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
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name",
                    "unoq_braccio",
                    "-topic",
                    "robot_description",
                    "-x",
                    "0",
                    "-y",
                    "0",
                    "-z",
                    "0.02",
                ],
                output="screen",
            ),
            TimerAction(
                period=4.0,
                actions=[
                    Node(
                        package="controller_manager",
                        executable="spawner",
                        arguments=[
                            "joint_state_broadcaster",
                            "--controller-manager",
                            "/controller_manager",
                        ],
                        output="screen",
                    ),
                    Node(
                        package="controller_manager",
                        executable="spawner",
                        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
                        output="screen",
                    ),
                ],
            ),
        ]
    )
