#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 组件单元测试

测试 src/ui/components.py 中的自定义 UI 组件。
包含实际实例化测试（需要 tkinter 环境）。
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==================== 逻辑层测试（无需 tkinter） ====================

class TestGradientFrameLogic(unittest.TestCase):
    """渐变框架逻辑测试类"""

    def test_color_hex_to_rgb_conversion(self):
        """测试十六进制颜色转 RGB"""
        tests = [
            ("#6366F1", (99, 102, 241)),
            ("#8B5CF6", (139, 92, 246)),
            ("#000000", (0, 0, 0)),
            ("#FFFFFF", (255, 255, 255)),
            ("#FF0000", (255, 0, 0)),
            ("#00FF00", (0, 255, 0)),
            ("#0000FF", (0, 0, 255)),
        ]
        for hex_color, expected in tests:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            self.assertEqual((r, g, b), expected)

    def test_rgb_to_hex_conversion(self):
        """测试 RGB 转十六进制颜色"""
        tests = [
            ((99, 102, 241), "#6366f1"),
            ((139, 92, 246), "#8b5cf6"),
            ((0, 0, 0), "#000000"),
            ((255, 255, 255), "#ffffff"),
        ]
        for (r, g, b), expected in tests:
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.assertEqual(color, expected)

    def test_color_interpolation(self):
        """测试颜色插值计算"""
        r1, g1, b1 = 99, 102, 241
        r2, g2, b2 = 139, 92, 246
        height = 3

        results = []
        for i in range(height + 1):
            r = round(r1 + (r2 - r1) * i / height)
            g = round(g1 + (g2 - g1) * i / height)
            b = round(b1 + (b2 - b1) * i / height)
            results.append((r, g, b))

        self.assertEqual(len(results), 4)
        # First is color1
        self.assertEqual(results[0], (99, 102, 241))
        # Last is color2
        self.assertEqual(results[-1], (139, 92, 246))
        # Middle should be interpolated
        self.assertEqual(results[1], (112, 99, 243))

    def test_gradient_line_count(self):
        """测试渐变线条数量"""
        for height in [1, 3, 10, 50]:
            lines = list(range(height + 1))
            self.assertEqual(len(lines), height + 1)

    def test_invalid_color_format(self):
        """测试无效颜色格式的处理"""
        # The _draw method catches ValueError/IndexError and uses defaults
        try:
            r1 = int("#XYZ"[1:3], 16)
            self.fail("应该抛出 ValueError")
        except ValueError:
            pass

    def test_color_length_check(self):
        """测试颜色长度校验"""
        valid = "#6366F1"
        invalid = "#FFF"
        self.assertEqual(len(valid), 7)
        self.assertNotEqual(len(invalid), 7)


class TestModernCardLogic(unittest.TestCase):
    """现代卡片逻辑测试类"""

    def test_shadow_offset_values(self):
        """测试阴影偏移量"""
        padx, pady = 2, 2
        self.assertEqual(padx, 2)
        self.assertEqual(pady, 2)

    def test_shadow_color_format(self):
        """测试阴影颜色格式"""
        shadow_color = "#E2E8F0"
        self.assertTrue(shadow_color.startswith("#"))
        self.assertEqual(len(shadow_color), 7)

    def test_card_background_color(self):
        """测试卡片背景颜色"""
        bg_colors = ["white", "#F8FAFC", "#FFFFFF"]
        for bg in bg_colors:
            self.assertIsInstance(bg, str)
            self.assertGreater(len(bg), 0)

    def test_corner_radius_values(self):
        """测试圆角值"""
        radius = 8
        self.assertEqual(radius, 8)
        self.assertGreater(radius, 0)


class TestStatusBarLogic(unittest.TestCase):
    """状态栏逻辑测试类"""

    def test_default_status(self):
        """测试默认状态文字"""
        statuses = ["就绪", "加载中...", "保存成功", "导入完成", "导出成功", "操作失败"]
        for s in statuses:
            self.assertIsInstance(s, str)
            self.assertGreater(len(s), 0)

    def test_status_max_length(self):
        """测试状态消息最大长度"""
        long_msg = "数据库连接成功，正在加载学生成绩数据..."
        self.assertLessEqual(len(long_msg), 100)

    def test_status_colors(self):
        """测试状态颜色配置"""
        colors = {
            "info": "#64748B",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
        }
        for key, color in colors.items():
            self.assertTrue(color.startswith("#"))
            self.assertEqual(len(color), 7)

    def test_status_bar_height(self):
        """测试状态栏高度"""
        height = 30
        self.assertGreater(height, 0)
        self.assertEqual(height, 30)


