import argparse
import json


def run_inference(image_path: str) -> dict:
    # Replace this stub with your Edge Impulse Linux/Python SDK call.
    # Return the highest-confidence object detection in this shape:
    return {
        "label": "Red Block",
        "confidence": 0.99,
        "bbox": {"x": 0, "y": 0, "width": 0, "height": 0},
        "image": image_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    print(json.dumps(run_inference(args.image)))


if __name__ == "__main__":
    main()
