import socket

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from unoq_braccio_driver.braccio_model import command_line_from_positions


class TcpBridge(Node):
    def __init__(self) -> None:
        super().__init__("unoq_braccio_tcp_bridge")
        self.declare_parameter("host", "unoq.local")
        self.declare_parameter("port", "8765")
        self.declare_parameter("command_topic", "/braccio/joint_command")
        self.declare_parameter("timeout", 2.0)

        self.host = str(self.get_parameter("host").value)
        self.port = int(str(self.get_parameter("port").value))
        self.timeout = float(self.get_parameter("timeout").value)
        topic = self.get_parameter("command_topic").value

        self.subscription = self.create_subscription(JointState, topic, self.on_command, 10)
        self.get_logger().info(f"TCP bridge targeting {self.host}:{self.port}")

    def on_command(self, msg: JointState) -> None:
        if not msg.name or not msg.position:
            self.get_logger().warning("Ignoring empty JointState command")
            return

        line = command_line_from_positions(list(msg.name), list(msg.position))
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                sock.sendall((line + "\n").encode("ascii"))
                response = sock.recv(128).decode("ascii", errors="replace").strip()
        except OSError as error:
            self.get_logger().error(f"TCP command failed: {error}")
            return

        if response != "OK":
            self.get_logger().warning(f"Remote agent response: {response or '<empty>'}")


def main() -> None:
    rclpy.init()
    node = TcpBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
