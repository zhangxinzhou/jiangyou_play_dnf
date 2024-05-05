import json
import unittest

from v1_dnf_arbitrator_auto_play import *


class PlayTest(unittest.TestCase):

    # TestCase基类方法,所有case执行之前自动执行
    @classmethod
    def setUpClass(cls) -> None:  # 1
        time.sleep(3)
        print()
        print("*" * 50, "class start", "*" * 50)

    # TestCase基类方法,所有case执行之后自动执行
    @classmethod
    def tearDownClass(cls) -> None:  # 2
        print("*" * 50, "class end", "*" * 50)
        print()

    def setUp(self) -> None:
        print()
        print("*" * 50, "method start", "*" * 50)

    def tearDown(self) -> None:
        print("*" * 50, "method end", "*" * 50)
        print()

    def test_role(self):
        role = zhanfa()
        role.role_play()

    def test_init_redis_val(self):
        ALL_ROLE_CONFIG = [
            {"role_class": "modao", "role_status": "done", },
            {"role_class": "naima01", "role_status": "done", },
            {"role_class": "nailuo", "role_status": "done", },
            {"role_class": "naima02", "role_status": "done", },
            {"role_class": "zhaohuan", "role_status": "done", },
            {"role_class": "saber", "role_status": "todo", },
            {"role_class": "zhanfa", "role_status": "todo", },
        ]
        redis_key = "ALL_ROLE_STATUS_" + time.strftime("%Y-%m-%d", time.localtime())
        redis_conn.set(name=redis_key, value=json.dumps(ALL_ROLE_CONFIG))

    def test_get_redis_val(self):
        redis_key = "ALL_ROLE_STATUS_" + time.strftime("%Y-%m-%d", time.localtime())
        redis_val = redis_conn.get(redis_key)
        l = json.loads(redis_val)
        for i in l:
            print(i)
