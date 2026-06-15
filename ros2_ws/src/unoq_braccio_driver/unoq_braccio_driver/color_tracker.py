import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class ColorTracker(Node):
    def __init__(self) -> None:
        super().__init__("unoq_braccio_color_tracker")
        self.declare_parameter("image_topic", "/braccio/camera/image_raw")
        self.declare_parameter("label", "object")
        self.declare_parameter("h_min", 35)
        self.declare_parameter("s_min", 80)
        self.declare_parameter("v_min", 60)
        self.declare_parameter("h_max", 85)
        self.declare_parameter("s_max", 255)
        self.declare_parameter("v_max", 255)
        self.declare_parameter("min_area", 500.0)

        self.label = str(self.get_parameter("label").value)
        self.min_area = float(self.get_parameter("min_area").value)
        self.lower = np.array(
            [
                int(self.get_parameter("h_min").value),
                int(self.get_parameter("s_min").value),
                int(self.get_parameter("v_min").value),
            ]
        )
        self.upper = np.array(
            [
                int(self.get_parameter("h_max").value),
                int(self.get_parameter("s_max").value),
                int(self.get_parameter("v_max").value),
            ]
        )

        self.bridge = CvBridge()
        self.label_pub = self.create_publisher(String, "/edge_impulse/label", 10)
        self.stats_pub = self.create_publisher(String, "/braccio/vision_stats", 10)
        self.debug_pub = self.create_publisher(Image, "/braccio/camera/debug", 10)
        self.subscription = self.create_subscription(
            Image,
            str(self.get_parameter("image_topic").value),
            self.on_image,
            10,
        )

    def on_image(self, msg: Image) -> None:
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.medianBlur(mask, 5)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            self.stats_pub.publish(String(data="visible=false"))
            return

        contour = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(contour))
        if area < self.min_area:
            self.stats_pub.publish(String(data=f"visible=false area={area:.1f}"))
            return

        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        height, width = frame.shape[:2]
        x_norm = (cx - width / 2.0) / (width / 2.0)
        y_norm = (cy - height / 2.0) / (height / 2.0)

        self.label_pub.publish(String(data=self.label))
        self.stats_pub.publish(
            String(
                data=(
                    f"visible=true label={self.label} area={area:.1f} "
                    f"cx={cx} cy={cy} x_norm={x_norm:.3f} y_norm={y_norm:.3f}"
                )
            )
        )

        cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
        debug_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        debug_msg.header = msg.header
        self.debug_pub.publish(debug_msg)


def main() -> None:
    rclpy.init()
    node = ColorTracker()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
