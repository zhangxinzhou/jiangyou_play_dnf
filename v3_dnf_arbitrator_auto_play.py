import ctypes
import ctypes.wintypes
import datetime
import json
import sys
import time

import pyautogui
import pydirectinput
import redis
import win32api
import win32con
import win32gui
from pynput import keyboard

# 关闭安全模式
pyautogui.FAILSAFE = False
# 延迟设置
pyautogui.PAUSE = 0.01
# 关闭安全模式
pydirectinput.FAILSAFE = False
# 延迟设置,默认0.1
pydirectinput.PAUSE = 0.01

# 退出
program_exit = False
# 暂停
program_pause = False


# 退出和暂停
def on_press(key):
    global program_exit
    global program_pause
    if key == keyboard.Key.f4:
        program_exit = True
        print(f"you press key [{key}], program will exit after a few seconds.")

    elif key == keyboard.Key.f3:
        program_pause = not program_pause
        if program_pause:
            print(f"you press key [{key}], program will pause after a few seconds.")
        else:
            print(f"you press key [{key}], program will resume after a few seconds.")


listener = keyboard.Listener(on_press=on_press)
listener.start()

# redis
redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
redis_conn = redis.Redis(connection_pool=redis_pool)


#######################################################
# xxx start
#######################################################
class ExecuteParameter(object):
    def __init__(self):
        self.count = 0
        self.progress_start_time = time.time()
        self.role_start_time = None
        self.stage_start_time = None
        self.current_method_name = None
        self.next_method_name = None
        self.V3_ALL_ROLE_CONFIG = None
        self.V3_ONE_ROLE_CONFIG = None
        self.role_name = None

        # 从redis中读取角色配置
        redis_key = "V3_ALL_ROLE_STATUS_" + time.strftime("%Y-%m-%d", time.localtime())
        redis_val = redis_conn.get(redis_key)
        if redis_val is None:
            with open('v3_all_role_config.json', 'r', encoding='utf-8') as f:
                redis_val = f.read()
            redis_conn.set(name=redis_key, value=redis_val)
        self.V3_ALL_ROLE_CONFIG: list = json.loads(redis_val)


E_P = ExecuteParameter()
execute_records_file = open('v3_execute_records.txt', 'w+', encoding='utf-8')


def aspect(func):
    def wrapper(*args, **kwargs):
        _f_name = func.__name__
        _time = time.time()
        E_P.count += 1
        E_P.current_method_name = _f_name
        execute_records_file.write(
            f'index=[{E_P.count:0>10d}],'
            f' time=[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}],'
            f' method_name=[{_f_name:<20}] start\n'
        )
        _result = func(*args, **kwargs)
        _cost = int((time.time() - _time) * 1000)
        execute_records_file.write(
            f'index=[{E_P.count:0>10d}],'
            f' time=[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}],'
            f' method_name=[{_f_name:<20}] end,'
            f'     cost=[{_cost:>6d}]ms\n'
        )
        # 暂停和退出
        global program_exit
        global program_pause
        if program_exit:
            print("program exit.")
            sys.exit(-1)
        while program_pause:
            if program_exit:
                print("program exit.")
                sys.exit(-1)
            print("program pause...")
            time.sleep(1)
        return _result

    return wrapper


def execute(first_method_name):
    E_P.next_method_name = first_method_name
    while True:
        if E_P.next_method_name is None:
            execute_records_file.close()
            break
        eval(E_P.next_method_name)()


#######################################################
# xxx start
#######################################################

#######################################################
# utils start
#######################################################


def press_key(key_list: list, duration=0.0, back_swing=0.3) -> None:
    """
    :param key_list: 按键
    :param duration: 按键持续时间,单位秒
    :param back_swing: 技能后摇时间,单位秒
    :return:
    """
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
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(0.1)


def mouse_left_double_click() -> None:
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(0.1)


def mouse_right_click() -> None:
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


#######################################################
# utils end
#######################################################

#######################################################
# 调用链 start
#######################################################

@aspect
def progress_start():
    print("process start")
    E_P.next_method_name = 'role_select'


@aspect
def progress_end():
    _cost = int(time.time() - E_P.progress_start_time)
    print(f'process end,cost=[{_cost}s]')


@aspect
def role_select():
    for _i in E_P.V3_ALL_ROLE_CONFIG:
        _role_dict: dict = _i
        _role_name = _role_dict.get('role_name')
        _role_status = _role_dict.get('role_status')
        if _role_status == 'done':
            continue
        elif _role_status == 'todo':
            E_P.role_name = _role_name
            E_P.V3_ONE_ROLE_CONFIG = _role_dict
            E_P.next_method_name = 'role_start'
            return
    E_P.next_method_name = 'progress_end'


@aspect
def role_start():
    pass


@aspect
def role_end():
    pass


@aspect
def stage_start():
    pass


@aspect
def stage_end():
    pass


#######################################################
# 调用链 start
#######################################################


if __name__ == '__main__':
    pass
    # execute(first_method_name='progress_start')
