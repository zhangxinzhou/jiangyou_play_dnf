from ultralytics import YOLO
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if __name__ == '__main__':
    # Create a new YOLO model from scratch
    model = YOLO('yolov8n.yaml')

    # Load a pretrained YOLO model (recommended for training)
    model = YOLO('yolov8n.pt')

    yaml_path = '_datasets_dnf_arbitrator.yaml'
    results = model.train(data=yaml_path, epochs=100)
    print("*" * 100)
    print(results)

    # Evaluate the model's performance on the validation set
    results = model.val()

    print("*" * 100)
    print(results)
