import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from unoq_braccio_driver.braccio_model import JOINT_NAMES

SIM_JOINT_NAMES = JOINT_NAMES


def servo_degrees_to_urdf_radians(name: str, value: float) -> float:
    centered = float(value) - 90.0
    if name == "shoulder":
        centered = float(value) - 90.0
    elif name == "gripper":
        return 0.1750 + max(0.0, min(1.0, (float(value) - 10.0) / 100.0)) * (1.2741 - 0.1750)
    return centered * 3.14159265359 / 180.0


class JointStateSimulator(Node):
    def __init__(self) -> None:
        super().__init__("unoq_braccio_joint_state_simulator")
        self.publisher = self.create_publisher(JointState, "/joint_states", 10)
        self.subscription = self.create_subscription(
            JointState,
            "/braccio/joint_command",
            self.on_command,
            10,
        )

    def on_command(self, msg: JointState) -> None:
        values_by_name = dict(zip(msg.name, msg.position))
        state = JointState()
        state.header.stamp = self.get_clock().now().to_msg()
        state.name = SIM_JOINT_NAMES
        state.position = [
            servo_degrees_to_urdf_radians(name, values_by_name.get(name, 90.0))
            for name in SIM_JOINT_NAMES
        ]
        self.publisher.publish(state)


def main() -> None:
    rclpy.init()
    node = JointStateSimulator()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
