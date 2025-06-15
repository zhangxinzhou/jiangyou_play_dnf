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

import v4_all_role_config as role_config

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
PRINT_METHOD = False
PRINT_KEY_PRESS = False

# 重试次数
RETRY_TIMES = 10
# 休眠时间
SLEEP_SECOND = 0.2


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
REDIS_POOL = redis.ConnectionPool(host='localhost', port=6379)
REDIS_CONN = redis.Redis(connection_pool=REDIS_POOL, decode_responses=True)


def press_key(_key_list: list, _duration=0.0, _back_swing=0.2) -> None:
    """
    :param _key_list: 按键
    :param _duration: 按键持续时间,单位秒
    :param _back_swing: 技能后摇时间,单位秒
    :return:
    """
    if PRINT_KEY_PRESS:
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
    time.sleep(SLEEP_SECOND)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(SLEEP_SECOND)


def mouse_left_double_click() -> None:
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(SLEEP_SECOND)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(SLEEP_SECOND)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 100, 100)
    time.sleep(SLEEP_SECOND)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 100, 100)
    time.sleep(SLEEP_SECOND)


def mouse_right_click() -> None:
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 100, 100)
    time.sleep(SLEEP_SECOND)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 100, 100)
    time.sleep(SLEEP_SECOND)


def get_window_hand() -> None:
    _window_title = r'地下城与勇士：创新世纪'
    _window_hwnd = win32gui.FindWindow(None, _window_title)
    if _window_title is None or _window_hwnd == 0:
        print(f"can not find game [{_window_title}]")
        sys.exit()
    return _window_hwnd


