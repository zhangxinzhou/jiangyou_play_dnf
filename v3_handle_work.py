# 处理工作
# 所谓工作简单的来说就将状态A处理成为状态B,以吃饭为例,将客人从饥饿状态处理成为吃饱饭状态
# is_ready 用来判断客人是不是饥饿转态
# is_finished 用来判断客人是不是吃饱饭状态
# do_work 是将is_ready,is_finished,your_code 组合起来实现一定的逻辑
# your_code 是处理状态的主要代码
import sys
from abc import ABCMeta, abstractmethod
import time
import datetime

# 等待loading等超时时间
WAITING_MAX_SECOND = 3
# 调试,打印执行到那个方法,方便观察卡在那个方法里面
PRINT_METHOD = True


def print_method_name(func):
    def wrapper(*args, **kwargs):
        _start_time = time.time()
        _result = func(*args, **kwargs)
        _cost = time.time() - _start_time
        if PRINT_METHOD:
            print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{str(func):<100}] cost=[{_cost:.2f}] s')
        return _result

    return wrapper


# 设想的工作流-未实现,先保存
# 处理工作
# 所谓工作简单的来说就将状态A处理成为状态B,以吃饭为例,将客人从饥饿状态处理成为吃饱饭状态
# is_ready 用来判断客人是不是饥饿转态
# is_finished 用来判断客人是不是吃饱饭状态
# do_work 是将is_ready,is_finished,your_code 组合起来实现一定的逻辑
# your_code 是处理状态的主要代码
class HandleWork(metaclass=ABCMeta):

    @classmethod
    def check_for_exit(cls):
        return False

    @classmethod
    def check_ready_to_work(cls):
        """
        判断是否满足工作条件,如果不满足就等待N秒(比如等待加载之类的操作)
        """
        return True

    @classmethod
    def check_before_work(cls):
        """
        工作之前判断下,工作是否已完成,如果已完成,无需工作,整个类就结束了
        如果没有完成,不需要等待N秒,因为大概率就是上游丢给你要处理的工作
        """
        return True

    @classmethod
    def check_after_work(cls):
        """
        工作完成后,判断工作是否已经完成.如果已完成,就结束了;如果未完成,则可能是加载等原因导致的,等待几秒后放行
        """
        return True

    @classmethod
    def is_ready(cls):
        return True

    @classmethod
    def is_finished(cls):
        return False

    @classmethod
    @abstractmethod
    def your_code(cls):
        pass

    @classmethod
    def check_work_ready(cls):
        """
        判断是否满足工作条件,如果不满足就等待N秒(比如等待加载之类的操作)
        """
        _start_time = time.time()
        while True:
            _cost = time.time() - _start_time
            if _cost > WAITING_MAX_SECOND:
                return True
            if cls.is_ready():
                return True

    @classmethod
    def check_work_finished_before_do_work(cls):
        """
        工作之前判断下,工作是否已完成,如果已完成,无需工作,整个类就结束了
        如果没有完成,不需要等待N秒,因为大概率就是上游丢给你要处理的工作
        """
        return cls.is_finished()

    @classmethod
    def check_work_finished_after_do_work(cls):
        """
        工作完成后,判断工作是否已经完成.如果已完成,就结束了;如果未完成,则可能是加载等原因导致的,等待几秒后放行
        """
        _start_time = time.time()
        while True:
            _cost = time.time() - _start_time
            if _cost > WAITING_MAX_SECOND:
                return True
            if cls.is_finished():
                return True

    @classmethod
    @print_method_name
    def do_work(cls):
        if cls.check_work_finished_before_do_work():
            # 工作已经完成,退出
            return
        if not cls.check_work_ready():
            # 不满足工作条件,退出
            print(
                f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '
                f'[{cls.__name__}] can not do work, exit')
            sys.exit(-1)

        # 执行你编写的逻辑
        cls.your_code()

        # 检查工作是否完成
        if cls.check_work_finished_after_do_work():
            return
