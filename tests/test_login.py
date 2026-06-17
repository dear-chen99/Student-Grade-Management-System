"""
Login 登录模块单元测试.

真正覆盖 LoginWindow 核心逻辑的测试，包括登录验证、角色切换、
辅助方法及生命周期等。
"""

import unittest
from unittest.mock import MagicMock, patch
from modules.login import LoginWindow


# ========== 核心修改：创建 MockLoginWindow 子类，跳过 GUI 初始化 ==========
class MockLoginWindow(LoginWindow):
    """一个假的 LoginWindow，不创建真正的 Tk 窗口，避免 TclError。

    通过跳过 super().__init__() 完全绕过 Tk 窗口创建，
    同时模拟所有被测试方法依赖的控件和属性。
    """

    def __init__(self):
        # 重点：不调用 super().__init__()，完全跳过 Tk 窗口创建
        self.login_result = None
        self.current_role = "admin"

        # 防止 tkinter 属性访问递归
        self.tk = MagicMock()
        self.bg_image = None
        self.photo_image = None
        self.mainloop = MagicMock()
        self.winfo_width = MagicMock(return_value=900)
        self.winfo_height = MagicMock(return_value=550)

        # 使用简单对象模拟 Entry 控件，避免 MagicMock 递归问题
        self.account_entry = type(
            "Entry",
            (),
            {
                "get": lambda self: "",
                "delete": lambda self, a, b: None,
                "configure": lambda self, **kw: None,
            },
        )()
        self.password_entry = type(
            "Entry",
            (),
            {
                "get": lambda self: "",
                "delete": lambda self, a, b: None,
                "configure": lambda self, **kw: None,
            },
        )()
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
        self.role_buttons = {
            "admin": MagicMock(),
            "teacher": MagicMock(),
            "student": MagicMock(),
        }

        # 创建真实 DataManager 用于验证
        from modules.data_manager import DataManager
        import tempfile
        self.dm = DataManager(file_path=tempfile.mktemp(suffix=".json"))


# ============================================================================


class TestLoginWindowCoreLogic(unittest.TestCase):
    """测试 LoginWindow 的核心登录逻辑，包括成功、失败及边界场景。"""

    def setUp(self):
        """创建一个假的 LoginWindow 实例，不会触发 Tk 初始化。"""
        self.login = MockLoginWindow()

    def _set_credentials(self, account: str, password: str) -> None:
        """设置模拟的账号密码。

        Args:
            account: 账号字符串。
            password: 密码字符串。
        """
        self.login.account_entry = type(
            "Entry", (), {"get": lambda self, s=account: s}
        )()
        self.login.password_entry = type(
            "Entry", (), {"get": lambda self, s=password: s}
        )()

    @patch("modules.login.messagebox.showerror")
    def test_login_action_success(self, mock_showerror):
        """测试登录成功：正确设置 login_result 并销毁窗口。

        使用默认 admin/123456 登录，预期 login_result 不为 None，
        success 为 True，且窗口被销毁，不弹出错误框。
        """
        self._set_credentials("admin", "123456")

        self.login._login_action()

        self.assertIsNotNone(self.login.login_result)
        self.assertTrue(self.login.login_result.get("success"))
        self.login.destroy.assert_called_once()
        mock_showerror.assert_not_called()

    @patch("modules.login.messagebox.showerror")
    def test_login_action_failure_wrong_password(self, mock_showerror):
        """测试登录失败：密码错误时不应销毁窗口，应弹出错误框。

        预期结果：login_result 保持 None，destroy 未被调用，
        showerror 被调用一次并提示"用户名或密码错误"。
        """
        self._set_credentials("admin", "wrong_password")

        self.login._login_action()

        self.assertIsNone(self.login.login_result)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")

    @patch("modules.login.messagebox.showerror")
    def test_login_action_failure_unknown_user(self, mock_showerror):
        """测试登录失败：未知用户名。

        预期结果：login_result 为 None，弹出错误提示。
        """
        self._set_credentials("unknown_user", "123456")

        self.login._login_action()

        self.assertIsNone(self.login.login_result)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")

    @patch("modules.login.messagebox.showerror")
    def test_login_action_username_trimming(self, mock_showerror):
        """测试登录时用户名空格会被正确处理。

        输入带前后空格的 admin，预期仍能正常登录成功。
        """
        self._set_credentials("  admin  ", "123456")

        self.login._login_action()

        self.assertIsNotNone(self.login.login_result)
        self.assertTrue(self.login.login_result.get("success"))
        self.login.destroy.assert_called_once()
        mock_showerror.assert_not_called()

    @patch("modules.login.messagebox.showerror")
    def test_login_action_empty_username(self, mock_showerror):
        """测试空用户名登录失败。

        预期结果：login_result 为 None，弹出错误提示。
        """
        self._set_credentials("", "123456")

        self.login._login_action()

        self.assertIsNone(self.login.login_result)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")

    @patch("modules.login.messagebox.showerror")
    def test_login_action_empty_password(self, mock_showerror):
        """测试空密码登录失败。

        预期结果：login_result 为 None，弹出错误提示。
        """
        self._set_credentials("admin", "")

        self.login._login_action()

        self.assertIsNone(self.login.login_result)
        self.login.destroy.assert_not_called()
        mock_showerror.assert_called_once_with("登录失败", "用户名或密码错误！")