def get_relative_window_rect(_hwnd):
    _function = ctypes.windll.dwmapi.DwmGetWindowAttribute
    rect = ctypes.wintypes.RECT()
    _function(ctypes.wintypes.HWND(_hwnd), ctypes.wintypes.DWORD(9), ctypes.byref(rect), ctypes.sizeof(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def get_absolute_window_rect(_hwnd, _game_x, _game_y):
    _window_left, _window_top, _window_right, _window_bottom = get_relative_window_rect(_hwnd)
    return _window_left + _game_x, _window_top + _game_y


# 窗口/游戏句柄
WINDOW_HWND = get_window_hand()
# 游戏高度,宽度,坐标等
WINDOW_LEFT, WINDOW_TOP, WINDOW_RIGHT, WINDOW_BOTTOM = get_relative_window_rect(WINDOW_HWND)
WINDOW_WIDTH = WINDOW_RIGHT - WINDOW_LEFT
WINDOW_HEIGHT = WINDOW_BOTTOM - WINDOW_TOP


def redis_get_last_n_labels_detail() -> (list, dict):
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
        time.sleep(SLEEP_SECOND)

    _last_n_labels = json.loads(REDIS_CONN.get('last_n_labels_detail_dict'))
    return _last_n_labels


def redis_get_labels_detail() -> (list, dict):
    _last_n_labels = redis_get_last_n_labels_detail()
    _labels_dict: dict = _last_n_labels[0]
    if _labels_dict is None:
        _labels_dict = {}
    _labels_list = [_key for _key, _val in _labels_dict.items()]
    return _labels_list, _labels_dict


def redis_has_label(_label) -> bool:
    _last_n_labels = redis_get_last_n_labels_detail()
    for _index, _one in enumerate(_last_n_labels):
        # 只关注最近3帧
        if _index > 2:
            return False
        _labels_dict: dict = _one
        if _labels_dict is None:
            _labels_dict = {}
        _labels_list = [_key for _key, _val in _labels_dict.items()]

        _has_label = _labels_list.__contains__(_label)
        if _has_label:
            return True
    return False


# 模糊搜索label
def redis_fuzzy_search_label(_label) -> bool:
    _last_n_labels = redis_get_last_n_labels_detail()
    for _index, _one in enumerate(_last_n_labels):
        # 只关注最近3帧
        if _index > 2:
            return False
        _labels_dict: dict = _one
        if _labels_dict is None:
            _labels_dict = {}
        _labels_list = [_key for _key, _val in _labels_dict.items()]

        for _label_name in _labels_list:
            if _label_name.__contains__(_label):
                return True
    return False


def redis_mouse_left_click_if_has_label(_label) -> bool:
    _last_n_labels = redis_get_last_n_labels_detail()
    for _index, _one in enumerate(_last_n_labels):
        # 只关注最近3帧
        if _index > 2:
            return False
        _labels_dict: dict = _one
        if _labels_dict is None:
            _labels_dict = {}
        _labels_list = [_key for _key, _val in _labels_dict.items()]

        _has_label = _labels_list.__contains__(_label)
        if _has_label:
            _game_x, _game_y = _labels_dict[_label][0]['label_box_center']
            _window_x, _window_y = get_absolute_window_rect(WINDOW_HWND, _game_x, _game_y)
            pydirectinput.moveTo(_window_x, _window_y)
            mouse_left_click()
            time.sleep(SLEEP_SECOND)
        return _has_label
    return False


def redis_get_skill_able(skill_key) -> bool:
    _skill = REDIS_CONN.hget('skill', skill_key)
    _skill_ok = _skill == b'Y'
    _lock_key = f'lock_{skill_key}'
    _lock_able = REDIS_CONN.get(_lock_key) is None
    if _skill_ok and REDIS_CONN.get and _lock_able:
        REDIS_CONN.set(_lock_key, 1, ex=1)
    return _skill_ok


def wait_all_skill_enable(_wait_second_limit=3):
    # 等待界面加载loading
    _start_time = time.time()
    while True:
        time.sleep(SLEEP_SECOND)
        _cost = time.time() - _start_time
        if _cost > _wait_second_limit:
            print(f'wait wait_all_skill_enable [{_cost:.2f}] s, skip')
            return
        if redis_get_skill_able('all'):
            return


def redis_get_all_role_config_key():
    # 从redis中读取配置
    _redis_key = "V3_ALL_ROLE_DUNGEON_CONFIG_"
    _today_str = time.strftime("%Y-%m-%d", time.localtime(time.time() - 8 * 3600))
    _today_redis_key = _redis_key + _today_str
    return _today_redis_key


def redis_get_one_role_dungeon_config(_role_name) -> dict:
    _today_redis_key = redis_get_all_role_config_key()
    _exist = REDIS_CONN.exists(_today_redis_key)
    _one_role_dungeon_list = role_config.ALL_ROLE_DUNGEON_DICT.get(_role_name)
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


def print_red_color(text: str):
    print('\033[1;31;40m' + text + '\033[0m')


def wait_detection_working():
    _start_time = time.time()
    while True:
        _cost = time.time() - _start_time
        _detection_working = REDIS_CONN.get('v3_detection_working')
        if _cost > 120:
            print_red_color(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] waiting [{_cost}]s, exit')
            sys.exit(-1)
        if _detection_working == b'1':
            print_red_color(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] detection is starting')
        if _detection_working == b'2':
            print_red_color(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] detection is working')
            break
        # 等待
        time.sleep(SLEEP_SECOND)


def print_method_name(func):
    def wrapper(*args, **kwargs):
        _start_time = time.time()
        _f_name = func.__name__
        _result = func(*args, **kwargs)
        _cost = time.time() - _start_time
        if PRINT_METHOD:
            print(f'execute function [{_f_name:<30}] cost=[{_cost:.2f}] s')
        return _result

    return wrapper


#######################################################
# utils END
#######################################################


# 畅玩任务
@print_method_name
def handle_town_play_quest():
    # 等待loading
    wait_all_skill_enable()

    # 打开畅玩任务(畅玩任务图标的感叹号识别的不准确)
    for i in range(3):
        if not redis_has_label('town_play_quest_ui_header'):
            press_key(_key_list=['f2'])
            time.sleep(0.1)
            break

    # 领取任务
    for i in range(3):
        if redis_mouse_left_click_if_has_label('town_play_quest_claim_all_light'):
            press_key(_key_list=['space'])
            time.sleep(0.1)
            pass

    # 关闭畅玩任务
    for i in range(3):
        if redis_has_label('town_play_quest_ui_header'):
            press_key(_key_list=['f2'])
            time.sleep(0.1)
            break


@print_method_name
def to_select_role_ui():
    # 存在游戏开始菜单,结束
    if redis_has_label('town_game_start_button'):
        return

    # 检测到活动的关闭按钮,就点击关闭按钮
    for i in range(RETRY_TIMES):
        redis_mouse_left_click_if_has_label('town_common_close_button')

    # 按esc出现选择菜单
    for i in range(RETRY_TIMES):
        if not redis_has_label('town_select_menu_select_role_light'):
            press_key(_key_list=['esc'], _back_swing=0.1)
            time.sleep(SLEEP_SECOND)

    # 左键单击选择角色按钮
    for i in range(RETRY_TIMES):
        if redis_mouse_left_click_if_has_label('town_select_menu_select_role_light'):
            time.sleep(SLEEP_SECOND)
            break

    # 存在游戏开始菜单,结束
    for i in range(RETRY_TIMES):
        if redis_has_label('town_game_start_button'):
            return

    print('can not find labels [town_game_start_button]')
    sys.exit(-1)


# 进入副本
@print_method_name
def to_dungeon_admirers():
    _dungeon_icon = 'dungeon_admirers_icon'

    # 如有esa菜单,关闭
    if redis_has_label('town_select_menu_ui_header'):
        press_key(_key_list=['esc'], _back_swing=0.5)

    # 按键n打开世界地图，用page down到地图收藏
    press_key(_key_list=['n'])
    time.sleep(0.1)
    press_key(_key_list=['pagedown'])

    # 传送到终末崇拜者
    for i in range(RETRY_TIMES):
        time.sleep(SLEEP_SECOND)
        if redis_mouse_left_click_if_has_label(_dungeon_icon):
            time.sleep(SLEEP_SECOND)
            break
    time.sleep(2)

    # 移动到第一个入口（蓝色/城镇）
    press_key(_key_list=['right'], _duration=0.2)
    press_key(_key_list=['left'], _duration=1)

    # 点击副本icon
    for i in range(3):
        redis_mouse_left_click_if_has_label(_dungeon_icon)
        time.sleep(SLEEP_SECOND)

    # 不满足进入条件,如:门票,战斗力
    if redis_has_label('dungeon_common_entry_disable'):
        # 不满足进入条件,退出到城镇
        press_key(_key_list=['f12'], _duration=0.5)
        print_red_color(
            f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] identify label=[dungeon_common_entry_disable]')
        return False
    # 疲劳不满足,无法进入副本
    if redis_has_label('dungeon_common_pl_disable'):
        # 不满足进入条件,退出到城镇
        press_key(_key_list=['f12'], _duration=0.5)
        print_red_color(
            f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] identify label=[dungeon_common_pl_disable]')
        return False
    # 成功,进入副本
    return True


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
    _handle_buff = role_config.ALL_ROLE_SKILL_DICT.get(_role_name).get('handle_buff')
    wait_all_skill_enable()
    time.sleep(SLEEP_SECOND)
    handle_key_list(_handle_buff)


# 识别到商店,维修武器,关闭商店
# 识别到道具,捡道具
# 识别到
# true 可以继续挑战,false 无法继续挑战
@print_method_name
def handle_dungeon_stage_end(_role_name, _is_finish=False) -> bool:
    if redis_has_label('dungeon_common_continue_box') or redis_has_label('dungeon_common_shop_box'):
        # 数字0 移动物品 捡东西
        time.sleep(2)
        press_key(_key_list=['left'], _duration=0.5)
        time.sleep(1)
        press_key(_key_list=['0'], _back_swing=0.5)
        # 拾取物品1
        wait_all_skill_enable()
        for _i in range(20):
            press_key(_key_list=['x'])

    # 再次确认关闭商店
    if redis_has_label('dungeon_common_shop_box'):
        press_key(_key_list=['esc'], _back_swing=0.5)
    # 如有esa菜单,关闭
    if redis_has_label('town_select_menu_ui_header'):
        press_key(_key_list=['esc'], _back_swing=0.5)

    for i in range(3):
        if _is_finish:
            press_key(_key_list=['f12'], _back_swing=2)
            return False
        elif redis_has_label('dungeon_common_continue_gray'):
            print_red_color(
                f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] identify label=[dungeon_common_continue_gray]')
            press_key(_key_list=['f12'], _back_swing=2)
            return False
        elif redis_has_label('dungeon_common_continue_normal'):
            press_key(_key_list=['f10'], _back_swing=2)
            return True

    # 终结
    if redis_has_label('dungeon_common_arrow'):
        return True

    press_key(_key_list=['f12'], _back_swing=2)
    return False


@print_method_name
def role_run():
    # 先判断是否满足run的条件
    _exit_fuzzy_label_list = ['monster', 'boss']
    _exit_precise_label_list = ['dungeon_common_continue_box', 'dungeon_common_shop_box']
    for _label_name in _exit_precise_label_list:
        if redis_has_label(_label_name):
            return
    for _label_name in _exit_fuzzy_label_list:
        if redis_fuzzy_search_label(_label_name):
            return

    # 开始跑
    pydirectinput.press('right')
    time.sleep(SLEEP_SECOND)
    pydirectinput.keyDown('right')
    # 结束跑
    _start_time = time.time()
    while True:
        time.sleep(SLEEP_SECOND)
        # # 如果有移动箭头的提示，继续run
        # if redis_has_label('dungeon_common_arrow'):
        #     break
        if time.time() - _start_time > 5:
            pydirectinput.keyUp('right')
            return
        for _label_name in _exit_precise_label_list:
            if redis_has_label(_label_name):
                pydirectinput.keyUp('right')
                return
        for _label_name in _exit_fuzzy_label_list:
            if redis_fuzzy_search_label(_label_name):
                pydirectinput.keyUp('right')
                return


@print_method_name
def face_to_monster_or_boss():
    _last_n_labels = redis_get_last_n_labels_detail()
    for _index, _one in enumerate(_last_n_labels):
        # 只关注最近3帧
        if _index > 2:
            return
        _labels_dict: dict = _one
        if _labels_dict is None:
            _labels_dict = {}
        _labels_list = [_key for _key, _val in _labels_dict.items()]

        # 如果找不到角色,就假设角色在中间
        _role_x, _role_y = WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.5
        if _labels_list.__contains__('town_role'):
            _role_x, _role_y = _labels_dict['town_role'][0]['label_box_center']

        for _label_name in _labels_list:
            if _label_name.__contains__('monster') or _label_name.__contains__('boss'):
                _monster_x, _monster_y = _labels_dict[_label_name][0]['label_box_center']
                _distance = _role_x - _monster_x
                _key_list = ['left'] if _distance > 0 else ['right']
                _duration = 0.2 if abs(_distance) > 200 else 0.0
                press_key(_key_list=_key_list, _duration=_duration, _back_swing=0.2)
                return


@print_method_name
def handle_monster(_role_name):
    _skill_list = role_config.ALL_ROLE_SKILL_DICT.get(_role_name).get('handle_monster')
    for _skill_one in _skill_list:
        _skill_key = _skill_one.get('key_list')[0]
        if redis_get_skill_able(_skill_key):
            press_key(_key_list=_skill_one.get('key_list'),
                      _duration=_skill_one.get('duration'),
                      _back_swing=_skill_one.get('back_swing'))
            time.sleep(0.1)
            return


@print_method_name
def handle_boss(_role_name):
    _skill_list = role_config.ALL_ROLE_SKILL_DICT.get(_role_name).get('handle_boss')
    _count = 0
    for _skill_one in _skill_list:
        _skill_key = _skill_one.get('key_list')[0]
        if redis_get_skill_able(_skill_key):
            press_key(_key_list=_skill_one.get('key_list'),
                      _duration=_skill_one.get('duration'),
                      _back_swing=_skill_one.get('back_swing'))
            time.sleep(0.1)
            _count += 1

    if _count == 0:
        handle_monster(_role_name)


@print_method_name
def handle_dungeon_stage_clear(_role_name):
    _start_time = time.time()
    while True:
        # 刷图超过60秒放一次大招
        _cost = time.time() - _start_time
        if _cost > 60:
            face_to_monster_or_boss()
            handle_boss(_role_name)
        # 退出
        if redis_has_label('dungeon_common_shop_box') or redis_has_label('dungeon_common_continue_box'):
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
def handle_dungeon_one_round(_role_name, _is_finish=False, _round=0) -> bool:
    # 上buff
    if _round == 0:
        handle_dungeon_stage_start(_role_name)
    # 刷图
    handle_dungeon_stage_clear(_role_name)
    # 关卡结束
    _is_continue = handle_dungeon_stage_end(_role_name, _is_finish)
    # 若检测到活动的关闭按钮,就点击关闭按钮
    if not _is_continue:
        for i in range(RETRY_TIMES):
            redis_mouse_left_click_if_has_label('town_common_close_button')
    return _is_continue


@print_method_name
def handle_dungeon_all_round(_role_name):
    _one_role_dungeon_list = redis_get_one_role_dungeon_config(_role_name)
    print("*" * 100)
    print(_one_role_dungeon_list)
    for _one_role_dungeon in _one_role_dungeon_list:
        _dungeon_name = _one_role_dungeon.get("dungeon_name")
        _dungeon_status = _one_role_dungeon.get("dungeon_status")
        _dungeon_round = _one_role_dungeon.get("dungeon_round")

        if _dungeon_status == 'todo' and _dungeon_round > 0:
            # 进入目标副本
            _entry_able = to_dungeon_admirers()
            if not _entry_able:
                print(
                    f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] dungeon_name=[{_dungeon_name:<20}] can not enter')
                # 到下一个for循环
                continue
            _MAX_ROUND = _dungeon_round
            for _round in range(_MAX_ROUND):
                _start_time = time.time()
                _is_finish = _round + 1 == _MAX_ROUND
                _is_continue = handle_dungeon_one_round(_role_name, _is_finish, _round)
                _cost = time.time() - _start_time
                print(
                    f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] dungeon_name=[{_dungeon_name:<20}] round=[{_round + 1:>02}/{_MAX_ROUND:>02}] cost=[{_cost:.2f}] s')
                if not _is_continue:
                    # 到下一个for循环
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
                f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] dungeon_name=[{_dungeon_name:<20}] has done, skip')


# 等待交易保护结束,关闭活动提醒页面
def wait_transaction_protect_end():
    # 等待交易保护icon消失
    _start_time = time.time()
    while True:
        _cost = time.time() - _start_time
        _has_transaction_protection_icon = redis_has_label('town_transaction_protection_icon')
        if _cost > 60:
            print_red_color(
                f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] wait 60s, go on')
            return
        if _has_transaction_protection_icon:
            print_red_color(
                f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] detection town_transaction_protection_icon, wait 5s')
        else:
            print_red_color(
                f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] do not detection town_transaction_protection_icon, go on')
            return
        time.sleep(5)


@print_method_name
def play_one_role(_role_index, _role_name):
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] start')
    # 开始时间
    _start_time = time.time()
    # 选择角色
    select_one_role(_role_name)
    wait_all_skill_enable()
    # 检测到活动的关闭按钮,就点击关闭按钮
    for i in range(RETRY_TIMES):
        redis_mouse_left_click_if_has_label('town_common_close_button')
    # 等待交易保护结束
    if _role_index == 0:
        wait_transaction_protect_end()
    # 刷图
    handle_dungeon_all_round(_role_name)
    # 领取奖励
    wait_all_skill_enable()
    # 畅玩任务,领取奖励
    # handle_town_play_quest()
    _cost = time.time() - _start_time
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] end')
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}] cost=[{_cost:.2f}] s')
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] role=[{_role_name:<15}]', "*" * 50)


