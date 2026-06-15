import math

import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from unoq_braccio_driver.braccio_model import JOINT_NAMES, POSES


def servo_degrees_to_controller_position(name: str, value: float) -> float:
    if name == "gripper":
        return 0.1750 + max(0.0, min(1.0, (float(value) - 10.0) / 100.0)) * (1.2741 - 0.1750)
    return math.radians(float(value) - 90.0)


class JointTrajectoryBridge(Node):
    def __init__(self) -> None:
        super().__init__("unoq_braccio_joint_trajectory_bridge")
        self.last_command = None
        self.publisher = self.create_publisher(
            JointTrajectory,
            "/arm_controller/joint_trajectory",
            10,
        )
        self.subscription = self.create_subscription(
            JointState,
            "/braccio/joint_command",
            self.on_command,
            10,
        )
        self.timer = self.create_timer(0.5, self.republish_last_command)

    def on_command(self, msg: JointState) -> None:
        values_by_name = dict(zip(msg.name, msg.position))
        trajectory = JointTrajectory()
        trajectory.header.stamp = self.get_clock().now().to_msg()
        trajectory.joint_names = JOINT_NAMES

        point = JointTrajectoryPoint()
        point.positions = [
            servo_degrees_to_controller_position(
                name,
                values_by_name.get(name, POSES["rest"][index]),
            )
            for index, name in enumerate(JOINT_NAMES)
        ]
        point.time_from_start = Duration(sec=2)
        trajectory.points = [point]
        self.last_command = trajectory
        self.publisher.publish(trajectory)

    def republish_last_command(self) -> None:
        if self.last_command is None:
            return
        self.last_command.header.stamp = self.get_clock().now().to_msg()
        self.publisher.publish(self.last_command)


def main() -> None:
    rclpy.init()
    node = JointTrajectoryBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
