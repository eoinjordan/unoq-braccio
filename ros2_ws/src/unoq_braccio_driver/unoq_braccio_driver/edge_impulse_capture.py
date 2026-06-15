import csv
import os
from datetime import datetime, timezone

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

from unoq_braccio_driver.braccio_model import JOINT_NAMES


class EdgeImpulseCapture(Node):
    def __init__(self) -> None:
        super().__init__("unoq_braccio_edge_impulse_capture")
        self.declare_parameter("output_file", "edge_impulse/captures/braccio_capture.csv")
        self.declare_parameter("label", "unlabeled")
        self.declare_parameter("label_topic", "/edge_impulse/label")

        self.current_label = str(self.get_parameter("label").value)
        self.last_positions: dict[str, float] | None = None
        self.last_time_ns: int | None = None
        self.last_status = ""
        self.last_vision_stats = ""

        output_file = str(self.get_parameter("output_file").value)
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        file_exists = os.path.exists(output_file)
        self.handle = open(output_file, "a", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.handle, fieldnames=self.fieldnames())
        if not file_exists or os.path.getsize(output_file) == 0:
            self.writer.writeheader()

        self.command_sub = self.create_subscription(
            JointState,
            "/braccio/joint_command",
            self.on_command,
            10,
        )
        self.label_sub = self.create_subscription(
            String,
            str(self.get_parameter("label_topic").value),
            self.on_label,
            10,
        )
        self.status_sub = self.create_subscription(
            String,
            "/braccio/firmware_status",
            self.on_status,
            10,
        )
        self.vision_sub = self.create_subscription(
            String,
            "/braccio/vision_stats",
            self.on_vision_stats,
            10,
        )
        self.get_logger().info(f"Capturing Edge Impulse CSV rows to {output_file}")

    def fieldnames(self) -> list[str]:
        fields = ["timestamp", "label", "dt_ms"]
        fields += [f"{name}_deg" for name in JOINT_NAMES]
        fields += [f"{name}_delta_deg" for name in JOINT_NAMES]
        fields += [f"{name}_rate_dps" for name in JOINT_NAMES]
        fields += ["firmware_status", "vision_stats"]
        return fields

    def on_label(self, msg: String) -> None:
        self.current_label = msg.data.strip() or "unlabeled"

    def on_status(self, msg: String) -> None:
        self.last_status = msg.data.strip()

    def on_vision_stats(self, msg: String) -> None:
        self.last_vision_stats = msg.data.strip()

    def on_command(self, msg: JointState) -> None:
        now_ns = self.get_clock().now().nanoseconds
        positions = dict(zip(msg.name, msg.position))
        ordered = {name: float(positions.get(name, 0.0)) for name in JOINT_NAMES}

        if self.last_time_ns is None:
            dt_ms = 0.0
        else:
            dt_ms = (now_ns - self.last_time_ns) / 1_000_000.0

        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "label": self.current_label,
            "dt_ms": f"{dt_ms:.3f}",
            "firmware_status": self.last_status,
            "vision_stats": self.last_vision_stats,
        }

        for name, value in ordered.items():
            previous = self.last_positions[name] if self.last_positions else value
            delta = value - previous
            rate = 0.0 if dt_ms <= 0.0 else delta / (dt_ms / 1000.0)
            row[f"{name}_deg"] = f"{value:.3f}"
            row[f"{name}_delta_deg"] = f"{delta:.3f}"
            row[f"{name}_rate_dps"] = f"{rate:.3f}"

        self.writer.writerow(row)
        self.handle.flush()
        self.last_positions = ordered
        self.last_time_ns = now_ns

    def destroy_node(self) -> bool:
        if hasattr(self, "handle"):
            self.handle.close()
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = EdgeImpulseCapture()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
