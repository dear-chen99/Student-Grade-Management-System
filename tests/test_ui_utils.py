"""UI 工具模块测试 - Test UI Utilities Module.

测试 src/utils/ui_utils.py 中的公共工具函数：
validate_password, create_dialog, create_treeview,
show_info, show_warning, show_error, confirm.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock tkinter 及子模块，避免在无显示环境下初始化 GUI
tk_mock = MagicMock()
tk_mock.TclError = type("TclError", (Exception,), {})
tk_mock.Frame = MagicMock(side_effect=lambda *a, **kw: MagicMock())
tk_mock.Label = MagicMock(side_effect=lambda *a, **kw: MagicMock())
tk_mock.Button = MagicMock(side_effect=lambda *a, **kw: MagicMock())
tk_mock.Entry = MagicMock(side_effect=lambda *a, **kw: MagicMock())
tk_mock.Text = MagicMock(side_effect=lambda *a, **kw: MagicMock())
tk_mock.Toplevel = MagicMock(side_effect=lambda *a, **kw: MagicMock())
tk_mock.StringVar = MagicMock(
    return_value=MagicMock(get=MagicMock(return_value=""), set=MagicMock())
)
tk_mock.IntVar = MagicMock(
    return_value=MagicMock(get=MagicMock(return_value=0), set=MagicMock())
)
tk_mock.DoubleVar = MagicMock(
    return_value=MagicMock(get=MagicMock(return_value=0.0), set=MagicMock())
)
tk_mock.BooleanVar = MagicMock(
    return_value=MagicMock(get=MagicMock(return_value=False), set=MagicMock())
)
tk_mock.messagebox = MagicMock(
    showerror=MagicMock(),
    showinfo=MagicMock(),
    showwarning=MagicMock(),
    askyesno=MagicMock(return_value=True),
    askokcancel=MagicMock(return_value=True),
)
tk_mock.filedialog = MagicMock(
    askopenfilename=MagicMock(return_value=""),
    asksaveasfilename=MagicMock(return_value=""),
)
tk_mock.simpledialog = MagicMock(askstring=MagicMock(return_value=""))
tk_mock.ttk = MagicMock(
    Frame=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Label=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Button=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Entry=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Combobox=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Treeview=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Scrollbar=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Style=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
    Notebook=MagicMock(side_effect=lambda *a, **kw: MagicMock()),
)
tk_mock.Event = MagicMock

_mock_modules = {
    "tkinter": tk_mock,
    "tkinter.messagebox": tk_mock.messagebox,
    "tkinter.filedialog": tk_mock.filedialog,
    "tkinter.simpledialog": tk_mock.simpledialog,
    "tkinter.ttk": tk_mock.ttk,
}


class TestValidatePassword(unittest.TestCase):
    """validate_password 密码强度校验测试."""

    def test_valid_password(self):
        """测试合法密码（含字母和数字，长度 >= 6）."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("abc123")
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_valid_password_long(self):
        """测试较长的合法密码."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("MyP@ssw0rd2026")
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_too_short(self):
        """测试密码过短（< 6 位）."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("ab1")
        self.assertFalse(is_valid)
        self.assertIn("6", msg)

    def test_no_letters(self):
        """测试密码无字母."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("123456")
        self.assertFalse(is_valid)
        self.assertIn("字母", msg)

    def test_no_digits(self):
        """测试密码无数字."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("abcdef")
        self.assertFalse(is_valid)
        self.assertIn("数字", msg)

    def test_empty_password(self):
        """测试空密码."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("")
        self.assertFalse(is_valid)

    def test_exactly_six_chars(self):
        """测试恰好 6 位密码（边界值）."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("ab1234")
        self.assertTrue(is_valid)

    def test_five_chars_too_short(self):
        """测试 5 位密码（边界值，应失败）."""
        from src.utils.ui_utils import validate_password

        is_valid, msg = validate_password("ab123")
        self.assertFalse(is_valid)


