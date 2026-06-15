from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    camera_index = LaunchConfiguration("camera_index")
    label = LaunchConfiguration("label")

    return LaunchDescription(
        [
            DeclareLaunchArgument("camera_index", default_value="0"),
            DeclareLaunchArgument("label", default_value="object"),
            Node(
                package="unoq_braccio_driver",
                executable="usb_camera_node",
                name="unoq_braccio_usb_camera",
                parameters=[{"camera_index": camera_index}],
                output="screen",
            ),
            Node(
                package="unoq_braccio_driver",
                executable="color_tracker",
                name="unoq_braccio_color_tracker",
                parameters=[{"label": label}],
                output="screen",
            ),
        ]
    )