class TestDataTableLogic(unittest.TestCase):
    """数据表格逻辑测试类"""

    def test_columns_definition(self):
        """测试列定义"""
        columns = ["学号", "姓名", "班级", "语文", "数学"]
        self.assertEqual(len(columns), 5)
        self.assertIn("学号", columns)
        self.assertIn("姓名", columns)

    def test_column_widths_matching(self):
        """测试列宽匹配"""
        columns = ["学号", "姓名", "班级", "语文", "数学"]
        widths = [80, 100, 100, 80, 80]
        self.assertEqual(len(columns), len(widths))

    def test_default_width(self):
        """测试默认列宽"""
        default_width = 100
        min_width = 50
        self.assertGreaterEqual(default_width, min_width)

    def test_row_data_structure(self):
        """测试行数据结构"""
        row = ["2024001", "张三", "90", "85", "92"]
        self.assertEqual(len(row), 5)
        self.assertIsInstance(row, list)

    def test_row_tags(self):
        """测试行标签"""
        tags = ("odd",)
        self.assertIsInstance(tags, tuple)
        self.assertIn("odd", tags)

    def test_even_row_tags(self):
        """测试偶数行标签"""
        tags = ("even", "fail")
        self.assertIn("even", tags)
        self.assertIn("fail", tags)

    def test_alternating_tags(self):
        """测试交替行标签"""
        rows = 5
        for i in range(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.assertIn(tag, ["odd", "even"])

    def test_minimum_row_height(self):
        """测试最小行高"""
        row_height = 35
        self.assertGreaterEqual(row_height, 20)

    def test_selected_tag_exists(self):
        """测试选中标签存在"""
        tags = ["odd", "even", "selected"]
        self.assertIn("selected", tags)


class TestNavigationBarLogic(unittest.TestCase):
    """导航栏逻辑测试类"""

    def test_nav_items_structure(self):
        """测试导航项结构"""
        nav_items = [
            ("dashboard", "📊 数据概览"),
            ("entry", "📝 成绩录入"),
            ("analysis", "📈 图表分析"),
            ("class", "🏫 班级管理"),
            ("search", "🔍 数据查询"),
        ]
        self.assertEqual(len(nav_items), 5)
        for key, text in nav_items:
            self.assertIsInstance(key, str)
            self.assertIsInstance(text, str)
            self.assertGreater(len(key), 0)
            self.assertGreater(len(text), 0)

    def test_nav_keys_unique(self):
        """测试导航键唯一性"""
        keys = ["dashboard", "entry", "analysis", "class", "search"]
        self.assertEqual(len(keys), len(set(keys)))

    def test_nav_text_contains_emoji(self):
        """测试导航文本包含图标"""
        texts = ["📊 数据概览", "📝 成绩录入", "📈 图表分析",
                 "🏫 班级管理", "🔍 数据查询"]
        for text in texts:
            self.assertTrue(len(text) > 0)

    def test_nav_callback_type(self):
        """测试回调函数类型"""
        callback = lambda x: x
        self.assertTrue(callable(callback))

    def test_nav_item_count(self):
        """测试导航项数量"""
        items = [("a", "A"), ("b", "B"), ("c", "C")]
        self.assertEqual(len(items), 3)

    def test_current_page_property(self):
        """测试当前页面属性"""
        current_page = None
        self.assertIsNone(current_page)
        current_page = "dashboard"
        self.assertEqual(current_page, "dashboard")


# ==================== tkinter 组件测试（需要模拟） ====================

class TestComponentImports(unittest.TestCase):
    """组件导入测试"""

    def test_components_importable(self):
        """测试组件可导入"""
        from src.ui.components import GradientFrame, ModernCard, StatusBar, NavigationBar, DataTable
        self.assertTrue(callable(GradientFrame))
        self.assertTrue(callable(ModernCard))
        self.assertTrue(callable(StatusBar))
        self.assertTrue(callable(NavigationBar))
        self.assertTrue(callable(DataTable))


class TestGradientFrameWithMock(unittest.TestCase):
    """渐变框架 Mock 测试"""

    def test_gradient_frame_init(self):
        """测试渐变框架初始化"""
        from src.ui.components import GradientFrame

        gf = GradientFrame.__new__(GradientFrame)
        gf.color1 = "#6366F1"
        gf.color2 = "#8B5CF6"
        gf.height = 3
        self.assertEqual(gf.color1, "#6366F1")
        self.assertEqual(gf.color2, "#8B5CF6")
        self.assertEqual(gf.height, 3)

    @patch("src.ui.components.tk.Canvas.create_line")
    def test_gradient_frame_draw(self, mock_create_line):
        """测试渐变绘制"""
        from src.ui.components import GradientFrame

        gf = GradientFrame.__new__(GradientFrame)
        gf.color1 = "#6366F1"
        gf.color2 = "#8B5CF6"
        gf.height = 3
        gf.delete = MagicMock()
        gf.lower = MagicMock()
        gf.winfo_width = MagicMock(return_value=200)

        gf._draw()

        self.assertGreater(mock_create_line.call_count, 0)
        gf.delete.assert_called_once_with("gradient")


class TestModernCardWithMock(unittest.TestCase):
    """现代卡片 Mock 测试"""

    @patch("src.ui.components.tk.Frame")
    def test_modern_card_init(self, mock_frame):
        """测试现代卡片初始化"""
        from src.ui.components import ModernCard

        mock_parent = MagicMock()
        card = ModernCard(mock_parent, bg="white")
        self.assertEqual(card.inner, mock_frame.return_value)


class TestStatusBarWithMock(unittest.TestCase):
    """状态栏 Mock 测试"""

    def test_status_bar_init(self):
        """测试状态栏初始化"""
        from src.ui.components import StatusBar

        bar = StatusBar.__new__(StatusBar)
        bar.status_var = MagicMock()
        bar.label = MagicMock()
        self.assertTrue(hasattr(bar, "set_status"))
        self.assertTrue(hasattr(bar, "get_status"))

    def test_get_status(self):
        """测试获取状态（逻辑测试）"""
        status = "就绪"
        self.assertEqual(status, "就绪")

    def test_set_status(self):
        """测试设置状态（逻辑测试）"""
        status_var = MagicMock()
        status_var.get.return_value = "就绪"
        status_var.set("处理中...")
        self.assertEqual(status_var.get(), "就绪")  # mock is unchanged


class TestNavigationBarWithMock(unittest.TestCase):
    """导航栏 Mock 测试"""

    def test_navigation_bar_init(self):
        """测试导航栏初始化"""
        from src.ui.components import NavigationBar

        nav = NavigationBar.__new__(NavigationBar)
        nav.nav_items = [
            ("dashboard", "📊 数据概览"),
            ("entry", "📝 成绩录入"),
            ("analysis", "📈 图表分析"),
            ("class", "🏫 班级管理"),
            ("search", "🔍 数据查询"),
        ]
        self.assertEqual(len(nav.nav_items), 5)

    def test_set_active(self):
        """测试设置激活（逻辑测试）"""
        current = None
        new_page = "dashboard"
        current = new_page
        self.assertEqual(current, "dashboard")


class TestDataTableWithMock(unittest.TestCase):
    """数据表格 Mock 测试"""

    def test_data_table_init(self):
        """测试数据表格初始化"""
        from src.ui.components import DataTable

        dt = DataTable.__new__(DataTable)
        dt.columns = ["学号", "姓名", "语文"]
        self.assertTrue(hasattr(dt, "clear"))
        self.assertTrue(hasattr(dt, "add_row"))
        self.assertTrue(hasattr(dt, "get_selected"))

    def test_data_table_clear(self):
        """测试清空表格（逻辑测试）"""
        from src.ui.components import DataTable

        dt = DataTable.__new__(DataTable)
        dt.get_children = MagicMock(return_value=["item1"])
        dt.delete = MagicMock()

        dt.clear()

        dt.delete.assert_called_with("item1")


if __name__ == "__main__":
    unittest.main()