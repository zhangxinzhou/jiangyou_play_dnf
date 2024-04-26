import unittest

from v1_dnf_arbitrator_auto_play import *


def test_role():
    role = DnfArbitratorRole001()
    role.role_play()


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
