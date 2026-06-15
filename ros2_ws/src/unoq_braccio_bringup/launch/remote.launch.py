from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    host = LaunchConfiguration("host")
    port = LaunchConfiguration("port")

    return LaunchDescription(
        [
            DeclareLaunchArgument("host", default_value="unoq.local"),
            DeclareLaunchArgument("port", default_value="8765"),
            Node(
                package="unoq_braccio_driver",
                executable="tcp_bridge",
                name="unoq_braccio_tcp_bridge",
                parameters=[{"host": host, "port": port}],
                output="screen",
            ),
        ]
    )
