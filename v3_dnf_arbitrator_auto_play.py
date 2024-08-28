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

import v3_all_role_config

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

# 调试,打印执行到那个方法,方便观察卡在那个方法里面
DEBUG_MODE = False


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


def press_key(_key_list: list, _duration=0.0, _back_swing=0.3) -> None:
    """
    :param _key_list: 按键
    :param _duration: 按键持续时间,单位秒
    :param _back_swing: 技能后摇时间,单位秒
    :return:
    """
    if DEBUG_MODE:
        print(f"_key_list={str(_key_list):<30},_duration={str(_duration):<5},_back_swing={str(_back_swing):<5}")
    key_list_len = len(_key_list)
    if key_list_len <= 0:
        raise Exception("key_list must not be empty!")
    if _duration is None:
        _duration = 0.0
    if _back_swing is None:
        _back_swing = 0.3

    if _duration <= 0.0:
        pydirectinput.press(_key_list)
    else:
        last_key = _key_list[-1]
        other_key_list = _key_list[:-1]
        if len(other_key_list) > 0:
            pydirectinput.press(other_key_list)
        pydirectinput.keyDown(last_key)
        time.sleep(_duration)
        pydirectinput.keyUp(last_key)

    # 休眠后摇时间
    time.sleep(_back_swing)


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
    # 暂停和退出控制
    global PROGRAM_EXIT
    global PROGRAM_PAUSE
    if PROGRAM_EXIT:
        print("program exit.")
        sys.exit(-1)
    while PROGRAM_PAUSE:
        if PROGRAM_EXIT:
            print("program exit.")
            sys.exit(-1)
        print("program pause...")
        time.sleep(1)

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


def redis_get_skill_able(skill_key) -> bool:
    _skill = REDIS_CONN.hget('skill', skill_key)
    _skill_ok = _skill == b'Y'
    _lock_key = f'lock_{skill_key}'
    _lock_able = REDIS_CONN.get(_lock_key) is None
    if _skill_ok and REDIS_CONN.get and _lock_able:
        REDIS_CONN.set(_lock_key, 1, ex=1)
    return _skill_ok


def wait_label_exists(_label_list: list, _wait_second_limit=10):
    # 等待界面加载loading
    _start_time = time.time()
    while True:
        time.sleep(0.5)
        _cost = time.time() - _start_time
        if _cost > _wait_second_limit:
            print(f'wait label [{_label_list}] [{_cost:.2f}] s, skip')
            return
        for _label in _label_list:
            if redis_has_label(_label):
                # print('loading complete')
                return


def wait_all_skill_enable(_wait_second_limit=3):
    # 等待界面加载loading
    _start_time = time.time()
    while True:
        time.sleep(0.5)
        _cost = time.time() - _start_time
        if _cost > _wait_second_limit:
            print(f'wait wait_all_skill_enable [{_cost:.2f}] s, skip')
            return
        if redis_get_skill_able('all'):
            return


def wait_loading(wait_second_limit=10):
    # 等待界面加载loading
    _label_list = ['town_play_quest_icon_gray', 'town_play_quest_icon_light']
    wait_label_exists(_label_list, wait_second_limit)


def redis_get_all_role_config_key():
    # 从redis中读取配置
    _redis_key = "V3_ALL_ROLE_DUNGEON_CONFIG_"
    _today_str = time.strftime("%Y-%m-%d", time.localtime(time.time() - 8 * 3600))
    _today_redis_key = _redis_key + _today_str
    return _today_redis_key


def redis_get_one_role_dungeon_config(_role_name) -> dict:
    _today_redis_key = redis_get_all_role_config_key()
    _exist = REDIS_CONN.exists(_today_redis_key)
    _one_role_dungeon_list = v3_all_role_config.ALL_ROLE_DUNGEON_DICT.get(_role_name)
    _key = _today_redis_key
    _value = _role_name
    _map = json.dumps(_one_role_dungeon_list)
    if _exist == 0:
        REDIS_CONN.hset(_key, _value, _map)
    _redis_val = REDIS_CONN.hget(_today_redis_key, _role_name)

    if _redis_val is None:
        REDIS_CONN.hset(_key, _value, _map)
    _redis_val = REDIS_CONN.hget(_today_redis_key, _role_name)

    return json.loads(str(_redis_val, encoding='utf-8'))


