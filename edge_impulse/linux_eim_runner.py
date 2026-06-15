import argparse
import json

import cv2
from edge_impulse_linux.image import ImageImpulseRunner


def best_detection(result: dict) -> dict:
    boxes = result.get("result", {}).get("bounding_boxes", [])
    if boxes:
        best = max(boxes, key=lambda item: float(item.get("value", 0.0)))
        return {
            "label": best.get("label", ""),
            "confidence": float(best.get("value", 0.0)),
            "bbox": {
                "x": int(best.get("x", 0)),
                "y": int(best.get("y", 0)),
                "width": int(best.get("width", 0)),
                "height": int(best.get("height", 0)),
            },
        }

    classifications = result.get("result", {}).get("classification", {})
    if classifications:
        label, confidence = max(classifications.items(), key=lambda item: float(item[1]))
        return {"label": label, "confidence": float(confidence), "bbox": None}

    return {"label": "", "confidence": 0.0, "bbox": None}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to Edge Impulse .eim model")
    parser.add_argument("--image", required=True, help="Path to image file")
    args = parser.parse_args()

    image = cv2.imread(args.image)
    if image is None:
        raise RuntimeError(f"Could not read image: {args.image}")

    with ImageImpulseRunner(args.model) as runner:
        model_info = runner.init()
        features, _ = runner.get_features_from_image(image)
        result = runner.classify(features)

    detection = best_detection(result)
    detection["image"] = args.image
    detection["project"] = model_info.get("project", {}).get("name", "")
    print(json.dumps(detection))


if __name__ == "__main__":
    main()
