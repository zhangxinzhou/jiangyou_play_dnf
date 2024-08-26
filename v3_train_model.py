from ultralytics import YOLO
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if __name__ == '__main__':
    # Create a new YOLO model from scratch
    model = YOLO('yolov8x.yaml')

    # Load a pretrained YOLO model (recommended for training)
    model = YOLO('yolov8x.pt')

    yaml_path = '_v3_datasets_dnf_arbitrator.yaml'
    results = model.train(data=yaml_path, epochs=200)
    print("*" * 100)
    print(results)

    # Evaluate the model's performance on the validation set
    results = model.val()

    print("*" * 100)
    print(results)
