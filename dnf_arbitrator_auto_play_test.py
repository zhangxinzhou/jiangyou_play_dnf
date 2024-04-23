import unittest

from dnf_arbitrator_auto_play import *


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
        role = DnfArbitratorRole001()
        role.role_play()

    def test_select_role(self):
        to_ui_role_select()

    def test_role_change(self):
        pass

    def test_to_arbitrator(self):
        move_to_arbitrator()

    def test_has_fatigue_point(self):
        print(has_no_fatigue_point())

    def test_play(self):
        play()