class TestVerifyLogin(unittest.TestCase):
    """测试 _verify_login 方法（不同角色）。"""

    def setUp(self):
        """创建 MockLoginWindow 并添加测试数据。"""
        self.login = MockLoginWindow()
        self.login.dm.add_teacher("T001", "王老师", "pass123")
        self.login.dm.add_student("2024001", "张三", "A班")
        self.login.dm.update_student("2024001", password="stu123")

    def test_verify_admin_success(self):
        """管理员验证成功。

        预期结果：success 为 True，role 为 admin。
        """
        self.login.current_role = "admin"
        result = self.login._verify_login("admin", "123456")
        self.assertTrue(result["success"])
        self.assertEqual(result["role"], "admin")

    def test_verify_admin_failure(self):
        """管理员验证失败。

        预期结果：success 为 False。
        """
        self.login.current_role = "admin"
        result = self.login._verify_login("admin", "wrong")
        self.assertFalse(result["success"])

    def test_verify_teacher_success(self):
        """教师验证成功。

        预期结果：success 为 True，role 为 teacher。
        """
        self.login.current_role = "teacher"
        result = self.login._verify_login("T001", "pass123")
        self.assertTrue(result["success"])
        self.assertEqual(result["role"], "teacher")

    def test_verify_teacher_failure(self):
        """教师验证失败。

        预期结果：success 为 False。
        """
        self.login.current_role = "teacher"
        result = self.login._verify_login("T001", "wrong")
        self.assertFalse(result["success"])

    def test_verify_student_success(self):
        """学生验证成功。

        预期结果：success 为 True，role 为 student。
        """
        self.login.current_role = "student"
        result = self.login._verify_login("2024001", "stu123")
        self.assertTrue(result["success"])
        self.assertEqual(result["role"], "student")

    def test_verify_student_failure(self):
        """学生验证失败。

        预期结果：success 为 False。
        """
        self.login.current_role = "student"
        result = self.login._verify_login("2024001", "wrong")
        self.assertFalse(result["success"])

    def test_verify_unknown_role(self):
        """未知角色验证失败。

        预期结果：success 为 False。
        """
        self.login.current_role = "unknown"
        result = self.login._verify_login("admin", "123456")
        self.assertFalse(result["success"])


