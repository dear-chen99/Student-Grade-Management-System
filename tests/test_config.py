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


class TestUIColors(unittest.TestCase):
    """UI 组件专用色系测试类."""

    def test_ui_colors_exists(self):
        """测试 UI_COLORS 配置存在."""
        from src.config import UI_COLORS

        self.assertIsInstance(UI_COLORS, dict)

    def test_ui_colors_primary(self):
        """测试 UI_COLORS 主色."""
        from src.config import UI_COLORS

        self.assertEqual(UI_COLORS["primary"], "#6366F1")

    def test_ui_colors_teal(self):
        """测试 UI_COLORS 青绿色."""
        from src.config import UI_COLORS

        self.assertEqual(UI_COLORS["teal"], "#00BFA5")

    def test_ui_colors_sidebar(self):
        """测试 UI_COLORS 侧边栏配色."""
        from src.config import UI_COLORS

        self.assertIn("sidebar_bg", UI_COLORS)
        self.assertIn("sidebar_active", UI_COLORS)
        self.assertIn("sidebar_inactive_bg", UI_COLORS)
        self.assertIn("sidebar_inactive_fg", UI_COLORS)

    def test_ui_colors_zebra(self):
        """测试 UI_COLORS 斑马纹配色."""
        from src.config import UI_COLORS

        self.assertIn("row_odd", UI_COLORS)
        self.assertIn("row_even", UI_COLORS)
        self.assertNotEqual(UI_COLORS["row_odd"], UI_COLORS["row_even"])

    def test_ui_colors_card_bg(self):
        """测试 UI_COLORS 卡片背景色."""
        from src.config import UI_COLORS

        self.assertEqual(UI_COLORS["card_bg"], "white")

    def test_ui_colors_format_hex(self):
        """测试 UI_COLORS 中所有 # 开头的颜色格式正确."""
        from src.config import UI_COLORS

        for key, value in UI_COLORS.items():
            if value.startswith("#"):
                self.assertTrue(
                    len(value) == 7,
                    f"UI_COLORS[{key}] 格式不正确: {value}",
                )


class TestFonts(unittest.TestCase):
    """字体配置测试类."""

    def test_fonts_exists(self):
        """测试 FONTS 配置存在."""
        from src.config import FONTS

        self.assertIsInstance(FONTS, dict)

    def test_fonts_body(self):
        """测试 FONTS 正文字体."""
        from src.config import FONTS

        self.assertIn("body", FONTS)
        self.assertEqual(FONTS["body"], ("微软雅黑", 11))

    def test_fonts_title(self):
        """测试 FONTS 标题字体."""
        from src.config import FONTS

        self.assertIn("title", FONTS)
        self.assertEqual(FONTS["title"], ("微软雅黑", 14, "bold"))

    def test_fonts_header(self):
        """测试 FONTS 横幅标题字体."""
        from src.config import FONTS

        self.assertIn("header", FONTS)
        self.assertEqual(FONTS["header"], ("微软雅黑", 16, "bold"))

    def test_fonts_small(self):
        """测试 FONTS 小号字体."""
        from src.config import FONTS

        self.assertIn("small", FONTS)
        self.assertEqual(FONTS["small"], ("微软雅黑", 9))

    def test_fonts_all_are_tuples(self):
        """测试 FONTS 所有值都是元组."""
        from src.config import FONTS

        for key, value in FONTS.items():
            self.assertIsInstance(
                value, tuple, f"FONTS[{key}] 不是元组: {type(value)}"
            )


class TestDialogSizes(unittest.TestCase):
    """弹窗尺寸配置测试类."""

    def test_dialog_sizes_exists(self):
        """测试 DIALOG_SIZES 配置存在."""
        from src.config import DIALOG_SIZES

        self.assertIsInstance(DIALOG_SIZES, dict)

    def test_dialog_sizes_small(self):
        """测试 DIALOG_SIZES small 尺寸."""
        from src.config import DIALOG_SIZES

        self.assertEqual(DIALOG_SIZES["small"], "300x220")

    def test_dialog_sizes_medium(self):
        """测试 DIALOG_SIZES medium 尺寸."""
        from src.config import DIALOG_SIZES

        self.assertEqual(DIALOG_SIZES["medium"], "350x250")

    def test_dialog_sizes_large(self):
        """测试 DIALOG_SIZES large 尺寸."""
        from src.config import DIALOG_SIZES

        self.assertEqual(DIALOG_SIZES["large"], "400x320")

    def test_dialog_sizes_format(self):
        """测试 DIALOG_SIZES 所有值都是 WxH 格式."""
        from src.config import DIALOG_SIZES

        import re

        for key, value in DIALOG_SIZES.items():
            self.assertRegex(
                value,
                r"^\d+x\d+$",
                f"DIALOG_SIZES[{key}] 格式不正确: {value}",
            )


class TestDialogOffset(unittest.TestCase):
    """弹窗偏移量配置测试类."""

    def test_dialog_offset_exists(self):
        """测试 DIALOG_OFFSET 配置存在."""
        from src.config import DIALOG_OFFSET

        self.assertIsInstance(DIALOG_OFFSET, dict)

    def test_dialog_offset_x(self):
        """测试 DIALOG_OFFSET x 偏移."""
        from src.config import DIALOG_OFFSET

        self.assertIn("x", DIALOG_OFFSET)
        self.assertIsInstance(DIALOG_OFFSET["x"], int)

    def test_dialog_offset_y(self):
        """测试 DIALOG_OFFSET y 偏移."""
        from src.config import DIALOG_OFFSET

        self.assertIn("y", DIALOG_OFFSET)
        self.assertIsInstance(DIALOG_OFFSET["y"], int)

    def test_dialog_offset_values(self):
        """测试 DIALOG_OFFSET 偏移值合理."""
        from src.config import DIALOG_OFFSET

        self.assertGreater(DIALOG_OFFSET["x"], 0)
        self.assertGreater(DIALOG_OFFSET["y"], 0)

    def test_dialog_offset_center_exists(self):
        """测试 DIALOG_OFFSET_CENTER 配置存在."""
        from src.config import DIALOG_OFFSET_CENTER

        self.assertIsInstance(DIALOG_OFFSET_CENTER, dict)
        self.assertIn("x", DIALOG_OFFSET_CENTER)
        self.assertIn("y", DIALOG_OFFSET_CENTER)


if __name__ == "__main__":
    unittest.main()
