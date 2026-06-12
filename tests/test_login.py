"""
Login 登录模块单元测试.

真正覆盖 LoginWindow 核心逻辑的测试.
"""

import unittest
from unittest.mock import MagicMock, patch
from modules.login import LoginWindow


# ========== ✅ 核心修改：创建 MockLoginWindow 子类，跳过 GUI 初始化 ==========
class MockLoginWindow(LoginWindow):
    """一个假的 LoginWindow，不创建真正的 Tk 窗口，避免 TclError。"""

    def __init__(self):
        # 重点：不调用 super().__init__()，完全跳过 Tk 窗口创建
        self.login_success = False

        # 模拟 GUI 控件和必须的方法
        self.username_entry = MagicMock()
        self.password_entry = MagicMock()
        self.destroy = MagicMock()
        self.withdraw = MagicMock()
        self.deiconify = MagicMock()
        self.lift = MagicMock()
        self.focus_force = MagicMock()
        self.update = MagicMock()
        self.update_idletasks = MagicMock()
        self.canvas = MagicMock()
        self.card = MagicMock()
        self.title_label = MagicMock()
        self.login_button = MagicMock()
        self.after = MagicMock()


# ============================================================================


class TestLoginWindowCoreLogic(unittest.TestCase):
    """测试 LoginWindow 的核心登录逻辑."""

    def setUp(self):
        """创建一个假的 LoginWindow 实例，不会触发 Tk 初始化。"""
        self.login = MockLoginWindow()

    @patch("modules.login.messagebox.showerror")
    def test_login_action_success(self, mock_showerror):
        """测试登录成功：正确设置 login_success 并销毁窗口."""
        self.login.username_entry.get = MagicMock(return_value="admin")
        self.login.password_entry.get = MagicMock(return_value="123456")

        self.login._login_action()

        self.assertTrue(self.login.login_success)
        self.login.destroy.assert_called_once()
        mock_showerror.assert_not_called()

    @patch("modules.login.messagebox.showerror")
    def test_login_action_failure_wrong_password(self, mock_showerror):
        """测试登录失败：密码错误时不应销毁窗口，应弹出错误框."""
        self.login.username_entry.get = MagicMock(return_value="admin")
        self.login.password_entry.get = MagicMock(return_value="wrong_password")

        self.login._login_action()

        self.assertFalse(self.login.login_success)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")

    @patch("modules.login.messagebox.showerror")
    def test_login_action_failure_unknown_user(self, mock_showerror):
        """测试登录失败：未知用户名."""
        self.login.username_entry.get = MagicMock(return_value="unknown_user")
        self.login.password_entry.get = MagicMock(return_value="123456")

        self.login._login_action()

        self.assertFalse(self.login.login_success)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")

    @patch("modules.login.messagebox.showerror")
    def test_login_action_username_trimming(self, mock_showerror):
        """测试登录时用户名空格会被正确处理."""
        self.login.username_entry.get = MagicMock(return_value="  admin  ")
        self.login.password_entry.get = MagicMock(return_value="123456")

        self.login._login_action()

        self.assertTrue(self.login.login_success)
        self.login.destroy.assert_called_once()
        mock_showerror.assert_not_called()

    @patch("modules.login.messagebox.showerror")
    def test_login_action_empty_username(self, mock_showerror):
        """测试空用户名登录失败."""
        self.login.username_entry.get = MagicMock(return_value="")
        self.login.password_entry.get = MagicMock(return_value="123456")

        self.login._login_action()

        self.assertFalse(self.login.login_success)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")

    @patch("modules.login.messagebox.showerror")
    def test_login_action_empty_password(self, mock_showerror):
        """测试空密码登录失败."""
        self.login.username_entry.get = MagicMock(return_value="admin")
        self.login.password_entry.get = MagicMock(return_value="")

        self.login._login_action()

        self.assertFalse(self.login.login_success)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")


if __name__ == "__main__":
    unittest.main()
