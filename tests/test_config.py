"""
配置模块测试 - Test Configuration Module.

测试 src/config.py 中的配置常量和设置。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfigConstants(unittest.TestCase):
    """配置常量测试类."""

    def test_colors_config_exists(self):
        """测试颜色配置存在."""
        from src.config import COLORS

        self.assertIsInstance(COLORS, dict)
        self.assertIn("primary", COLORS)
        self.assertIn("secondary", COLORS)
        self.assertIn("success", COLORS)
        self.assertIn("warning", COLORS)
        self.assertIn("danger", COLORS)

    def test_colors_format(self):
        """测试颜色格式."""
        from src.config import COLORS

        for key, value in COLORS.items():
            self.assertTrue(
                value.startswith("#") and len(value) == 7,
                f"颜色 {key} 格式不正确: {value}",
            )

    def test_window_config_exists(self):
        """测试窗口配置存在."""
        from src.config import WINDOW_CONFIG

        self.assertIsInstance(WINDOW_CONFIG, dict)
        self.assertEqual(WINDOW_CONFIG["title"], "学生成绩管理系统")
        self.assertEqual(WINDOW_CONFIG["width"], 1200)
        self.assertEqual(WINDOW_CONFIG["height"], 780)

    def test_login_config_exists(self):
        """测试登录配置存在."""
        from src.config import LOGIN_CONFIG

        self.assertIsInstance(LOGIN_CONFIG, dict)
        self.assertEqual(LOGIN_CONFIG["default_username"], "admin")
        self.assertEqual(LOGIN_CONFIG["default_password"], "123456")

    def test_chart_config_exists(self):
        """测试图表配置存在."""
        from src.config import CHART_CONFIG

        self.assertIsInstance(CHART_CONFIG, dict)
        self.assertEqual(CHART_CONFIG["passing_score"], 60)
        self.assertEqual(CHART_CONFIG["excellent_score"], 90)

    def test_data_config_exists(self):
        """测试数据配置存在."""
        from src.config import DATA_CONFIG

        self.assertIsInstance(DATA_CONFIG, dict)
        self.assertEqual(DATA_CONFIG["backup_suffix"], ".bak")
        self.assertEqual(DATA_CONFIG["temp_suffix"], ".tmp")


class TestColorValues(unittest.TestCase):
    """颜色值测试类."""

    def test_primary_color(self):
        """测试主色."""
        from src.config import COLORS

        self.assertEqual(COLORS["primary"], "#6366F1")

    def test_secondary_color(self):
        """测试次色."""
        from src.config import COLORS

        self.assertEqual(COLORS["secondary"], "#8B5CF6")

    def test_success_color(self):
        """测试成功色."""
        from src.config import COLORS

        self.assertEqual(COLORS["success"], "#10B981")

    def test_warning_color(self):
        """测试警告色."""
        from src.config import COLORS

        self.assertEqual(COLORS["warning"], "#F59E0B")

    def test_danger_color(self):
        """测试危险色."""
        from src.config import COLORS

        self.assertEqual(COLORS["danger"], "#EF4444")

    def test_info_color(self):
        """测试信息色."""
        from src.config import COLORS

        self.assertEqual(COLORS["info"], "#3B82F6")

    def test_white_color(self):
        """测试白色."""
        from src.config import COLORS

        self.assertEqual(COLORS["white"], "#FFFFFF")

    def test_gray_color(self):
        """测试灰色."""
        from src.config import COLORS

        self.assertEqual(COLORS["gray"], "#64748B")


class TestWindowDimensions(unittest.TestCase):
    """窗口尺寸测试类."""

    def test_window_width(self):
        """测试窗口宽度."""
        from src.config import WINDOW_CONFIG

        self.assertEqual(WINDOW_CONFIG["width"], 1200)
        self.assertGreater(WINDOW_CONFIG["width"], 0)

    def test_window_height(self):
        """测试窗口高度."""
        from src.config import WINDOW_CONFIG

        self.assertEqual(WINDOW_CONFIG["height"], 780)
        self.assertGreater(WINDOW_CONFIG["height"], 0)

    def test_min_width(self):
        """测试最小宽度."""
        from src.config import WINDOW_CONFIG

        self.assertEqual(WINDOW_CONFIG["min_width"], 1000)
        self.assertGreater(WINDOW_CONFIG["min_width"], 0)

    def test_min_height(self):
        """测试最小高度."""
        from src.config import WINDOW_CONFIG

        self.assertEqual(WINDOW_CONFIG["min_height"], 620)
        self.assertGreater(WINDOW_CONFIG["min_height"], 0)


class TestConfigConstantsValues(unittest.TestCase):
    """配置常量值测试类."""

    def test_passing_score(self):
        """测试及格分数."""
        from src.config import CHART_CONFIG

        self.assertEqual(CHART_CONFIG["passing_score"], 60)

    def test_excellent_score(self):
        """测试优秀分数."""
        from src.config import CHART_CONFIG

        self.assertEqual(CHART_CONFIG["excellent_score"], 90)

    def test_backup_suffix(self):
        """测试备份文件后缀."""
        from src.config import DATA_CONFIG

        self.assertEqual(DATA_CONFIG["backup_suffix"], ".bak")

    def test_temp_suffix(self):
        """测试临时文件后缀."""
        from src.config import DATA_CONFIG

        self.assertEqual(DATA_CONFIG["temp_suffix"], ".tmp")


if __name__ == "__main__":
    unittest.main()
