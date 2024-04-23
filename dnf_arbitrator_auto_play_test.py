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

    def test_role001(self):
        role = DnfArbitratorRole001()
        role.role_play()

    def test_role002(self):
        role = DnfArbitratorRole002()
        role.role_play()

    def test_role003(self):
        role = DnfArbitratorRole003()
        role.role_play()

    def test_role004(self):
        role = DnfArbitratorRole004()
        role.role_play()

    def test_role005(self):
        role = DnfArbitratorRole005()
        role.role_play()

    def test_role006(self):
        role = DnfArbitratorRole006()
        role.role_play()

    def test_role007(self):
        role = DnfArbitratorRole007()
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
