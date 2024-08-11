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


# 窗口/游戏句柄
WINDOW_HWND = get_window_hand()


def get_relative_window_rect(_hwnd):
    _function = ctypes.windll.dwmapi.DwmGetWindowAttribute
    rect = ctypes.wintypes.RECT()
    _function(ctypes.wintypes.HWND(_hwnd), ctypes.wintypes.DWORD(9), ctypes.byref(rect), ctypes.sizeof(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def get_absolute_window_rect(_hwnd, _game_x, _game_y):
    _window_left, _window_top, _window_right, _window_bottom = get_relative_window_rect(_hwnd)
    return _window_left + _game_x, _window_top + _game_y


def redis_get_labels_detail() -> (list, dict):
    _labels_dict: dict = json.loads(REDIS_CONN.get('labels_detail_dict'))
    if _labels_dict is None:
        _labels_dict = {}
    _labels_list = [_key for _key, _val in _labels_dict.items()]
    return _labels_list, _labels_dict


def redis_has_label(_label) -> bool:
    _labels_list, _labels_dict = redis_get_labels_detail()
    _labels_list: list = _labels_list
    _labels_dict: dict = _labels_dict
    _has_label = _labels_list.__contains__(_label)
    return _has_label


def redis_fuzzy_search_label(_label) -> bool:
    _labels_list, _labels_dict = redis_get_labels_detail()
    _labels_list: list[str] = _labels_list
    _labels_dict: dict = _labels_dict
    for _label_name in _labels_list:
        if _label_name.__contains__(_label):
            return True
    return False


def redis_mouse_left_click_if_has_label(_label) -> bool:
    _labels_list, _labels_dict = redis_get_labels_detail()
    _labels_list: list = _labels_list
    _labels_dict: dict = _labels_dict
    _has_label = _labels_list.__contains__(_label)
    if _has_label:
        _game_x, _game_y = _labels_dict[_label]['label_box_center']
        _window_x, _window_y = get_absolute_window_rect(WINDOW_HWND, _game_x, _game_y)
        pydirectinput.moveTo(_window_x, _window_y)
        mouse_left_click()
        time.sleep(0.3)
    return _has_label


def redis_get_skill(skill_key) -> bool:
    _skill = REDIS_CONN.hget('skill', skill_key)
    _skill_ok = _skill == b'Y'
    return _skill_ok


def wait_label_exists(_label_list: list, _wait_second_limit=10):
    # 等待界面加载loading
    _start_time = time.time()
    while True:
        time.sleep(0.5)
        if time.time() - _start_time > _wait_second_limit:
            print('loading too long, skip')
            return
        for _label in _label_list:
            if redis_has_label('town_play_quest_icon_gray'):
                # print('loading complete')
                return None


def wait_loading(wait_second_limit=10):
    # 等待界面加载loading
    _label_list = ['town_play_quest_icon_gray', 'town_play_quest_icon_light']
    wait_label_exists(_label_list, wait_second_limit)


def redis_get_all_role_config_key():
    # 从redis中读取配置
    _redis_key = "V3_ALL_ROLE_CONFIG_"
    _today_str = time.strftime("%Y-%m-%d", time.localtime(time.time() - 24 * 3600))
    _today_redis_key = _redis_key + _today_str
    return _today_redis_key


def redis_get_one_role_config(_role_name) -> dict:
    _today_redis_key = redis_get_all_role_config_key()
    _exist = REDIS_CONN.exists(_today_redis_key)
    if _exist == 0:
        all_role_config_list = all_role_config.ALL_ROLE_CONFIG_LIST
        for one in all_role_config_list:
            _key = _today_redis_key
            _value = one['role_name']
            _map = json.dumps(one)
            REDIS_CONN.hset(_key, _value, _map)

    _redis_val = REDIS_CONN.hget(_today_redis_key, _role_name)
    if _redis_val is None:
        print(f'miss role=[{_role_name}] config')

    return json.loads(str(_redis_val, encoding='utf-8'))


def redis_set_one_role_config(_one_role_config: dict) -> None:
    _today_redis_key = redis_get_all_role_config_key()
    REDIS_CONN.hset(_today_redis_key, json.dumps(_one_role_config))


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

    print("*" * 50)


# 畅玩任务
def handle_town_play_quest():
    wait_loading()

    # 打开畅玩任务(畅玩任务图标的感叹号识别的不准确)
    if not redis_has_label('town_play_quest_ui_header'):
        redis_mouse_left_click_if_has_label('town_play_quest_icon_gray')
    if not redis_has_label('town_play_quest_ui_header'):
        redis_mouse_left_click_if_has_label('town_play_quest_icon_light')

    # 领取奖励
    while redis_mouse_left_click_if_has_label('town_play_quest_claim_light'):
        pass

    # 关闭畅玩任务(如果识别不出来关闭按钮,再点一下畅玩任务图标)
    if not redis_mouse_left_click_if_has_label('town_play_quest_ui_close_button'):
        if redis_has_label('town_play_quest_ui_header'):
            redis_mouse_left_click_if_has_label('town_play_quest_icon_gray')
        if redis_has_label('town_play_quest_ui_header'):
            redis_mouse_left_click_if_has_label('town_play_quest_icon_light')


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


def to_select_role_ui():
    if redis_has_label('town_game_start_button'):
        return

    for i in range(3):
        if not redis_has_label('town_select_menu_select_role_light'):
            press_key(key_list=['esc'], back_swing=0.1)
            time.sleep(0.5)

    if not redis_mouse_left_click_if_has_label('town_select_menu_select_role_light'):
        print('can not find labels [town_select_menu_select_role_light]')
        sys.exit(-1)


# 进入副本
def to_dungeon_arbitrator():
    for i in range(3):
        if not redis_has_label('town_select_menu_teleportation_light'):
            press_key(key_list=['esc'], back_swing=0.1)

    redis_mouse_left_click_if_has_label('town_select_menu_teleportation_light')
    redis_mouse_left_click_if_has_label('dungeon_arbitrator_icon')
    for i in range(2):
        if not redis_mouse_left_click_if_has_label('dungeon_arbitrator_icon'):
            press_key(key_list=['right'], duration=3)


def handle_dungeon_common(_role_name):
    pass


def to_target_dungeon(_dungeon_name='dungeon_arbitrator'):
    if _dungeon_name == 'dungeon_arbitrator':
        to_dungeon_arbitrator()
    else:
        print(f'this is no [{_dungeon_name}]')


def play_one_role(_role_name):
    _one_role_config = redis_get_one_role_config(_role_name)
    _role_name = _one_role_config.get('role_name')
    _role_status = _one_role_config.get('role_status')
    _role_xy = _one_role_config.get('role_xy')
    _handle_buff = _one_role_config.get('handle_buff')
    _handle_monster = _one_role_config.get('handle_monster')
    _handle_boss = _one_role_config.get('handle_boss')
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name}] start]')
    # 进入选择角色ui
    to_select_role_ui()
    wait_label_exists(['town_game_start_button'])
    # 选择角色
    _window_left, _window_top, _window_right, _window_bottom = get_relative_window_rect(WINDOW_HWND)
    _window_width = _window_right - _window_left
    _window_height = _window_bottom - _window_top
    _game_x_percent, _game_y_percent = _role_xy[0], _role_xy[1]
    _role_x = int(_window_left + _window_width * _game_x_percent)
    _role_y = int(_window_top + _window_height * _game_y_percent)
    pydirectinput.moveTo(_role_x, _role_y)
    mouse_left_double_click()
    # 畅玩任务,领取奖励
    handle_town_play_quest()
    # 进入目标副本
    to_dungeon_arbitrator()
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name}] end]')


if __name__ == '__main__':
    time.sleep(1)

    # 被其他窗口遮挡，调用后放到最前面
    win32gui.SetForegroundWindow(WINDOW_HWND)
    # 解决被最小化的情况
    win32gui.ShowWindow(WINDOW_HWND, win32con.SW_RESTORE)
    time.sleep(1)

    role_name_list = ['modao', 'naima01', 'nailuo', 'naima02', 'zhaohuan', 'saber', 'zhanfa', 'papading']
    for role_name in role_name_list:
        play_one_role(role_name)

    # handle_town_play_quest()
