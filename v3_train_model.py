from ultralytics import YOLO
import os
from ruamel import yaml

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

CLASSES_PATH = r'datasets\v3_dnf_arbitrator\classes.txt'
DATASETS_YMAL_PATH = r'_v3_datasets_dnf_arbitrator.yaml'


def handle_detasets_ymal():
    classes_names = {}
    with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            classes_names[index] = line.strip()

    with open(DATASETS_YMAL_PATH, 'r', encoding='utf-8') as f:
        yaml_file = yaml.load(f.read(), Loader=yaml.RoundTripLoader)
        yaml_file['names'] = classes_names

    with open(DATASETS_YMAL_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(data=yaml_file, stream=f, Dumper=yaml.RoundTripDumper)


def train_model():
    # Create a new YOLO model from scratch
    model = YOLO('yolov8x.yaml')

    # Load a pretrained YOLO model (recommended for training)
    model = YOLO('yolov8x.pt')

    results = model.train(data=DATASETS_YMAL_PATH, epochs=1000)
    print("*" * 100)
    print(results)

    # Evaluate the model's performance on the validation set
    results = model.val()

    print("*" * 100)
    print(results)


if __name__ == '__main__':
    # 将数据集的classes.txt文件转换为yaml文件
    handle_detasets_ymal()
    train_model()