def redis_set_one_role_config(_one_role_config: dict) -> None:
    _today_redis_key = redis_get_all_role_config_key()
    REDIS_CONN.hset(_today_redis_key, json.dumps(_one_role_config))


def print_method_name(func):
    def wrapper(*args, **kwargs):
        _f_name = func.__name__
        if DEBUG_MODE:
            print(f'execute function [{_f_name:<30}]')
        _result = func(*args, **kwargs)
        return _result

    return wrapper


#######################################################
# utils END
#######################################################


# 畅玩任务
@print_method_name
def handle_town_play_quest():
    wait_all_skill_enable()

    # 打开畅玩任务(畅玩任务图标的感叹号识别的不准确)
    if not redis_has_label('town_play_quest_ui_header'):
        redis_mouse_left_click_if_has_label('town_play_quest_icon_gray')
    if not redis_has_label('town_play_quest_ui_header'):
        redis_mouse_left_click_if_has_label('town_play_quest_icon_light')

    # 领取奖励
    for i in range(10):
        if not redis_mouse_left_click_if_has_label('town_play_quest_claim_light'):
            break

    # 关闭畅玩任务(如果识别不出来关闭按钮,再点一下畅玩任务图标)
    if not redis_mouse_left_click_if_has_label('town_play_quest_ui_close_button'):
        if redis_has_label('town_play_quest_ui_header'):
            redis_mouse_left_click_if_has_label('town_play_quest_icon_gray')
        if redis_has_label('town_play_quest_ui_header'):
            redis_mouse_left_click_if_has_label('town_play_quest_icon_light')


@print_method_name
def to_select_role_ui():
    if redis_has_label('town_game_start_button'):
        return

    for i in range(3):
        if not redis_has_label('town_select_menu_select_role_light'):
            press_key(_key_list=['esc'], _back_swing=0.1)
            time.sleep(0.5)

    if not redis_mouse_left_click_if_has_label('town_select_menu_select_role_light'):
        print('can not find labels [town_select_menu_select_role_light]')
        sys.exit(-1)


# 进入副本
@print_method_name
def to_dungeon_arbitrator(_dungeon_icon):
    try_times = 3
    sleep_second = 0.3
    # esc打开菜单
    for i in range(try_times):
        time.sleep(sleep_second)
        if not redis_has_label('town_select_menu_teleportation_light'):
            press_key(_key_list=['esc'], _back_swing=0.1)

    # 点击传送阵
    for i in range(try_times):
        time.sleep(sleep_second)
        if redis_mouse_left_click_if_has_label('town_select_menu_teleportation_light'):
            break

    # 传送到目标副本区域
    for i in range(try_times):
        time.sleep(sleep_second)
        if redis_mouse_left_click_if_has_label(_dungeon_icon):
            break

    # 进入副本,选择进入的地下城,点击进入地下城
    for i in range(try_times):
        time.sleep(sleep_second)
        press_key(_key_list=['right'], _duration=2)
        if redis_mouse_left_click_if_has_label(_dungeon_icon):
            press_key(_key_list=['space'], _back_swing=0.1)
            break


@print_method_name
def handle_key_list(_key_list: list):
    if _key_list is None or len(_key_list) == 0:
        return
    for _one in _key_list:
        _one: dict = _one
        press_key(_key_list=_one.get('key_list'), _duration=_one.get('duration'), _back_swing=_one.get('back_swing'))


# 上buff
@print_method_name
def handle_dungeon_stage_start(_role_name):
    _handle_buff = v3_all_role_config.ALL_ROLE_SKILL_DICT.get(_role_name).get('handle_buff')
    wait_all_skill_enable()
    time.sleep(0.5)
    handle_key_list(_handle_buff)


