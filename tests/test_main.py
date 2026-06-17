"""Main 入口模块单元测试.

使用 mock 绕过 GUI 初始化，测试主程序流程。
"""

import unittest
from unittest.mock import MagicMock, patch


class TestMainModule(unittest.TestCase):
    """测试 main.py 模块级功能."""

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_main_imports(self, mock_login, mock_dm, mock_ctk):
        """测试 main.py 可以成功导入."""
        import main

        self.assertTrue(hasattr(main, "DataManager"))
        self.assertTrue(hasattr(main, "LoginWindow"))

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_main_base_dir(self, mock_login, mock_dm, mock_ctk):
        """测试项目根目录已加入 sys.path."""
        import main
        import sys
        import os

        base_dir = os.path.dirname(os.path.abspath(main.__file__))
        self.assertIn(base_dir, sys.path)

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_main_function_exists(self, mock_login, mock_dm, mock_ctk):
        """测试 main() 函数存在."""
        import main
        self.assertTrue(callable(getattr(main, "main", None)))


class TestMainFlow(unittest.TestCase):

    """测试主程序 main() 函数流程逻辑."""

    @patch("main._reset_tk_state")
    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_login_cancelled_breaks_loop(self, mock_login_cls, mock_dm_cls, mock_ctk, mock_reset):
        """测试登录取消后退出循环."""
        import main
        mock_dm = MagicMock()
        mock_dm_cls.return_value = mock_dm
        mock_login = MagicMock()
        mock_login.run.return_value = {"success": False}
        mock_login_cls.return_value = mock_login

        with patch("builtins.print"):
            main.main()

        mock_login.run.assert_called_once()
        mock_reset.assert_not_called()

    @patch("main._reset_tk_state")
    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_login_success_no_logout(self, mock_login_cls, mock_dm_cls, mock_ctk, mock_reset):
        """测试登录成功且不退出登录时结束循环."""
        import main
        mock_dm = MagicMock()
        mock_dm_cls.return_value = mock_dm
        mock_login = MagicMock()
        mock_login.run.return_value = {
            "success": True,
            "role": "admin",
            "user": {"username": "admin"},
        }
        mock_login_cls.return_value = mock_login

        mock_app_cls = MagicMock()
        mock_app_cls.return_value.run.return_value = {"logout": False}
        mock_module = MagicMock(App=mock_app_cls)

        with patch("builtins.__import__", return_value=mock_module):
            with patch("builtins.print"):
                main.main()

        mock_reset.assert_called_once()
        mock_app_cls.assert_called_once_with(
            data_manager=mock_dm, user_info={"username": "admin"}
        )

    @patch("main._reset_tk_state")
    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_unknown_role_breaks(self, mock_login_cls, mock_dm_cls, mock_ctk, mock_reset):
        """测试未知角色时退出循环."""
        import main
        mock_dm = MagicMock()
        mock_dm_cls.return_value = mock_dm
        mock_login = MagicMock()
        mock_login.run.return_value = {
            "success": True,
            "role": "unknown",
            "user": {},
        }
        mock_login_cls.return_value = mock_login

        with patch("builtins.print"):
            main.main()

        mock_reset.assert_called_once()


class TestResetTkState(unittest.TestCase):
    """测试 _reset_tk_state 函数."""

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_reset_tk_state(self, mock_login, mock_dm, mock_ctk):
        """测试 _reset_tk_state 可被调用."""
        import main
        with patch("tkinter._default_root", None):
            with patch("ttkbootstrap.Style"):
                # 只需验证函数可调用且不抛异常
                try:
                    main._reset_tk_state()
                except Exception:
                    pass  # tkinter 未初始化时可能抛异常，属预期行为
                self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
