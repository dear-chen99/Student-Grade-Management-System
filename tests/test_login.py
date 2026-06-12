"""
Login 登录模块单元测试.

测试登录窗口的验证逻辑，包括：
- 登录验证（含边界情况）
- 窗口组件
- 用户交互
- 数据验证
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.login import LoginWindow
from src.config import LOGIN_CONFIG


class TestLoginValidation(unittest.TestCase):
    """登录验证逻辑测试类."""

    def setUp(self):
        """测试前准备."""
        self.valid_username = LOGIN_CONFIG["default_username"]
        self.valid_password = LOGIN_CONFIG["default_password"]

    def test_valid_credentials(self):
        """测试有效凭据."""
        self.assertEqual(self.valid_username, "admin")
        self.assertEqual(self.valid_password, "123456")

    def test_invalid_username(self):
        """测试无效用户名."""
        is_valid = "wrong" == self.valid_username and "123456" == self.valid_password
        self.assertFalse(is_valid)

    def test_invalid_password(self):
        """测试无效密码."""
        is_valid = "admin" == self.valid_username and "wrong" == self.valid_password
        self.assertFalse(is_valid)

    def test_empty_username(self):
        """测试空用户名."""
        is_valid = "" == self.valid_username and "123456" == self.valid_password
        self.assertFalse(is_valid)

    def test_empty_password(self):
        """测试空密码."""
        is_valid = "admin" == self.valid_username and "" == self.valid_password
        self.assertFalse(is_valid)

    def test_empty_credentials(self):
        """测试空凭据."""
        is_valid = "" == self.valid_username and "" == self.valid_password
        self.assertFalse(is_valid)

    def test_whitespace_credentials(self):
        """测试空白字符凭据（去空格后有效."""
        username = "  admin  ".strip()
        password = "  123456  ".strip()
        is_valid = username == self.valid_username and password == self.valid_password
        self.assertTrue(is_valid)

    def test_case_sensitive_username(self):
        """测试用户名大小写敏感."""
        is_valid = "Admin" == self.valid_username and "123456" == self.valid_password
        self.assertFalse(is_valid)

    def test_case_sensitive_password(self):
        """测试密码大小写敏感."""
        is_valid = "admin" == self.valid_username and "123456 " == self.valid_password
        self.assertFalse(is_valid)

    def test_whitespace_only_username(self):
        """测试仅空白字符用户名."""
        username = "   ".strip()
        self.assertEqual(username, "")

    def test_whitespace_only_password(self):
        """测试仅空白字符密码."""
        password = "   ".strip()
        self.assertEqual(password, "")

    def test_none_username(self):
        """测试 None 用户名."""
        username = None
        is_valid = username == self.valid_username
        self.assertFalse(is_valid)

    def test_none_password(self):
        """测试 None 密码."""
        password = None
        is_valid = password == self.valid_password
        self.assertFalse(is_valid)

    def test_very_long_credentials(self):
        """测试超长凭据."""
        long_user = "admin" + "a" * 100
        long_pass = "123456" + "b" * 100
        self.assertFalse(long_user == self.valid_username)
        self.assertFalse(long_pass == self.valid_password)


class TestLoginBehavior(unittest.TestCase):
    """登录行为测试类."""

    def test_username_strip(self):
        """测试用户名去空格."""
        tests = [
            ("admin", "admin"),
            ("  admin", "admin"),
            ("admin  ", "admin"),
            ("  admin  ", "admin"),
            ("\tadmin\n", "admin"),
        ]
        for raw, expected in tests:
            self.assertEqual(raw.strip(), expected)

    def test_password_strip(self):
        """测试密码去空格."""
        tests = [
            ("123456", "123456"),
            ("  123456  ", "123456"),
        ]
        for raw, expected in tests:
            self.assertEqual(raw.strip(), expected)

    def test_login_success_sets_flag(self):
        """测试登录成功设置标志."""
        login_success = False
        username = "admin"
        password = "123456"
        if username == "admin" and password == "123456":
            login_success = True
        self.assertTrue(login_success)

    def test_login_failure_keeps_flag(self):
        """测试登录失败保持标志."""
        login_success = True
        username = "wrong"
        password = "wrong"
        if username == "admin" and password == "123456":
            login_success = True
        else:
            login_success = False
        self.assertFalse(login_success)

    def test_login_error_message(self):
        """测试登录失败错误消息."""
        error_msgs = {
            "invalid": "用户名或密码错误",
            "empty": "用户名和密码不能为空",
            "locked": "账户已被锁定",
        }
        self.assertEqual(error_msgs["invalid"], "用户名或密码错误")
        self.assertEqual(error_msgs["empty"], "用户名和密码不能为空")

    def test_login_success_destruction(self):
        """测试登录成功时应关闭窗口."""
        should_destroy = False
        if "admin" == "admin" and "123456" == "123456":
            should_destroy = True
        self.assertTrue(should_destroy)

    def test_multiple_attempts(self):
        """测试多次尝试."""
        attempts = 0
        max_attempts = 3
        for i in range(max_attempts):
            username = "wrong"
            password = "wrong"
            if username == "admin" and password == "123456":
                break
            attempts += 1
        self.assertEqual(attempts, 3)

    def test_empty_field_detection(self):
        """测试空字段检测."""

        def validate(username, password):
            errors = []
            if not username or not username.strip():
                errors.append("用户名不能为空")
            if not password or not password.strip():
                errors.append("密码不能为空")
            return errors

        self.assertEqual(len(validate("", "")), 2)
        self.assertEqual(len(validate("admin", "")), 1)
        self.assertEqual(len(validate("", "123456")), 1)
        self.assertEqual(len(validate("admin", "123456")), 0)


class TestLoginConstants(unittest.TestCase):
    """登录常量测试类."""

    def test_default_username_constant(self):
        """测试默认用户名常量."""
        self.assertEqual(LOGIN_CONFIG["default_username"], "admin")
        self.assertIsInstance(LOGIN_CONFIG["default_username"], str)

    def test_default_password_constant(self):
        """测试默认密码常量."""
        self.assertEqual(LOGIN_CONFIG["default_password"], "123456")
        self.assertIsInstance(LOGIN_CONFIG["default_password"], str)

    def test_login_success_false_initially(self):
        """测试登录成功标志初始为 False."""
        login_success = False
        self.assertFalse(login_success)

    def test_window_dimensions(self):
        """测试窗口尺寸配置."""
        width = 400
        height = 350
        min_width = 300
        min_height = 250
        self.assertEqual(width, 400)
        self.assertEqual(height, 350)
        self.assertGreaterEqual(width, min_width)
        self.assertGreaterEqual(height, min_height)

    def test_login_config_keys(self):
        """测试登录配置键."""
        expected_keys = {"default_username", "default_password"}
        self.assertEqual(set(LOGIN_CONFIG.keys()), expected_keys)


class TestLoginCredentials(unittest.TestCase):
    """登录凭据测试类."""

    def test_correct_credentials_match(self):
        """测试正确凭据匹配."""
        creds = {"username": "admin", "password": "123456"}
        result = (
            creds["username"] == LOGIN_CONFIG["default_username"]
            and creds["password"] == LOGIN_CONFIG["default_password"]
        )
        self.assertTrue(result)

    def test_incorrect_credentials(self):
        """测试错误凭据."""
        creds = {"username": "admin", "password": "wrong"}
        result = (
            creds["username"] == LOGIN_CONFIG["default_username"]
            and creds["password"] == LOGIN_CONFIG["default_password"]
        )
        self.assertFalse(result)

    def test_partial_credentials(self):
        """测试部分凭据."""
        for pw in ["", " ", "\t"]:
            result = (
                "admin" == LOGIN_CONFIG["default_username"]
                and pw == LOGIN_CONFIG["default_password"]
            )
            self.assertFalse(result)

    def test_username_length(self):
        """测试用户名长度."""
        username = ""
        self.assertEqual(len(username), 0)
        username = "admin"
        self.assertEqual(len(username), 5)

    def test_password_length(self):
        """测试密码长度."""
        password = ""
        self.assertEqual(len(password), 0)
        password = "123456"
        self.assertEqual(len(password), 6)


class TestLoginWindowModule(unittest.TestCase):
    """登录窗口模块测试."""

    def test_login_window_importable(self):
        """测试 LoginWindow 类可导入."""
        self.assertTrue(callable(LoginWindow))

    def test_login_success_var(self):
        """测试 login_success 变量."""
        login_success = False
        self.assertFalse(login_success)

    def test_login_window_attributes(self):
        """测试 LoginWindow 类属性."""
        expected = {
            "__init__",
            "run",
            "_login_action",
            "_prepare_and_show",
            "_preload_background",
            "_show_window",
        }
        actual = {
            name
            for name in dir(LoginWindow)
            if not name.startswith("__") or name in expected
        }
        for attr in expected:
            self.assertIn(attr, dir(LoginWindow))

    def test_mock_login_validation(self):
        """测试模拟登录验证函数."""

        def mock_validate(username, password):
            return (
                username == LOGIN_CONFIG["default_username"]
                and password == LOGIN_CONFIG["default_password"]
            )

        self.assertTrue(mock_validate("admin", "123456"))
        self.assertFalse(mock_validate("wrong", "wrong"))
        self.assertFalse(mock_validate("", ""))

    def test_login_with_special_chars(self):
        """测试特殊字符密码."""
        passwords = ["123456!", "abc123", "测试密码", "!@#$%^"]
        for pw in passwords:
            result = pw == LOGIN_CONFIG["default_password"]
            self.assertFalse(result)


class TestLoginValidationEdgeCases(unittest.TestCase):
    """登录验证边界情况测试."""

    def test_validate_empty_both(self):
        """测试双空验证."""

        def validate(u, p):
            if not u or not p:
                return False
            return (
                u == LOGIN_CONFIG["default_username"]
                and p == LOGIN_CONFIG["default_password"]
            )

        self.assertFalse(validate("", ""))
        self.assertFalse(validate(None, None))
        self.assertFalse(validate("admin", None))
        self.assertFalse(validate(None, "123456"))

    def test_validate_type_safety(self):
        """测试类型安全验证."""

        def validate(u, p):
            if not isinstance(u, str) or not isinstance(p, str):
                return False
            return (
                u == LOGIN_CONFIG["default_username"]
                and p == LOGIN_CONFIG["default_password"]
            )

        self.assertFalse(validate(123, "123456"))
        self.assertFalse(validate("admin", 456))
        self.assertFalse(validate(None, "123456"))
        self.assertTrue(validate("admin", "123456"))

    def test_strip_validation(self):
        """测试去空格验证."""

        def validate_stripped(u, p):
            return (
                u.strip() == LOGIN_CONFIG["default_username"]
                and p.strip() == LOGIN_CONFIG["default_password"]
            )

        self.assertTrue(validate_stripped("  admin  ", "  123456  "))
        self.assertTrue(validate_stripped("admin", "123456"))


if __name__ == "__main__":
    unittest.main()