# 识别到商店,维修武器,关闭商店
# 识别到道具,捡道具
# 识别到
# true 可以继续挑战,false 无法继续挑战
@print_method_name
def handle_dungeon_stage_end(_role_name, _is_finish=False) -> bool:
    # wait_label_exists(['dungeon_common_shop_box'])
    if redis_has_label('dungeon_common_shop_box'):
        # 维修武器
        press_key(_key_list=['s', 'space'], _back_swing=0.1)
        time.sleep(3)
        # 关闭商店
        press_key(_key_list=['esc'], _back_swing=0.5)
        # 数字0 移动物品 捡东西
        press_key(_key_list=['0'], _back_swing=0.5)
        # 捡东西(墙角检测不到物品,因此就这样吧)
        for _i in range(20):
            press_key(_key_list=['x'])

    # 再次确认关闭商店
    if redis_has_label('dungeon_common_shop_box'):
        press_key(_key_list=['esc'], _back_swing=0.5)

    if _is_finish:
        press_key(_key_list=['f12'], _back_swing=2)
        return False
    elif redis_has_label('dungeon_common_continue_gray'):
        press_key(_key_list=['f12'], _back_swing=2)
        return False
    elif redis_has_label('dungeon_common_continue_normal'):
        press_key(_key_list=['f10'], _back_swing=2)
        return True
    else:
        press_key(_key_list=['f12'], _back_swing=2)
        return False


@print_method_name
def role_run():
    # 退出条件
    if redis_fuzzy_search_label('monster') or redis_fuzzy_search_label(
            'boss') or redis_fuzzy_search_label(
        'star_box') or redis_has_label(
        'dungeon_common_shop_box' or redis_has_label('dungeon_common_continue_box')):
        return

    # 判断是否可以跑
    _start_time = time.time()
    _sleep_time = 0.2
    while True:
        time.sleep(_sleep_time)
        if time.time() - _start_time > 5:
            break
        if redis_get_skill_able('all'):
            break

    pydirectinput.press('right')
    time.sleep(_sleep_time)
    pydirectinput.keyDown('right')
    time.sleep(_sleep_time)
    while True:
        if redis_fuzzy_search_label('monster') or redis_fuzzy_search_label(
                'boss') or redis_fuzzy_search_label(
            'star_box') or redis_has_label(
            'dungeon_common_shop_box' or redis_has_label('dungeon_common_continue_box')):
            pydirectinput.keyUp('right')
            return
        time.sleep(_sleep_time)


@print_method_name
def face_to_monster_or_boss():
    _labels_list, _labels_dict = redis_get_labels_detail()
    _labels_list: list[str] = _labels_list
    _labels_dict: dict = _labels_dict
    if _labels_list.__contains__('town_role'):
        _role_x, _role_y = _labels_dict['town_role']['label_box_center']

        for _label_name in _labels_list:
            if _label_name.__contains__('monster'):
                _monster_x, _monster_y = _labels_dict[_label_name]['label_box_center']
                if _role_x - _monster_x > 0:
                    press_key(_key_list=['left'], _duration=0.1, _back_swing=0.2)
                else:
                    press_key(_key_list=['right'], _duration=0.1, _back_swing=0.2)
                return

        for _label_name in _labels_list:
            if _label_name.__contains__('boss'):
                _monster_x, _monster_y = _labels_dict[_label_name]['label_box_center']
                if _role_x - _monster_x > 0:
                    press_key(_key_list=['left'], _duration=0.1, _back_swing=0.2)
                else:
                    press_key(_key_list=['right'], _duration=0.1, _back_swing=0.2)
                return


@print_method_name
def handle_monster(_role_name):
    _skill_list = v3_all_role_config.ALL_ROLE_SKILL_DICT.get(_role_name).get('handle_monster')
    for _skill_one in _skill_list:
        _skill_key = _skill_one.get('key_list')[0]
        if redis_get_skill_able(_skill_key):
            press_key(_key_list=_skill_one.get('key_list'),
                      _duration=_skill_one.get('duration'),
                      _back_swing=_skill_one.get('back_swing'))
            time.sleep(0.5)
            return


@print_method_name
def handle_boss(_role_name):
    _skill_list = v3_all_role_config.ALL_ROLE_SKILL_DICT.get(_role_name).get('handle_boss')
    _count = 0
    for _skill_one in _skill_list:
        _skill_key = _skill_one.get('key_list')[0]
        if redis_get_skill_able(_skill_key):
            press_key(_key_list=_skill_one.get('key_list'),
                      _duration=_skill_one.get('duration'),
                      _back_swing=_skill_one.get('back_swing'))
            time.sleep(0.5)
            _count += 1

    if _count == 0:
        handle_monster(_role_name)


