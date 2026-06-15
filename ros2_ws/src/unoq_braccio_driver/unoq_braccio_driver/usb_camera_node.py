import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class UsbCameraNode(Node):
    def __init__(self) -> None:
        super().__init__("unoq_braccio_usb_camera")
        self.declare_parameter("camera_index", 0)
        self.declare_parameter("frame_id", "usb_camera")
        self.declare_parameter("width", 640)
        self.declare_parameter("height", 480)
        self.declare_parameter("fps", 15.0)

        self.frame_id = str(self.get_parameter("frame_id").value)
        fps = float(self.get_parameter("fps").value)
        index = int(self.get_parameter("camera_index").value)

        self.capture = cv2.VideoCapture(index)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.get_parameter("width").value))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.get_parameter("height").value))
        self.capture.set(cv2.CAP_PROP_FPS, fps)

        if not self.capture.isOpened():
            raise RuntimeError(f"Could not open USB camera index {index}")

        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Image, "/braccio/camera/image_raw", 10)
        self.timer = self.create_timer(1.0 / max(fps, 1.0), self.publish_frame)
        self.get_logger().info(f"USB camera {index} publishing /braccio/camera/image_raw")

    def publish_frame(self) -> None:
        ok, frame = self.capture.read()
        if not ok:
            self.get_logger().warning("USB camera frame read failed")
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        self.publisher.publish(msg)

    def destroy_node(self) -> bool:
        if hasattr(self, "capture"):
            self.capture.release()
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = UsbCameraNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
