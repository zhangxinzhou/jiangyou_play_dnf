import ctypes
import ctypes.wintypes
import sys
import time

import pyautogui
import pydirectinput
import win32api
import win32con
import win32gui
from pynput import keyboard

from constants import *

# 退出
program_exit = False
# 暂停
program_pause = False


# 按f2键,程序将会退出,退出原理:pyautogui打开安全模式,并且将鼠标移动到(0,0)位置触发异常事件
def on_press(key):
    global program_exit
    global program_pause
    if key == keyboard.Key.f4:
        program_exit = True
        print(f"you press key [{key}], program will exit after a few seconds.")

    elif key == keyboard.Key.pause:
        program_pause = not program_pause
        if program_pause:
            print(f"you press key [{key}], program will pause after a few seconds.")
        else:
            print(f"you press key [{key}], program will resume after a few seconds.")


listener = keyboard.Listener(on_press=on_press)
listener.start()


def hand_exit_and_pause() -> bool:
    global program_exit
    global program_pause
    if program_exit:
        print("program exit.")
        sys.exit(-1)
    elif program_pause:
        print("program pause...")
        return True
    return False


def direct_press_key(key_list: list, duration=0.0, back_swing=0.0) -> None:
    """
    :param key_list: 按键
    :param duration: 按键持续时间,单位秒
    :param back_swing: 技能后摇时间,单位秒
    :return:
    """
    while hand_exit_and_pause():
        time.sleep(1)

    key_list_len = len(key_list)
    if key_list_len <= 0:
        raise Exception("key_list must not be empty!")
    if duration <= 0.0:
        pydirectinput.press(key_list)
    else:
        last_key = key_list[-1]
        other_key_list = key_list[:-1]
        if len(other_key_list) > 0:
            pydirectinput.press(other_key_list)
        pydirectinput.keyDown(last_key)
        time.sleep(duration)
        pydirectinput.keyUp(last_key)

    # 休眠后摇时间
    time.sleep(back_swing)


def mouse_left_click() -> None:
    while hand_exit_and_pause():
        time.sleep(1)

    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(0.1)


def mouse_left_double_click() -> None:
    while hand_exit_and_pause():
        time.sleep(1)

    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(0.1)


def mouse_right_click() -> None:
    while hand_exit_and_pause():
        time.sleep(1)

    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 100, 100)
    time.sleep(0.1)


def get_window_hand() -> None:
    window_title = r'地下城与勇士：创新世纪'
    window_hwnd = win32gui.FindWindow(None, window_title)
    if window_title is None or window_hwnd == 0:
        print(f"can not find game [{window_title}]")
        sys.exit()
    return window_hwnd


def get_window_rect(hwnd):
    _function = ctypes.windll.dwmapi.DwmGetWindowAttribute
    rect = ctypes.wintypes.RECT()
    _function(ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(9), ctypes.byref(rect), ctypes.sizeof(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def to_ui_role_select():
    direct_press_key(key_list='esc', back_swing=0.1)
    img_location = pyautogui.locateOnScreen(image=IMG_SELECT_ROLE_PATH, confidence=0.9)
    if img_location is None:
        direct_press_key(key_list='esc', back_swing=0.1)
        img_location = pyautogui.locateOnScreen(image=IMG_SELECT_ROLE_PATH, confidence=0.9)

    # 如果还是无法识别,那就只能结束了
    if img_location is None:
        print("can not find image on screen, end")
        sys.exit()

    x, y = pyautogui.center(img_location)
    pyautogui.moveTo(x=x, y=y)
    mouse_left_click()


def move_to_arbitrator():
    direct_press_key(key_list=['right'], duration=2)
    img_location = pyautogui.locateOnScreen(image=IMG_ARBITRATOR_AREA_PATH, confidence=0.9)
    if img_location is not None:
        x, y = pyautogui.center(img_location)
        pyautogui.moveTo(x=x, y=y)
        mouse_left_click()
        direct_press_key(key_list=['right'], duration=2)
        img_location = pyautogui.locateOnScreen(image=IMG_ARBITRATOR_SMALL_PATH, confidence=0.9)
        if img_location is not None:
            x, y = pyautogui.center(img_location)
            pyautogui.moveTo(x=x, y=y)
            mouse_left_click()
        img_location = pyautogui.locateOnScreen(image=IMG_ARBITRATOR_BIG_PATH, confidence=0.9)
        if img_location is not None:
            x, y = pyautogui.center(img_location)
            pyautogui.moveTo(x=x, y=y)
            mouse_left_click()
    time.sleep(5)


def has_no_fatigue_point() -> bool:
    img_location = pyautogui.locateOnScreen(image=IMG_ZERO_FATIGUE_PATH, confidence=0.95)
    if img_location is not None:
        return True
    img_location = pyautogui.locateOnScreen(image=IMG_ZERO_FATIGUE_PATH, confidence=0.95)
    if img_location is not None:
        return True
    return False
