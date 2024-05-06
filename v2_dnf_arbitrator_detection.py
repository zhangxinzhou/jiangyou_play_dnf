import ctypes
import ctypes.wintypes
import json
import sys
import time

import cv2
import numpy as np
import redis
import supervision as sv
import win32gui
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication
from ultralytics import YOLO

# 游戏窗口截图所需
_app = QApplication(sys.argv)
_screen = QApplication.primaryScreen()

# redis 用来存储识别到的labels的相关信息,供play程序使用
# redis_conn = redis.Redis(host='127.0.0.1', port='6379')
redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
redis_conn = redis.Redis(connection_pool=redis_pool)


# 获取真实的窗口 POS,win7 之后加了毛玻璃效果
# 如果这个方法无法使用,就用如下的方式

# left, top, right, bottom = win32gui.GetWindowRect(window_hwnd)
def get_window_rect(hwnd):
    _function = ctypes.windll.dwmapi.DwmGetWindowAttribute
    rect = ctypes.wintypes.RECT()
    _function(ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(9), ctypes.byref(rect), ctypes.sizeof(rect))
    return rect.left, rect.top, rect.right, rect.bottom


# QImage 转换成opencv的matrix
def q_image_to_cv2_mat(_q_image: QImage):
    tmp_img = _q_image.convertToFormat(QImage.Format_RGBX8888)
    ptr = tmp_img.constBits()
    ptr.setsize(tmp_img.byteCount())
    _cv2_mat = np.array(ptr, copy=True).reshape(tmp_img.height(), tmp_img.width(), 4)
    _cv2_mat = cv2.cvtColor(_cv2_mat, cv2.COLOR_BGRA2RGB)
    return _cv2_mat


if __name__ == '__main__':
    window_title = r'地下城与勇士：创新世纪'
    window_hwnd = win32gui.FindWindow(None, window_title)
    if window_title is None or window_hwnd == 0:
        print(f"can not find game [{window_title}]")
        exit(-1)
    print('start loading model')
    model = YOLO('yolov8s.pt')
    print('end loading model')

    labels_list = []
    labels_max_len = 10
    prev_time = time.time()
    while True:
        cost_time = time.time() - prev_time
        prev_time = time.time()

        q_image = _screen.grabWindow(window_hwnd).toImage()
        cv2_mat = q_image_to_cv2_mat(q_image)

        # 渲染模型预测结果
        results = model.predict(cv2_mat)
        result = results[0]
        detections = sv.Detections.from_ultralytics(result)

        labels = [model.model.names[class_id] for class_id in detections.class_id]
        # 将labels放入redis
        if len(labels_list) >= labels_max_len:
            labels_list.pop(0)
        labels_list.append(labels)
        json_str = json.dumps(labels_list)
        redis_conn.set(name='labels_list', value=json_str)

        # 需要查看监测的结果,就将show_window改为True
        show_window = True
        if show_window:
            bounding_box_annotator = sv.BoundingBoxAnnotator()
            label_annotator = sv.LabelAnnotator()
            annotated_image = bounding_box_annotator.annotate(scene=cv2_mat, detections=detections)
            annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)

            left, top, right, bottom = get_window_rect(window_hwnd)

            # 左上角显示窗口相关信息
            cost_text = f'cost [{cost_time * 1000:.2f}] ms'
            rect_text = f', rectangle [left={left:<4} top={top:<4} right={right:<4} bottom={bottom:<4}]'
            text = cost_text + rect_text
            cv2.putText(cv2_mat, text=text, org=(20, 20), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5,
                        color=(0, 0, 255))
            cv2.imshow('game_screen', cv2_mat)
            key = cv2.waitKey(1)

            if key != -1:
                break
