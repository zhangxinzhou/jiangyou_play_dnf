from abc import ABCMeta, abstractmethod, ABC
from datetime import datetime

from pynput import keyboard

from v0_dnf_arbitrator_auto_play_utils import *

# 关闭安全模式
pyautogui.FAILSAFE = False
# 延迟设置
pyautogui.PAUSE = 0.05
# 找不到图片不要抛异常
pyautogui.useImageNotFoundException(False)
# 关闭安全模式
pydirectinput.FAILSAFE = False
# 延迟设置,默认0.1
pydirectinput.PAUSE = 0.1


# 按f2键,程序将会退出,退出原理:pyautogui打开安全模式,并且将鼠标移动到(0,0)位置触发异常事件
def on_press(key):
    if key == keyboard.Key.f2:
        print(f"you press key [{key}], program will exit")
        pyautogui.FAILSAFE = True
        pyautogui.moveTo(0, 0)
        return False


listener = keyboard.Listener(on_press=on_press)
listener.start()


class DnfArbitratorCommonRole(metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.press_key = direct_press_key
        self.role_name = None
        self.round = 0
        self.max_round = 20
        self.round_time = time.time()
        self.total_time = time.time()
        self.has_fatigue_point = True

        # 周四打副本要留疲劳,周三要领深渊门票
        day_of_week = 1 + datetime.now().weekday()
        if day_of_week == 3:
            self.max_round = 20
        elif day_of_week == 4:
            self.max_round = 4

    def role_run(self, key='right', duration=2):
        self.press_key(key_list=[key, key], duration=duration)

    def role_walk(self, key='right', duration=2):
        self.press_key(key_list=[key], duration=duration)

    # 关卡开始的操作,如上buff
    @abstractmethod
    def stage_start(self):
        pass

    @abstractmethod
    def stage_clear(self):
        pass

    # 关卡结束时的操作,如维修武器
    def stage_end(self) -> bool:
        # 维修武器
        self.press_key(key_list=['s', 'space'], back_swing=0.1)
        # 数字0 移动物品 捡东西
        self.press_key(key_list=['0'], back_swing=0.5)
        # 捡东西
        for _i in range(15):
            self.press_key(key_list=['x'])
        # 关闭维修商店
        self.press_key(key_list=['esc'], back_swing=0.5)
        # 判断是否还有疲劳
        has_no_point = has_no_fatigue_point()
        if has_no_point or not self.has_fatigue_point:
            # 返回城镇,然后等待五秒
            self.press_key(key_list=['f12'], back_swing=5)
            self.has_fatigue_point = False
        else:
            # 再次挑战,然后等待5秒
            self.press_key(key_list=['f10'], back_swing=5)
            self.has_fatigue_point = True

    def role_play(self) -> bool:
        while self.has_fatigue_point:
            if self.round >= self.max_round:
                self.has_fatigue_point = False
                break
            self.round += 1
            print(f'role [{self.role_name}], round [{self.round:>2}/{self.max_round:>2}] start')
            self.stage_start()
            self.stage_clear()
            self.stage_end()
            round_cost = time.time() - self.round_time
            total_cost = time.time() - self.total_time
            self.round_time = time.time()
            print(
                f'role [{self.role_name}], round [{self.round:>2}/{self.max_round:>2}] end, '
                f'round_cost=[{round_cost:.2f}] s, total_cost=[{total_cost:.2f}] s')


# 角色001
class DnfArbitratorRole001(DnfArbitratorCommonRole, ABC):

    def __init__(self):
        super().__init__()
        self.role_name = 'r1_modao'

    # 关卡开始的操作,如上buff
    def stage_start(self):
        self.press_key(key_list=['up', 'right', 'space'], back_swing=0.1)

        self.press_key(key_list=['up', 'up', 'space'], back_swing=0.5)

        self.press_key(key_list=['down', 'up', 'space'], back_swing=0.1)

        self.press_key(key_list=['down'], duration=0.3, back_swing=0.1)

    def stage_clear(self):
        self.role_run()
        self.press_key(key_list=['w'], back_swing=0.1)

        self.role_run(duration=3)

        time.sleep(10)


# 角色002
class DnfArbitratorRole002(DnfArbitratorCommonRole, ABC):

    def __init__(self):
        super().__init__()
        self.role_name = 'r2_naima'

    # 关卡开始的操作,如上buff
    def stage_start(self):
        self.press_key(key_list=['right', 'right', 'space'], back_swing=0.1)

        self.press_key(key_list=['up', 'up', 'space'], back_swing=0.1)

        self.press_key(key_list=['down', 'left', 'space'], back_swing=0.1)

        self.press_key(key_list=['e'], duration=0.3, back_swing=0.1)

    def stage_clear(self):
        self.role_run(duration=1)
        self.press_key(key_list=['s'], back_swing=0.8)

        self.role_run(duration=1)
        self.press_key(key_list=['s'], back_swing=0.8)

        self.role_run(duration=1)
        self.press_key(key_list=['q', 'a'], back_swing=5)


class DnfArbitratorRole003(DnfArbitratorCommonRole, ABC):

    def __init__(self):
        super().__init__()
        self.role_name = 'r3_nailio'

    # 关卡开始的操作,如上buff
    def stage_start(self):
        self.press_key(key_list=['right', 'right', 'space'], back_swing=1)

        self.press_key(key_list=['up', 'up', 'space'], back_swing=0.5)

        self.press_key(key_list=['f'], back_swing=0.1)

    def stage_clear(self):
        self.role_run(duration=1)
        self.press_key(key_list=['f'], back_swing=0.8)

        self.role_run(duration=1)
        self.press_key(key_list=['f'], back_swing=0.8)

        self.role_run(duration=1)
        self.press_key(key_list=['a'], back_swing=1)
        self.press_key(key_list=['ctrl'], back_swing=10)


class DnfArbitratorRole004(DnfArbitratorCommonRole, ABC):

    def __init__(self):
        super().__init__()
        self.role_name = 'r4_naima'

    # 关卡开始的操作,如上buff
    def stage_start(self):
        self.press_key(key_list=['right', 'right', 'space'], back_swing=0.1)

        self.press_key(key_list=['up', 'up', 'space'], back_swing=0.1)

        self.press_key(key_list=['down', 'left', 'space'], back_swing=0.1)

        self.press_key(key_list=['e'], duration=0.3, back_swing=0.1)

    def stage_clear(self):
        self.role_run(duration=1.2)
        self.press_key(key_list=['s'], back_swing=0.8)

        self.role_run(duration=1.2)
        self.press_key(key_list=['s'], back_swing=0.8)

        self.role_run(duration=1.5)
        self.press_key(key_list=['q', 'a'], back_swing=5)


class DnfArbitratorRole005(DnfArbitratorCommonRole, ABC):

    def __init__(self):
        super().__init__()
        self.role_name = 'r5_zhaohuan'

    # 关卡开始的操作,如上buff
    def stage_start(self):
        self.press_key(key_list=['q'], back_swing=2)

        self.press_key(key_list=['r'], back_swing=0.5)

        self.press_key(key_list=['t'], back_swing=0.5)

        self.press_key(key_list=['up', 'right', 'up', 'space'], back_swing=0.5)

        self.press_key(key_list=['e'], back_swing=0.5)

    def stage_clear(self):
        self.role_run(duration=8)

        self.press_key(key_list=['y'], back_swing=8)


class DnfArbitratorRole006(DnfArbitratorCommonRole, ABC):

    def __init__(self):
        super().__init__()
        self.role_name = 'r6_saber'

    # 关卡开始的操作,如上buff
    def stage_start(self):
        self.press_key(key_list=['q', 'left'], back_swing=0.1)

        self.press_key(key_list=['right', 'right', 'space'], back_swing=0.5)

        self.press_key(key_list=['a'], duration=2, back_swing=0.1)

    def stage_clear(self):
        self.role_run()
        self.press_key(key_list=['s'], duration=0.8, back_swing=0.1)

        self.role_run()
        self.press_key(key_list=['f'], duration=1, back_swing=0.5)

        self.role_run()
        self.press_key(key_list=['y'], back_swing=8)


class DnfArbitratorRole007(DnfArbitratorCommonRole, ABC):
    def __init__(self):
        super().__init__()
        self.role_name = 'r7_zhanfa'

    # 关卡开始的操作,如上buff
    def stage_start(self):
        self.press_key(key_list=['right', 'right', 'space'], back_swing=0.5)

        self.press_key(key_list=['r'], duration=2, back_swing=0.1)

    def stage_clear(self):
        self.role_run()
        self.press_key(key_list=['g'], duration=0.8, back_swing=1)

        self.role_run()
        self.press_key(key_list=['h'], duration=1, back_swing=1)

        self.role_run()
        self.press_key(key_list=['t'], back_swing=8)


# 角色配置
ALL_ROLE_CONFIG = [
    {"role_agent": DnfArbitratorRole001(), "left": 2 / 8, "top": 1 / 3, "status": "todo", },
    {"role_agent": DnfArbitratorRole002(), "left": 3 / 8, "top": 1 / 3, "status": "todo", },
    {"role_agent": DnfArbitratorRole003(), "left": 4 / 8, "top": 1 / 3, "status": "todo", },
    {"role_agent": DnfArbitratorRole004(), "left": 5 / 8, "top": 1 / 3, "status": "todo", },
    {"role_agent": DnfArbitratorRole005(), "left": 6 / 8, "top": 1 / 3, "status": "todo", },
    {"role_agent": DnfArbitratorRole006(), "left": 1 / 8, "top": 2 / 3, "status": "todo", },
    {"role_agent": DnfArbitratorRole007(), "left": 2 / 8, "top": 2 / 3, "status": "todo", },
]


def play():
    time.sleep(1)

    window_hwnd = get_window_hand()
    # 被其他窗口遮挡，调用后放到最前面
    win32gui.SetForegroundWindow(window_hwnd)
    # 解决被最小化的情况
    win32gui.ShowWindow(window_hwnd, win32con.SW_RESTORE)
    time.sleep(3)

    # 开启大写锁定,防止输入法干扰
    direct_press_key(key_list=['capslock'], back_swing=0.1)

    for one_role_config in ALL_ROLE_CONFIG:
        # 到选择角色界面
        to_ui_role_select()
        time.sleep(5)

        # 切换成对应角色
        window_left, window_top, window_right, window_bottom = get_window_rect(window_hwnd)
        window_width = window_right - window_left
        window_height = window_bottom - window_top
        role_x = int(window_left + window_width * one_role_config['left'])
        role_y = int(window_top + window_height * one_role_config['top'])
        pyautogui.moveTo(x=role_x, y=role_y)
        mouse_left_double_click()
        time.sleep(5)

        # 判断是否有疲劳
        has_no_point = has_no_fatigue_point()
        if has_no_point:
            one_role_config['status'] = "done"
            continue

        move_to_arbitrator()

        role_agent: DnfArbitratorCommonRole = one_role_config['role_agent']
        print(f"role [{role_agent.role_name}] play start")
        play_start_time = time.time()
        role_agent.role_play()
        play_cost_time = time.time() - play_start_time
        print(f"role [{role_agent.role_name}] play end, play total cost [{play_cost_time:.2f}] s")


if __name__ == '__main__':
    play()
