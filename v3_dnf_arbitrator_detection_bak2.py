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


# 判断是不是灰色图
# def calc_gray_confidence(_cv2_mat):
#     # 虽然不知道是什么原理,但是真的好用 来源 https://stackoverflow.org.cn/questions/64038736
#     hsv = cv2.cvtColor(_cv2_mat, cv2.COLOR_BGR2HSV)
#     # define range of gray color in HSV
#     lower_gray = np.array([0, 0, 0])
#     upper_gray = np.array([255, 10, 255])
#     # Threshold the HSV image to get only gray colors
#     mask = cv2.inRange(hsv, lower_gray, upper_gray)
#     _gray_val = np.count_nonzero(mask) / mask.size
#     return _gray_val


def calc_colorful_confidence(_cv2_mat):
    _hsv = cv2.cvtColor(_cv2_mat, cv2.COLOR_BGR2HSV)
    _colorful_lower = np.array([0, 127, 127])
    _colorful_upper = np.array([360, 255, 255])
    _colorful_mask = cv2.inRange(_hsv, _colorful_lower, _colorful_upper)
    _colorful_count = cv2.countNonZero(_colorful_mask)
    _colorful_percent = _colorful_count / _colorful_mask.size

    return _colorful_percent > 0.2


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
        _one_y = calc_colorful_confidence(_skill_icon)
        _all_count += 1
        if _one_y:
            _all_count_y += 1
        _color = COLOR_GREEN if _one_y else COLOR_RED
        cv2.rectangle(_cv2_mat, _pt1, _pt2, color=_color, thickness=1)
        redis_conn.hset('skill', _skill_key, 'Y' if _one_y else 'N')
    # 整个技能框
    _all_y = _all_count_y > 5
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
    model_path = r"models/v3_best.pt"
    model = YOLO(model_path)
    print('end loading model')

    prev_time = time.time()
    # 解决偶尔识别错误的问题,比如(再次挑战正常/灰色)偶尔识别错误,但是马上又会识别正确,对于这种情况就取最近N帧的数据
    n = 3
    last_n_labels_detail_list = []
    last_n_labels_name_list = []
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

        # 写入redis的值
        labels_detail_list = []  # 最近一帧所有的label
        labels_detail_dict = {}  # 最近N帧概率最大的label,label只会出现一次
        if len(labels) > 0:
            labels_detail_list = json.loads(result.tojson())
        # 只保留最近N帧的数据
        while len(last_n_labels_detail_list) >= 3:
            last_n_labels_detail_list.pop(0)
            last_n_labels_name_list.pop(0)
        last_n_labels_detail_list.append(labels_detail_list)
        last_n_labels_name_list.append(set(labels))
        last_n_labels_name_count_dict = {}
        for labels_list in last_n_labels_name_list:
            for label_name in labels_list:
                label_count = last_n_labels_name_count_dict.get(label_name, 0)
                label_count += 1
                last_n_labels_name_count_dict[label_name] = label_count
        # 计算最近N帧出现概率大于0.5的label_name
        last_n_labels_name_set = set(key for key, val in last_n_labels_name_count_dict.items())

        # 处理成字典key是label,多个相同的label只保留概率最大的那个
        for frame in last_n_labels_detail_list:
            for one in frame:
                label_name = one['name']
                label_prob = one['confidence']
                label_box = one['box']
                label_box_x_center = int((label_box['x1'] + label_box['x2']) / 2)
                label_box_y_center = int((label_box['y1'] + label_box['y2']) / 2)
                label_box_center = [label_box_x_center, label_box_y_center]
                if label_prob > labels_detail_dict.get(label_name, {}).get('label_prob', 0):
                    if labels_detail_dict.get(label_name) is None:
                        labels_detail_dict[label_name] = {}
                    labels_detail_dict[label_name]['label_name'] = label_name
                    labels_detail_dict[label_name]['label_prob'] = label_prob
                    labels_detail_dict[label_name]['label_box'] = label_box
                    labels_detail_dict[label_name]['label_box_center'] = label_box_center
        # 处理字典,将坐标画出来
        for k, v in labels_detail_dict.items():
            # 画出坐标
            x, y = v['label_box_center']
            # 十字坐标的长度
            cross_length = 100
            cv2.line(cv2_mat, pt1=(x, y - cross_length), pt2=(x, y + cross_length), color=(0, 0, 255), thickness=3)
            cv2.line(cv2_mat, pt1=(x - cross_length, y), pt2=(x + cross_length, y), color=(0, 0, 255), thickness=3)
        redis_conn.set(name='labels_detail_list', value=json.dumps(labels_detail_list))
        redis_conn.set(name='labels_detail_dict', value=json.dumps(labels_detail_dict))

        # 需要查看监测的结果,就将show_window改为True
        show_window = True
        window_name = 'game_screen'
        cv2.namedWindow(window_name)
        if show_window:
            left, top, right, bottom = get_window_rect(window_hwnd)

            # 左上角显示窗口相关信息
            cost_text = f'cost [{cost_time * 1000:.2f}] ms'
            rect_text = f', rectangle [left={left:<4} top={top:<4} right={right:<4} bottom={bottom:<4}]'
            text = cost_text + rect_text
            cv2.putText(cv2_mat, text=text, org=(20, 20), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5,
                        color=(0, 0, 255))

            handle_skill(cv2_mat)
            cv2.imshow(window_name, result.plot(line_width=1, font_size=0.1))
            key = cv2.waitKey(1)

            if key != -1:
                break
