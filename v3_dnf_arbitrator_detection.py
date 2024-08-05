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

import v3_all_role_config

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


mouse_x = 0
mouse_y = 0


def show_mouse_position(_event, _x, _y, _flags, _params):
    global mouse_x
    global mouse_y
    mouse_x = _x
    mouse_y = _y


# 判断是不是灰色图
def calc_gray_confidence(_cv2_mat):
    # 虽然不知道是什么原理,但是真的好用 来源 https://stackoverflow.org.cn/questions/64038736
    hsv = cv2.cvtColor(_cv2_mat, cv2.COLOR_BGR2HSV)
    # define range of gray color in HSV
    lower_gray = np.array([0, 0, 0])
    upper_gray = np.array([255, 10, 255])
    # Threshold the HSV image to get only gray colors
    mask = cv2.inRange(hsv, lower_gray, upper_gray)
    return np.count_nonzero(mask) / mask.size


COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)


# 判断技能是否可用的方法
def handle_skill(_cv2_mat):
    _box_x1 = v3_all_role_config.SKILL_BOX_X1
    _box_x2 = v3_all_role_config.SKILL_BOX_X2
    _box_y1 = v3_all_role_config.SKILL_BOX_Y1
    _box_y2 = v3_all_role_config.SKILL_BOX_Y2
    # 具体技能
    _all_count_y = 0
    _all_count = 0
    for _skill_key, _skill_xy in v3_all_role_config.SKILL_ICON_LOCATION.items():
        _pt1_x, _pt1_y, _pt2_x, _pt2_y = _skill_xy
        _pt1, _pt2 = (_pt1_x, _pt1_y), (_pt2_x, _pt2_y)
        # 判断技能是否可用
        _skill_icon = _cv2_mat[_pt1_y:_pt2_y, _pt1_x:_pt2_x]
        _gray_confidence = calc_gray_confidence(_skill_icon)
        _one_y = _gray_confidence < 0.6
        _all_count += 1
        if _one_y:
            _all_count_y += 1
        _color = COLOR_GREEN if _one_y else COLOR_RED
        cv2.rectangle(_cv2_mat, _pt1, _pt2, color=_color, thickness=1)
        redis_conn.hset('skill', _skill_key, 'Y' if _one_y else 'N')
    # 整个技能框
    _all_y = _all_count_y / _all_count > 0.5
    _color = COLOR_GREEN if _all_y else COLOR_RED
    cv2.rectangle(_cv2_mat, (_box_x1 - 1, _box_y1 - 1), (_box_x2 + 1, _box_y2 + 1), color=_color, thickness=1)
    redis_conn.hset('skill', f'all', 'Y' if _all_y else 'N')


if __name__ == '__main__':
    window_title = r'地下城与勇士：创新世纪'
    window_hwnd = win32gui.FindWindow(None, window_title)
    if window_title is None or window_hwnd == 0:
        print(f"can not find game [{window_title}]")
        exit(-1)
    print('start loading model')
    model_path = r"models/best.pt"
    model = YOLO(model_path)
    print('end loading model')

    last_n_label_max_size = 10
    last_n_label_list = []
    # 最近n个预测结果
    last_n_result_max_size = 3
    last_n_result_list = []
    prev_time = time.time()
    while True:
        cost_time = time.time() - prev_time
        prev_time = time.time()

        q_image = _screen.grabWindow(window_hwnd).toImage()
        cv2_mat = q_image_to_cv2_mat(q_image)
        img_shape = cv2_mat.shape
        height = img_shape[0]
        width = img_shape[1]

        # 渲染模型预测结果
        results = model.predict(cv2_mat)

        # 因为一次只有一张图片,所以就只有只返回一个results只有一个
        result = results[0]
        detections = sv.Detections.from_ultralytics(result)
        labels = [model.model.names[class_id] for class_id in detections.class_id]
        if len(last_n_label_list) > last_n_label_max_size:
            last_n_label_list.pop(0)
        last_n_label_list.append(set(labels))
        last_n_label_list_size = len(last_n_label_list)
        label_rate_dict = {}
        tmp_dict = {}
        for i in last_n_label_list:
            for j in i:
                count = tmp_dict.get(j, 0)
                count += 1
                tmp_dict[j] = count
        set_all = label_rate_dict.keys() | tmp_dict.keys()
        for k in set_all:
            count = tmp_dict.get(k, 0)
            rate = count / last_n_label_list_size
            label_rate_dict[k] = rate
            print(k, rate)
        # 存在概率
        redis_conn.set(name='labels_exists_dict', value=json.dumps(label_rate_dict))

        # 写入redis的值
        label_dict = {}
        if len(labels) > 0:
            result_json_obj = json.loads(result.tojson())
            # 每个分类中找出一个概率最大的即可
            last_n_result_list_size = len(last_n_result_list)
            if last_n_result_list_size > last_n_result_max_size:
                last_n_result_list.pop(0)
            last_n_result_list.append(result_json_obj)

            for i in last_n_result_list:
                for j in i:
                    label_name = j['name']
                    label_prob = j['confidence']
                    label_box = j['box']
                    label_box_x_center = int((label_box['x1'] + label_box['x2']) / 2)
                    label_box_y_center = int((label_box['y1'] + label_box['y2']) / 2)
                    label_box_center = [label_box_x_center, label_box_y_center]
                    prev_label_prob = 0
                    if label_prob > label_dict.get(label_name, {}).get(label_prob, 0):
                        if label_dict.get(label_name) is None:
                            label_dict[label_name] = {}
                        label_dict[label_name]['label_name'] = label_name
                        label_dict[label_name]['label_prob'] = label_prob
                        label_dict[label_name]['label_box'] = label_box
                        label_dict[label_name]['label_box_center'] = label_box_center
            for k, v in label_dict.items():
                print(k, v)
                # 画出坐标
                x, y = v['label_box_center']
                cv2.line(cv2_mat, pt1=(x, y - 100), pt2=(x, y + 100), color=(0, 0, 255), thickness=3)
                cv2.line(cv2_mat, pt1=(x - 100, y), pt2=(x + 100, y), color=(0, 0, 255), thickness=3)
        redis_conn.set(name='labels_detail_dict', value=json.dumps(label_dict))

        # 需要查看监测的结果,就将show_window改为True
        show_window = True
        window_name = 'game_screen'
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, show_mouse_position)
        if show_window:
            left, top, right, bottom = get_window_rect(window_hwnd)

            # 左上角显示窗口相关信息
            cost_text = f'cost [{cost_time * 1000:.2f}] ms'
            rect_text = f', rectangle [left={left:<4} top={top:<4} right={right:<4} bottom={bottom:<4}]'
            text = cost_text + rect_text
            cv2.putText(cv2_mat, text=text, org=(20, 20), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5,
                        color=(0, 0, 255))

            position_txt = f'x=[{mouse_x:>4}] y=[{mouse_y:>4}] color=[{cv2_mat[mouse_y][mouse_x]}]'
            cv2.putText(cv2_mat, text=position_txt, org=(20, 20 + 40), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5,
                        color=(0, 0, 255))
            handle_skill(cv2_mat)
            cv2.imshow(window_name, result.plot())
            key = cv2.waitKey(1)

            if key != -1:
                break