# 选择角色
def select_one_role(_role_name):
    # 获取角色配置
    _one_role_skill_config = role_config.ALL_ROLE_SKILL_DICT.get(_role_name)
    _role_xy = _one_role_skill_config.get('role_xy')
    # 进入选择角色ui
    to_select_role_ui()
    # 选择角色
    _game_x_percent, _game_y_percent = _role_xy[0], _role_xy[1]
    _role_x = int(WINDOW_LEFT + WINDOW_WIDTH * _game_x_percent)
    _role_y = int(WINDOW_TOP + WINDOW_HEIGHT * _game_y_percent)
    pydirectinput.moveTo(_role_x, _role_y)
    mouse_left_double_click()


@print_method_name
def play():
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] program start')
    # 开始时间
    _start_time = time.time()
    time.sleep(SLEEP_SECOND)

    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] waiting detection working')
    wait_detection_working()

    # 被其他窗口遮挡，调用后放到最前面
    win32gui.SetForegroundWindow(WINDOW_HWND)
    # 解决被最小化的情况
    win32gui.ShowWindow(WINDOW_HWND, win32con.SW_RESTORE)
    time.sleep(SLEEP_SECOND)

    role_name_list = ["modao", "zhanfa", "zhaohuan", "yuansu", "nailuo", "naima01", "naima02", "naima03", "saber",
                      "papading"]
    # role_name_list = ["yuansu"]
    # =============================play开始===============================
    for role_index, role_name in enumerate(role_name_list):
        play_one_role(role_index, role_name)

    # 畅玩任务,领取奖励
    # for role_index, role_name in enumerate(role_name_list):
    #     select_one_role(role_name)
    #     wait_all_skill_enable()
    #     handle_town_play_quest()

    # =============================play开始===============================

    # 计算耗时
    _cost = time.time() - _start_time
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] program end')
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] cost=[{_cost:.2f}] s')


@print_method_name
def single_method_test():
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] test start')
    # 开始时间
    _start_time = time.time()
    time.sleep(SLEEP_SECOND)

    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] waiting detection working')
    wait_detection_working()

    # 被其他窗口遮挡，调用后放到最前面
    win32gui.SetForegroundWindow(WINDOW_HWND)
    # 解决被最小化的情况
    win32gui.ShowWindow(WINDOW_HWND, win32con.SW_RESTORE)
    time.sleep(SLEEP_SECOND)

    # =============================待测试的单个方案===============================
    to_dungeon_admirers()
    # =============================待测试的单个方案===============================

    # 计算耗时
    _cost = time.time() - _start_time
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] test end')


if __name__ == '__main__':
    play()
    # single_method_test()
