from ultralytics import YOLO
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if __name__ == '__main__':
    # Create a new YOLO model from scratch
    model = YOLO('yolov8n.yaml')

    # Load a pretrained YOLO model (recommended for training)
    model = YOLO('yolov8n.pt')

    # Train the model using the 'coco128.yaml' dataset for 3 epochs
    results = model.train(data='coco128.yaml', epochs=3)

    # Evaluate the model's performance on the validation set
    results = model.val()

    # Perform object detection on an image using the model
    results = model('dnf.png')

    # Export the model to ONNX format
    success = model.export(format='onnx')
    print("*" * 100)
    print(success)