class TestSwitchRole(unittest.TestCase):
    """测试 _switch_role 方法。"""

    def setUp(self):
        """创建 MockLoginWindow 实例。"""
        self.login = MockLoginWindow()

    def test_switch_to_teacher(self):
        """切换到教师角色。

        预期结果：current_role 被设为 teacher。
        """
        self.login._switch_role("teacher")
        self.assertEqual(self.login.current_role, "teacher")

    def test_switch_to_student(self):
        """切换到学生角色。

        预期结果：current_role 被设为 student。
        """
        self.login._switch_role("student")
        self.assertEqual(self.login.current_role, "student")

    def test_switch_to_admin(self):
        """切换回管理员角色。

        预期结果：current_role 被恢复为 admin。
        """
        self.login._switch_role("teacher")
        self.login._switch_role("admin")
        self.assertEqual(self.login.current_role, "admin")


class TestLoginWindowHelpers(unittest.TestCase):
    """测试 LoginWindow 辅助方法。"""

    def setUp(self):
        """创建 MockLoginWindow 实例。"""
        self.login = MockLoginWindow()

    def test_preload_background_no_image(self):
        """测试预加载背景图片（图片不存在）。

        预期结果：bg_image 保持 None。
        """
        self.login.image_path = "nonexistent.jpg"
        self.login._preload_background()
        self.assertIsNone(self.login.bg_image)

    @patch("modules.login.os.path.exists")
    @patch("modules.login.Image.open")
    def test_preload_background_with_image(self, mock_open, mock_exists):
        """测试预加载背景图片（图片存在）。

        预期结果：bg_image 被成功赋值。
        """
        mock_exists.return_value = True
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        self.login.image_path = "bg.jpg"
        self.login._preload_background()
        self.assertIsNotNone(self.login.bg_image)

    def test_fix_entry_height(self):
        """测试修复输入框高度。

        预期结果：方法无异常执行。
        """
        self.login._fix_entry_height()
        self.assertTrue(True)

    def test_refresh_placeholders_admin(self):
        """测试刷新占位符（管理员角色）。

        预期结果：方法无异常执行。
        """
        self.login.current_role = "admin"
        self.login._refresh_placeholders()
        self.assertTrue(True)

    def test_refresh_placeholders_teacher(self):
        """测试刷新占位符（教师角色）。

        预期结果：方法无异常执行。
        """
        self.login.current_role = "teacher"
        self.login._refresh_placeholders()
        self.assertTrue(True)

    def test_refresh_placeholders_student(self):
        """测试刷新占位符（学生角色）。

        预期结果：方法无异常执行。
        """
        self.login.current_role = "student"
        self.login._refresh_placeholders()
        self.assertTrue(True)

    def test_show_window(self):
        """测试显示窗口方法。

        预期结果：deiconify、lift、focus_force 被依次调用。
        """
        self.login._show_window()
        self.login.deiconify.assert_called_once()
        self.login.lift.assert_called_once()
        self.login.focus_force.assert_called_once()

    def test_run_returns_dict(self):
        """测试 run 方法返回字典。

        预期结果：返回字典类型。
        """
        self.login.login_result = {"success": True}
        result = self.login.run()
        self.assertIsInstance(result, dict)


class TestLoginWindowLifecycle(unittest.TestCase):
    """测试 LoginWindow 生命周期方法。"""

    def setUp(self):
        """创建 MockLoginWindow 实例。"""
        self.login = MockLoginWindow()

    def test_prepare_and_show_no_bg(self):
        """测试准备并显示窗口（无背景图）。

        预期结果：canvas.delete("all") 被调用以清空画布。
        """
        self.login.bg_image = None
        self.login._prepare_and_show()
        self.login.canvas.delete.assert_called_once_with("all")

    @patch("modules.login.ImageTk.PhotoImage")
    @patch("modules.login.Image.Resampling")
    def test_prepare_and_show_with_bg(self, mock_resampling, mock_photo):
        """测试准备并显示窗口（有背景图）。

        预期结果：canvas.delete("all") 被调用，背景图处理不抛异常。
        """
        mock_img = MagicMock()
        mock_img.resize.return_value = MagicMock()
        self.login.bg_image = mock_img
        self.login._prepare_and_show()
        self.login.canvas.delete.assert_called_once_with("all")


if __name__ == "__main__":
    unittest.main()