@print_method_name
def handle_dungeon_stage_clear(_role_name):
    while True:
        # 退出
        if redis_has_label('dungeon_common_shop_box'):
            return
        # 打怪
        elif redis_fuzzy_search_label('monster'):
            face_to_monster_or_boss()
            handle_monster(_role_name)
        # 打boss
        elif redis_fuzzy_search_label('boss'):
            face_to_monster_or_boss()
            handle_boss(_role_name)
        # 移动
        elif redis_has_label('dungeon_common_arrow'):
            role_run()
        else:
            role_run()


@print_method_name
def handle_dungeon_one_round(_role_name, _is_finish=False) -> bool:
    # 上buff
    handle_dungeon_stage_start(_role_name)
    # 刷图
    handle_dungeon_stage_clear(_role_name)
    # 关卡结束
    _is_continue = handle_dungeon_stage_end(_role_name, _is_finish)
    return _is_continue


@print_method_name
def handle_dungeon_all_round(_role_name):
    _one_role_dungeon_list = redis_get_one_role_dungeon_config(_role_name)
    for _one_role_dungeon in _one_role_dungeon_list:
        _dungeon_name = _one_role_dungeon.get("dungeon_name")
        _dungeon_icon = _one_role_dungeon.get("dungeon_icon")
        _dungeon_status = _one_role_dungeon.get("dungeon_status")
        _dungeon_round = _one_role_dungeon.get("dungeon_round")

        if _dungeon_status == 'todo' and _dungeon_round > 0:
            # 进入目标副本
            to_dungeon_arbitrator(_dungeon_icon)
            _MAX_ROUND = _dungeon_round
            for _round in range(_MAX_ROUND):
                _start_time = time.time()
                _is_finish = _round + 1 == _MAX_ROUND
                _is_continue = handle_dungeon_one_round(_role_name, _is_finish)
                _cost = time.time() - _start_time
                print(
                    f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] dungeon_name=[{_dungeon_name}] round=[{_round:>02}] cost=[{_cost:.2f}] s')
                if not _is_continue:
                    break
            # redis更新状态
            _one_role_dungeon['dungeon_status'] = 'done'
            _today_redis_key = redis_get_all_role_config_key()
            _key = _today_redis_key
            _value = _role_name
            _map = json.dumps(_one_role_dungeon_list)
            REDIS_CONN.hset(_key, _value, _map)

        else:
            print(
                f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] dungeon_name=[{_dungeon_name}] has done, skip')


@print_method_name
def to_target_dungeon(_dungeon_icon):
    if _dungeon_icon is not None:
        to_dungeon_arbitrator(_dungeon_icon=_dungeon_icon)
    else:
        print(f'_dungeon_icon can not be None, skip')


@print_method_name
def play_one_role(_role_name):
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] start')
    # 开始时间
    _start_time = time.time()
    # 获取角色配置
    _one_role_skill_config = v3_all_role_config.ALL_ROLE_SKILL_DICT.get(_role_name)
    _role_xy = _one_role_skill_config.get('role_xy')

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
    # 刷图
    handle_dungeon_all_round(_role_name)
    # 畅玩任务,领取奖励
    handle_town_play_quest()
    _cost = time.time() - _start_time
    print(
        f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] end, cost=[{_cost:.2f}] s')


@print_method_name
def play():
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] program start')
    # 开始时间
    _start_time = time.time()
    time.sleep(1)

    # 被其他窗口遮挡，调用后放到最前面
    win32gui.SetForegroundWindow(WINDOW_HWND)
    # 解决被最小化的情况
    win32gui.ShowWindow(WINDOW_HWND, win32con.SW_RESTORE)
    time.sleep(1)

    role_name_list = ["modao", "naima01", "nailuo", "naima02", "zhaohuan", "saber", "zhanfa", "papading", "naima03"]
    # =============================play开始===============================
    for role_name in role_name_list:
        play_one_role(role_name)
    # =============================play开始===============================

    # =============================测试开始===============================
    # 测试单个角色刷图
    # handle_dungeon_all_round('papading')
    # 测试单个角色
    # play_one_role('naima02')
    # 测试移动到地下城仲裁者
    # to_dungeon_arbitrator('dungeon_arbitrator_icon')
    # 测试移动到地下城缥缈店书库
    # to_dungeon_arbitrator('dungeon_library_icon')
    # =============================测试结束===============================

    # 计算耗时
    _cost = time.time() - _start_time
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] program end, cost=[{_cost:.2f}] s')


if __name__ == '__main__':
    play()
