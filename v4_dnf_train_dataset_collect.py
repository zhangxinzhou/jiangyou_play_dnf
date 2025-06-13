import datetime
import os.path
import sys

import cv2
import numpy as np
import win32gui
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication
from pynput import keyboard

# 暂停
save_image = False

# 用f12来截图
# 退出和暂停功能的实现
def on_press(_key):
    global save_image
    if _key == keyboard.Key.f12:
        save_image = True


listener = keyboard.Listener(on_press=on_press)
listener.start()

# 游戏窗口截图所需
_app = QApplication(sys.argv)
_screen = QApplication.primaryScreen()


# QImage 转换成opencv的matrix
def q_image_to_cv2_mat(_q_image: QImage):
    tmp_img = _q_image.convertToFormat(QImage.Format_RGBX8888)
    ptr = tmp_img.constBits()
    ptr.setsize(tmp_img.byteCount())
    _cv2_mat = np.array(ptr, copy=True).reshape(tmp_img.height(), tmp_img.width(), 4)
    _cv2_mat = cv2.cvtColor(_cv2_mat, cv2.COLOR_BGRA2RGB)
    return _cv2_mat


# dataset路径,如果不存在就创建
datasets_images_path = r'datasets/v4_dnf_arbitrator/images'
datasets_labels_path = r'datasets/v4_dnf_arbitrator/labels'
if not os.path.exists(datasets_images_path):
    os.makedirs(datasets_images_path)
if not os.path.exists(datasets_labels_path):
    os.makedirs(datasets_labels_path)
if __name__ == '__main__':
    window_title = r'地下城与勇士：创新世纪'
    window_hwnd = win32gui.FindWindow(None, window_title)
    if window_title is None:
        print(f"can not find game [{window_title}]")
        exit(-1)

    save_msg = f""
    while True:
        q_image = _screen.grabWindow(window_hwnd).toImage()
        cv2_mat = q_image_to_cv2_mat(q_image)
        if save_image:
            save_image = False
            file_name = f"dnf_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            img_data_full_path = os.path.join(datasets_images_path, f'{file_name}')
            save_msg = f"save img [{file_name}] success"
            cv2.imwrite(img_data_full_path, cv2_mat)
            print(save_msg)

        # 显示图片
        cv2.putText(cv2_mat, text=save_msg, org=(20, 20), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5,
                    color=(0, 0, 255))
        cv2.imshow('game_screen', cv2_mat)
        key = cv2.waitKey(1)
        # esc 退出
        if key == 27:
            break
