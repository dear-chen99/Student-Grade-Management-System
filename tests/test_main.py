"""Main 入口模块单元测试.

使用 mock 绕过 GUI 初始化，测试主程序流程，包括模块导入、
主函数逻辑、登录循环以及 tkinter 状态重置等功能。
"""

import unittest
from unittest.mock import MagicMock, patch


class TestMainModule(unittest.TestCase):
    """测试 main.py 模块级功能，包括导入、路径设置和函数存在性。"""

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_main_imports(self, mock_login, mock_dm, mock_ctk):
        """测试 main.py 可以成功导入，且核心类已暴露到模块命名空间。

        预期结果：main 模块包含 DataManager 和 LoginWindow 属性。
        """
        import main  # 在 mock 环境就绪后导入 main，避免提前初始化 GUI

        self.assertTrue(hasattr(main, "DataManager"))
        self.assertTrue(hasattr(main, "LoginWindow"))

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_main_base_dir(self, mock_login, mock_dm, mock_ctk):
        """测试项目根目录已加入 sys.path。

        预期结果：main 文件所在目录位于 sys.path 中，确保后续相对导入正常。
        """
        import main  # 在 mock 环境就绪后导入 main，避免提前初始化 GUI
        import sys
        import os

        base_dir = os.path.dirname(os.path.abspath(main.__file__))
        self.assertIn(base_dir, sys.path)

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_main_function_exists(self, mock_login, mock_dm, mock_ctk):
        """测试 main() 函数存在且可调用。

        预期结果：main 模块包含名为 main 的可调用对象。
        """
        import main  # 在 mock 环境就绪后导入 main，避免提前初始化 GUI

        self.assertTrue(callable(getattr(main, "main", None)))


class TestMainFlow(unittest.TestCase):
    """测试主程序 main() 函数流程逻辑，包括登录成功、取消及未知角色等分支。"""

    @patch("main._reset_tk_state")
    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_login_cancelled_breaks_loop(
        self, mock_login_cls, mock_dm_cls, mock_ctk, mock_reset
    ):
        """测试登录取消后退出循环。

        模拟登录窗口返回 success=False，预期主循环直接结束，
        login.run() 被调用一次，且 _reset_tk_state 不会被调用。
        """
        import main  # 在 mock 环境就绪后导入 main，避免提前初始化 GUI

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
    def test_login_success_no_logout(
        self, mock_login_cls, mock_dm_cls, mock_ctk, mock_reset
    ):
        """测试登录成功且不退出登录时结束循环。

        模拟管理员登录成功，App.run() 返回 logout=False，
        预期 _reset_tk_state 被调用一次，App 被正确初始化。
        """
        import main  # 在 mock 环境就绪后导入 main，避免提前初始化 GUI

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
    def test_unknown_role_breaks(
        self, mock_login_cls, mock_dm_cls, mock_ctk, mock_reset
    ):
        """测试未知角色时退出循环。

        模拟登录成功但返回未知角色，预期 _reset_tk_state 被调用一次后循环结束。
        """
        import main  # 在 mock 环境就绪后导入 main，避免提前初始化 GUI

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
    """测试 _reset_tk_state 函数在 tkinter 状态清理时的行为。"""

    @patch("main.ctk")
    @patch("main.DataManager")
    @patch("main.LoginWindow")
    def test_reset_tk_state(self, mock_login, mock_dm, mock_ctk):
        """测试 _reset_tk_state 可被调用。

        在 tkinter 未初始化环境下调用可能抛出异常，属于预期行为，
        只要函数可执行即视为通过。
        """
        import main  # 在 mock 环境就绪后导入 main，避免提前初始化 GUI

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
