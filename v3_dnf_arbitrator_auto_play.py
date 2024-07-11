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
PROGRAM_EXIT = False
# 暂停
PROGRAM_PAUSE = False


#######################################################
# utils START
#######################################################

# 退出和暂停
def on_press(key):
    global PROGRAM_EXIT
    global PROGRAM_PAUSE
    if key == keyboard.Key.f4:
        PROGRAM_EXIT = True
        print(f"you press key [{key}], program will exit after a few seconds.")

    elif key == keyboard.Key.f3:
        PROGRAM_PAUSE = not PROGRAM_PAUSE
        if PROGRAM_PAUSE:
            print(f"you press key [{key}], program will pause after a few seconds.")
        else:
            print(f"you press key [{key}], program will resume after a few seconds.")


listener = keyboard.Listener(on_press=on_press)
listener.start()

# redis
REDIS_POOL = redis.ConnectionPool(host='127.0.0.1', port=6379)
REDIS_CONN = redis.Redis(connection_pool=REDIS_POOL)


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
# utils END
#######################################################

#######################################################
# global start
#######################################################
class GlobalParameter(object):
    def __init__(self):
        # 时间
        self.progress_start_time = None
        self.progress_end_time = None
        self.role_start_time = None
        self.role_end_time = None
        self.stage_start_time = None
        self.stage_end_time = None
        # 记录方法执行情况
        self.method_count: int = 0
        self.method_name_previous: str = None
        self.method_name_current: str = None
        self.method_name_next: str = None
        self.method_name_continue_count = 0
        self.method_name_continue_limit: int = 10
        # 角色相关配置
        self.v3_all_role_config = None
        self.v3_one_role_config = None
        #
        self.role_name: str = None
        self.role_current_round: int = 0
        self.role_max_round: int = 10

        # 从redis中读取角色配置
        redis_key = "V3_ALL_ROLE_STATUS_" + time.strftime("%Y-%m-%d", time.localtime())
        redis_val = REDIS_CONN.get(redis_key)
        if redis_val is None:
            with open('v3_all_role_config.json', 'r', encoding='utf-8') as f:
                redis_val = f.read()
            REDIS_CONN.set(name=redis_key, value=redis_val)
        self.v3_all_role_config: list = json.loads(redis_val)


GP = GlobalParameter()
execute_records_file = open('v3_execute_records.txt', 'w+', encoding='utf-8')


def aspect(func):
    def wrapper(*args, **kwargs):
        _f_name = func.__name__
        # 如果某一个方法被连续执行N次,说明很有可能被卡在了某种场景之中,处于死循环中,需要重置到某个初始场景中来跳出死循环
        if GP.method_name_current == GP.method_name_current:
            GP.method_name_continue_count += 1
        else:
            GP.method_name_continue_count = 0
        if GP.method_name_continue_count > GP.method_name_continue_limit:
            print(f'method_name=[{_f_name}], continuously called by [{GP.method_name_list_limit}] times, so reset')
            # return program_reset

        _time = time.time()
        GP.method_count += 1
        GP.method_name_previous = GP.method_name_current
        GP.method_name_current = _f_name
        execute_records_file.write(
            f'index=[{GP.count:0>10d}],'
            f' time=[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}],'
            f' method_name=[{_f_name:<20}] start\n'
        )
        _result = func(*args, **kwargs)
        GP.method_name_next = _f_name.__name__
        _cost = int((time.time() - _time) * 1000)
        execute_records_file.write(
            f'index=[{GP.count:0>10d}],'
            f' time=[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}],'
            f' method_name=[{_f_name:<20}] end,'
            f'     cost=[{_cost:>6d}]ms\n'
        )
        # 暂停和退出
        global PROGRAM_EXIT
        global PROGRAM_PAUSE
        if PROGRAM_EXIT:
            print("program exit...")
            sys.exit(-1)
        while PROGRAM_PAUSE:
            if PROGRAM_EXIT:
                print("program exit...")
                sys.exit(-1)
            print("program pause...")
            time.sleep(1)
        return _result

    return wrapper


#######################################################
# global end
#######################################################


#######################################################
# 调用链 START
#######################################################

@aspect
def program_start():
    GP.progress_start_time = time.time()
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] program start')
    return program_route


@aspect
def program_end():
    GP.progress_end_time = time.time()
    _cost = int(GP.progress_end_time - GP.progress_end_time)
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] program end, cost=[{_cost}s]')
    sys.exit(0)


@aspect
def program_reset():
    # 如果某一个方法被连续执行N次,说明很有可能被卡在了某种场景之中,通过该方法重置
    return program_route


@aspect
def program_route():
    # route思路:识别xx场景->路由到执行xx场景的方法
    # 识别到loading->执行等一秒
    # 识别到赛利亚->esa
    # 识别到选择角色框->点击
    # 识别到选择角色界面->选择角色

    pass


@aspect
def role_start():
    GP.role_start_time = time.time()
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{GP.role_name}] start]')
    return role_route


@aspect
def role_end():
    GP.role_end_time = time.time()
    _cost = int(GP.role_start_time - GP.role_end_time)
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{GP.role_name}] end, cost=[{_cost}s]')
    pass


@aspect
def role_route():
    pass


@aspect
def stage_start():
    GP.role_start_time = time.time()
    print(
        f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{GP.role_name}], '
        f'round=[{GP.role_current_round:>2}/{GP.role_max_round:>2}] start]')
    return stage_route


@aspect
def stage_end():
    GP.role_end_time = time.time()
    _cost = int(GP.role_start_time - GP.role_end_time)
    print(
        f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{GP.role_name}], '
        f'round=[{GP.role_current_round:>2}/{GP.role_max_round:>2}] end], cost=[{_cost}s]')
    return program_route


@aspect
def stage_route():
    pass


@aspect
def role_select():
    for _i in GP.v3_all_role_config:
        _role_dict: dict = _i
        _role_name = _role_dict.get('role_name')
        _role_status = _role_dict.get('role_status')
        if _role_status == 'done':
            continue
        elif _role_status == 'todo':
            GP.role_name = _role_name
            GP.v3_one_role_config = _role_dict
            GP.next_method_name = 'role_start'
            return
    GP.next_method_name = 'progress_end'


#######################################################
# 调用链 END
#######################################################

def execute():
    method_obj = program_start
    while True:
        method_obj = method_obj()


if __name__ == '__main__':
    pass
    # execute(first_method_name='progress_start')
