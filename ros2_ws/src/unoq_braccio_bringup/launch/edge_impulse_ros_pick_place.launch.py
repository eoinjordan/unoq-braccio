"""
Pick-and-place using edgeimpulse_ros for inference (optional backend).

This is an alternative to ``edge_impulse_pick_place.launch.py``. Instead of the
repo's ``edge_impulse_vision`` runner-command node, it runs the ``edgeimpulse_ros``
detector on the camera image topic and bridges its ``vision_msgs`` output to the
``/edge_impulse/label`` topic the executor already consumes.

Requires ``edgeimpulse_ros`` to be present in the same ROS 2 workspace.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    stream_url = LaunchConfiguration("stream_url")
    model_path = LaunchConfiguration("model_path")
    image_topic = LaunchConfiguration("image_topic")
    image_qos = LaunchConfiguration("image_qos")
    confidence_threshold = LaunchConfiguration("confidence_threshold")
    publish_debug_image = LaunchConfiguration("publish_debug_image")
    detections_topic = LaunchConfiguration("detections_topic")
    min_confidence = LaunchConfiguration("min_confidence")
    workflow_file = LaunchConfiguration("workflow_file")

    return LaunchDescription(
        [
            DeclareLaunchArgument("stream_url", default_value="http://unoq.local:8080/stream"),
            DeclareLaunchArgument(
                "model_path",
                default_value="",
                description="Path to the Edge Impulse .eim model (required)",
            ),
            DeclareLaunchArgument("image_topic", default_value="/braccio/camera/image_raw"),
            DeclareLaunchArgument("image_qos", default_value="sensor_data"),
            DeclareLaunchArgument(
                "confidence_threshold",
                default_value="-1.0",
                description="edgeimpulse_ros publish threshold; <0 uses the model default",
            ),
            DeclareLaunchArgument("publish_debug_image", default_value="false"),
            DeclareLaunchArgument(
                "detections_topic",
                default_value="/edgeimpulse_detector/detections",
            ),
            DeclareLaunchArgument(
                "min_confidence",
                default_value="0.65",
                description="Minimum score for the bridge to publish a label",
            ),
            DeclareLaunchArgument(
                "workflow_file",
                default_value="edge_impulse/pick_place_workflows.yaml",
            ),
            Node(
                package="unoq_braccio_driver",
                executable="mjpeg_camera_node",
                name="unoq_braccio_mjpeg_camera",
                parameters=[{"stream_url": stream_url}],
                output="screen",
            ),
            Node(
                package="edgeimpulse_ros",
                executable="edgeimpulse_detector",
                name="edgeimpulse_detector",
                parameters=[
                    {
                        "model_path": model_path,
                        "image_topic": image_topic,
                        "image_transport": "raw",
                        "image_qos": image_qos,
                        "confidence_threshold": confidence_threshold,
                        "publish_debug_image": publish_debug_image,
                    }
                ],
                output="screen",
            ),
            Node(
                package="unoq_braccio_driver",
                executable="detection_label_bridge",
                name="unoq_braccio_detection_label_bridge",
                parameters=[
                    {
                        "detections_topic": detections_topic,
                        "min_confidence": min_confidence,
                    }
                ],
                output="screen",
            ),
            Node(
                package="unoq_braccio_driver",
                executable="pick_place_executor",
                name="unoq_braccio_pick_place_executor",
                parameters=[{"workflow_file": workflow_file}],
                output="screen",
            ),
        ]
    )