class TestCreateDialog(unittest.TestCase):
    """create_dialog 弹窗创建测试."""

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_returns_toplevel(self):
        """测试 create_dialog 返回 Toplevel 实例."""
        from src.utils.ui_utils import create_dialog

        parent = MagicMock()
        parent.winfo_x.return_value = 100
        parent.winfo_y.return_value = 200

        dialog = create_dialog(parent, "测试弹窗")
        self.assertIsNotNone(dialog)
        dialog.title.assert_called_once_with("测试弹窗")

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_default_size(self):
        """测试 create_dialog 默认使用 medium 尺寸."""
        from src.utils.ui_utils import create_dialog

        parent = MagicMock()
        parent.winfo_x.return_value = 0
        parent.winfo_y.return_value = 0

        dialog = create_dialog(parent, "测试")
        # geometry 应被调用，包含尺寸和偏移
        dialog.geometry.assert_called_once()
        geom_arg = dialog.geometry.call_args[0][0]
        self.assertIn("350x250", geom_arg)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_custom_size_key(self):
        """测试 create_dialog 使用 DIALOG_SIZES 中的键名."""
        from src.utils.ui_utils import create_dialog

        parent = MagicMock()
        parent.winfo_x.return_value = 0
        parent.winfo_y.return_value = 0

        dialog = create_dialog(parent, "测试", size="small")
        geom_arg = dialog.geometry.call_args[0][0]
        self.assertIn("300x220", geom_arg)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_direct_geometry_string(self):
        """测试 create_dialog 直接传入 WxH 格式尺寸."""
        from src.utils.ui_utils import create_dialog

        parent = MagicMock()
        parent.winfo_x.return_value = 0
        parent.winfo_y.return_value = 0

        dialog = create_dialog(parent, "测试", size="600x400")
        geom_arg = dialog.geometry.call_args[0][0]
        self.assertIn("600x400", geom_arg)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_modal(self):
        """测试 create_dialog 模态模式调用 grab_set 和 transient."""
        from src.utils.ui_utils import create_dialog

        parent = MagicMock()
        parent.winfo_x.return_value = 0
        parent.winfo_y.return_value = 0

        dialog = create_dialog(parent, "测试", modal=True)
        dialog.grab_set.assert_called_once()
        dialog.transient.assert_called_once_with(parent)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_non_modal(self):
        """测试 create_dialog 非模态模式不调用 grab_set."""
        from src.utils.ui_utils import create_dialog

        parent = MagicMock()
        parent.winfo_x.return_value = 0
        parent.winfo_y.return_value = 0

        dialog = create_dialog(parent, "测试", modal=False)
        dialog.grab_set.assert_not_called()
        dialog.transient.assert_not_called()

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_custom_offset(self):
        """测试 create_dialog 自定义偏移量."""
        from src.utils.ui_utils import create_dialog

        parent = MagicMock()
        parent.winfo_x.return_value = 100
        parent.winfo_y.return_value = 200

        offset = {"x": 10, "y": 20}
        dialog = create_dialog(parent, "测试", offset=offset)
        geom_arg = dialog.geometry.call_args[0][0]
        # 100 + 10 = 110, 200 + 20 = 220
        self.assertIn("+110+220", geom_arg)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dialog_default_offset(self):
        """测试 create_dialog 默认偏移量（DIALOG_OFFSET）."""
        from src.utils.ui_utils import create_dialog
        from src.config import DIALOG_OFFSET

        parent = MagicMock()
        parent.winfo_x.return_value = 100
        parent.winfo_y.return_value = 200

        dialog = create_dialog(parent, "测试")
        geom_arg = dialog.geometry.call_args[0][0]
        expected_x = 100 + DIALOG_OFFSET["x"]
        expected_y = 200 + DIALOG_OFFSET["y"]
        self.assertIn(f"+{expected_x}+{expected_y}", geom_arg)


class TestCreateTreeview(unittest.TestCase):
    """create_treeview 表格创建测试."""

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview_returns_tuple(self):
        """测试 create_treeview 返回 (tree, frame) 元组."""
        from src.utils.ui_utils import create_treeview

        parent = MagicMock()
        tree, frame = create_treeview(
            parent, columns=["学号", "姓名"], widths=[100, 80]
        )
        self.assertIsNotNone(tree)
        self.assertIsNotNone(frame)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview_columns_heading(self):
        """测试 create_treeview 配置表头."""
        from src.utils.ui_utils import create_treeview

        parent = MagicMock()
        tree, _ = create_treeview(
            parent, columns=["学号", "姓名"], widths=[100, 80]
        )
        # heading 应被调用两次
        self.assertEqual(tree.heading.call_count, 2)
        tree.heading.assert_any_call("学号", text="学号")
        tree.heading.assert_any_call("姓名", text="姓名")

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview_column_widths(self):
        """测试 create_treeview 配置列宽."""
        from src.utils.ui_utils import create_treeview

        parent = MagicMock()
        tree, _ = create_treeview(
            parent, columns=["A", "B", "C"], widths=[50, 60, 70]
        )
        tree.column.assert_any_call("A", width=50, anchor="center")
        tree.column.assert_any_call("B", width=60, anchor="center")
        tree.column.assert_any_call("C", width=70, anchor="center")

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview_zebra_default(self):
        """测试 create_treeview 默认启用斑马纹."""
        from src.utils.ui_utils import create_treeview

        parent = MagicMock()
        tree, _ = create_treeview(
            parent, columns=["A"], widths=[50]
        )
        tree.tag_configure.assert_any_call("odd", background=unittest.mock.ANY)
        tree.tag_configure.assert_any_call("even", background=unittest.mock.ANY)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview_zebra_disabled(self):
        """测试 create_treeview 禁用斑马纹."""
        from src.utils.ui_utils import create_treeview

        parent = MagicMock()
        tree, _ = create_treeview(
            parent, columns=["A"], widths=[50], zebra=False
        )
        tree.tag_configure.assert_not_called()

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview_pack_true(self):
        """测试 create_treeview pack=True 自动打包 Frame."""
        from src.utils.ui_utils import create_treeview

        parent = MagicMock()
        _, frame = create_treeview(
            parent, columns=["A"], widths=[50], pack=True
        )
        frame.pack.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview_pack_false(self):
        """测试 create_treeview pack=False 不打包 Frame."""
        from src.utils.ui_utils import create_treeview

        parent = MagicMock()
        _, frame = create_treeview(
            parent, columns=["A"], widths=[50], pack=False
        )
        frame.pack.assert_not_called()


