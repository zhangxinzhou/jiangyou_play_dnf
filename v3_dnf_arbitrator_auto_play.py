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

import v3_all_role_config as all_role_config

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
REDIS_CONN = redis.Redis(connection_pool=REDIS_POOL, decode_responses=True)


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
    _window_title = r'地下城与勇士：创新世纪'
    _window_hwnd = win32gui.FindWindow(None, _window_title)
    if _window_title is None or _window_hwnd == 0:
        print(f"can not find game [{_window_title}]")
        sys.exit()
    return _window_hwnd


def get_relative_window_rect(hwnd):
    _function = ctypes.windll.dwmapi.DwmGetWindowAttribute
    rect = ctypes.wintypes.RECT()
    _function(ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(9), ctypes.byref(rect), ctypes.sizeof(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def get_absolute_window_rect(_hwnd, _game_x, _game_y):
    _window_left, _window_top, _window_right, _window_bottom = get_relative_window_rect(_hwnd)
    return _window_left + _game_x, _window_top + _game_y


def redis_get_labels_detail() -> (list, dict):
    _labels_dict: dict = json.loads(REDIS_CONN.get('labels_detail_dict'))
    if _labels_dict is None:
        _labels_dict = {}
    _labels_list = [key for key, val in _labels_dict.items()]
    return _labels_list, _labels_dict


def redis_get_skill(skill_key) -> bool:
    _skill = REDIS_CONN.hget('skill', skill_key)
    _skill_ok = _skill == b'Y'
    return _skill_ok


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

        redis_key = "V3_ALL_ROLE_CONFIG_"
        yesterday_str = time.strftime("%Y-%m-%d", time.localtime())
        yesterday_redis_key = redis_key + yesterday_str
        today_str = time.strftime("%Y-%m-%d", time.localtime(time.time() - 24 * 3600))
        today_redis_key = redis_key + today_str
        # 删除昨天的key
        REDIS_CONN.delete(yesterday_redis_key)
        # 从redis中读取角色配置
        redis_val = REDIS_CONN.get(today_redis_key)
        if redis_val is None:
            redis_val = json.dumps(all_role_config.ALL_ROLE_CONFIG_LIST)
            REDIS_CONN.set(name=today_redis_key, value=redis_val)
        self.v3_all_role_config: list = json.loads(redis_val)


GP = GlobalParameter()
execute_records_file = open('v3_execute_records.txt', 'w+', encoding='utf-8')


def aspect(func):
    def wrapper(*args, **kwargs):
        _f_name = func.__name__
        _time = time.time()
        GP.method_count += 1
        GP.method_name_previous = GP.method_name_current
        GP.method_name_current = _f_name
        # 如果某一个方法被连续执行N次,说明很有可能被卡在了某种场景之中,处于死循环中,需要重置到某个初始场景中来跳出死循环
        if GP.method_name_previous == GP.method_name_current:
            GP.method_name_continue_count += 1
        else:
            GP.method_name_continue_count = 0
        if GP.method_name_continue_count > GP.method_name_continue_limit:
            print(
                f'method_name=[{GP.method_name_current}], continuously called by [{GP.method_name_continue_count}] times')
            # return program_reset
        execute_records_file.write(
            f'index=[{GP.method_count:0>10d}]'
            f', time=[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}]'
            f', method_name=[{_f_name:<20}] start\n'
        )
        _result = func(*args, **kwargs)
        GP.method_name_next = _result
        _cost = int((time.time() - _time) * 1000)
        execute_records_file.write(
            f'index=[{GP.method_count:0>10d}]'
            f', time=[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}]'
            f', method_name=[{_f_name:<20}] end'
            f', cost=[{_cost:>6d}]ms\n'
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
def template():
    # 1.检查是否满足工作条件
    # 2.满足开始工作,不满足等待N轮,N轮之后还不满足则路由到某个节点
    # 3.开始工作
    # 4.确认工作结束,传递给下一个节点
    pass


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
    _labels_list, _labels_dict = redis_get_labels_detail()
    _labels_list: list = _labels_list
    _labels_dict: dict = _labels_dict

    # town_play_task_icon_light
    if _labels_list.__contains__('town_play_task_icon_light'):
        return handle_town_play_quest

    print("*" * 50)


# 畅玩任务
@aspect
def handle_town_play_quest():
    _labels_list, _labels_dict = redis_get_labels_detail()
    _labels_list: list = _labels_list
    _labels_dict: dict = _labels_dict
    if _labels_list.__contains__('town_play_task_icon_light'):
        # 点击畅玩任务图标
        _x, _y = _labels_dict['town_play_task_icon_light']['label_box_center']
        #
        pydirectinput.moveTo(_x, _y)
        mouse_left_click()


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


def play_one_role(_role_name):
    pass


if __name__ == '__main__':
    # execute(first_method_name='progress_start')
    time.sleep(1)

    window_hwnd = get_window_hand()
    # 被其他窗口遮挡，调用后放到最前面
    win32gui.SetForegroundWindow(window_hwnd)
    # 解决被最小化的情况
    win32gui.ShowWindow(window_hwnd, win32con.SW_RESTORE)
    time.sleep(1)

    while True:
        # 拿分类标签
        _labels_list, _labels_dict = redis_get_labels_detail()

        key_list = ['town_play_quest_claim_light', 'town_play_quest_icon_light', 'town_play_quest_ui_close_button']
        has_label = False
        for key in key_list:
            if _labels_list.__contains__(key):
                # 点击畅玩任务图标
                game_x, game_y = _labels_dict[key]['label_box_center']
                window_x, window_y = get_absolute_window_rect(window_hwnd, game_x, game_y)
                pydirectinput.moveTo(window_x, window_y)
                mouse_left_click()
                has_label = True
                time.sleep(0.3)

        if not has_label and _labels_list.__contains__('town_play_quest_icon_gray'):
            break
