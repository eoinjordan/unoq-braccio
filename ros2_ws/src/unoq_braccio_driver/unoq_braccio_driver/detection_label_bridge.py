import json
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from vision_msgs.msg import Detection2DArray


class DetectionLabelBridge(Node):
    """Bridge edgeimpulse_ros detections to the Braccio label topic.

    edgeimpulse_ros publishes vision_msgs/Detection2DArray, while the pick/place
    executor consumes a std_msgs/String on /edge_impulse/label. This node selects
    the highest-scoring detection and republishes its class label (plus the raw
    detection as JSON, matching edge_impulse_vision) so the executor is unchanged.
    """

    def __init__(self) -> None:
        super().__init__("unoq_braccio_detection_label_bridge")
        self.declare_parameter("detections_topic", "/edgeimpulse_detector/detections")
        self.declare_parameter("label_topic", "/edge_impulse/label")
        self.declare_parameter("detection_topic", "/edge_impulse/detection")
        self.declare_parameter("min_confidence", 0.65)
        self.declare_parameter("max_fps", 2.0)
        self.declare_parameter("publish_unmatched", False)

        self.min_confidence = float(self.get_parameter("min_confidence").value)
        self.max_period = 1.0 / max(float(self.get_parameter("max_fps").value), 0.1)
        self.publish_unmatched = bool(self.get_parameter("publish_unmatched").value)
        self.last_run = 0.0

        self.label_pub = self.create_publisher(
            String, str(self.get_parameter("label_topic").value), 10
        )
        self.detection_pub = self.create_publisher(
            String, str(self.get_parameter("detection_topic").value), 10
        )
        self.subscription = self.create_subscription(
            Detection2DArray,
            str(self.get_parameter("detections_topic").value),
            self.on_detections,
            10,
        )

    def on_detections(self, msg: Detection2DArray) -> None:
        now = time.monotonic()
        if now - self.last_run < self.max_period:
            return

        best = self.select_best(msg)
        if best is None:
            return
        self.last_run = now

        label, confidence, detection = best
        self.detection_pub.publish(String(data=json.dumps(detection)))
        if confidence >= self.min_confidence:
            self.label_pub.publish(String(data=label))
        elif self.publish_unmatched:
            self.label_pub.publish(String(data="unmatched"))

    def select_best(self, msg: Detection2DArray):
        best_label = ""
        best_score = -1.0
        best_bbox = None
        for detection in msg.detections:
            if not detection.results:
                continue
            hypothesis = detection.results[0].hypothesis
            score = float(hypothesis.score)
            if score > best_score:
                best_score = score
                best_label = str(hypothesis.class_id)
                best_bbox = detection.bbox

        if best_bbox is None or not best_label:
            return None

        # vision_msgs 4.x nests the centre under `position`; older releases expose
        # x/y directly on the centre pose.
        center = best_bbox.center
        point = getattr(center, "position", center)
        detection = {
            "label": best_label,
            "confidence": best_score,
            "bbox": {
                "x": float(getattr(point, "x", 0.0)),
                "y": float(getattr(point, "y", 0.0)),
                "width": float(best_bbox.size_x),
                "height": float(best_bbox.size_y),
            },
        }
        return best_label, best_score, detection


def main() -> None:
    rclpy.init()
    node = DetectionLabelBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