class TestShowInfo(unittest.TestCase):
    """show_info 信息提示框测试."""

    @patch.dict("sys.modules", _mock_modules)
    def test_show_info_without_parent(self):
        """测试 show_info 无父窗口时直接调用 messagebox."""
        from src.utils.ui_utils import show_info

        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            show_info("提示", "操作成功")
            mock_mb.showinfo.assert_called_once_with("提示", "操作成功")

    @patch.dict("sys.modules", _mock_modules)
    def test_show_info_with_parent(self):
        """测试 show_info 有父窗口时传入 parent 参数."""
        from src.utils.ui_utils import show_info

        parent = MagicMock()
        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            show_info("提示", "操作成功", parent=parent)
            mock_mb.showinfo.assert_called_once_with(
                "提示", "操作成功", parent=parent
            )


class TestShowWarning(unittest.TestCase):
    """show_warning 警告提示框测试."""

    @patch.dict("sys.modules", _mock_modules)
    def test_show_warning_without_parent(self):
        """测试 show_warning 无父窗口."""
        from src.utils.ui_utils import show_warning

        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            show_warning("警告", "数据异常")
            mock_mb.showwarning.assert_called_once_with("警告", "数据异常")

    @patch.dict("sys.modules", _mock_modules)
    def test_show_warning_with_parent(self):
        """测试 show_warning 有父窗口."""
        from src.utils.ui_utils import show_warning

        parent = MagicMock()
        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            show_warning("警告", "数据异常", parent=parent)
            mock_mb.showwarning.assert_called_once_with(
                "警告", "数据异常", parent=parent
            )


class TestShowError(unittest.TestCase):
    """show_error 错误提示框测试."""

    @patch.dict("sys.modules", _mock_modules)
    def test_show_error_without_parent(self):
        """测试 show_error 无父窗口."""
        from src.utils.ui_utils import show_error

        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            show_error("错误", "操作失败")
            mock_mb.showerror.assert_called_once_with("错误", "操作失败")

    @patch.dict("sys.modules", _mock_modules)
    def test_show_error_with_parent(self):
        """测试 show_error 有父窗口."""
        from src.utils.ui_utils import show_error

        parent = MagicMock()
        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            show_error("错误", "操作失败", parent=parent)
            mock_mb.showerror.assert_called_once_with(
                "错误", "操作失败", parent=parent
            )


class TestConfirm(unittest.TestCase):
    """confirm 确认对话框测试."""

    @patch.dict("sys.modules", _mock_modules)
    def test_confirm_without_parent(self):
        """测试 confirm 无父窗口返回 askyesno 结果."""
        from src.utils.ui_utils import confirm

        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            mock_mb.askyesno.return_value = True
            result = confirm("确认", "确定删除？")
            mock_mb.askyesno.assert_called_once_with("确认", "确定删除？")
            self.assertTrue(result)

    @patch.dict("sys.modules", _mock_modules)
    def test_confirm_with_parent(self):
        """测试 confirm 有父窗口."""
        from src.utils.ui_utils import confirm

        parent = MagicMock()
        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            mock_mb.askyesno.return_value = False
            result = confirm("确认", "确定删除？", parent=parent)
            mock_mb.askyesno.assert_called_once_with(
                "确认", "确定删除？", parent=parent
            )
            self.assertFalse(result)

    @patch.dict("sys.modules", _mock_modules)
    def test_confirm_returns_true(self):
        """测试 confirm 用户点击'是'返回 True."""
        from src.utils.ui_utils import confirm

        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            mock_mb.askyesno.return_value = True
            result = confirm("确认", "继续操作？")
            self.assertTrue(result)

    @patch.dict("sys.modules", _mock_modules)
    def test_confirm_returns_false(self):
        """测试 confirm 用户点击'否'返回 False."""
        from src.utils.ui_utils import confirm

        with patch("src.utils.ui_utils.messagebox") as mock_mb:
            mock_mb.askyesno.return_value = False
            result = confirm("确认", "继续操作？")
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
