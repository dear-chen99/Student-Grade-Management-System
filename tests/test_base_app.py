"""Base App (src/utils/base_app.py) 单元测试.

使用 mock 绕过 Tkinter GUI 初始化，测试 BaseApp 基类的公共方法、
UI 辅助函数、导出逻辑及生命周期等。
"""

import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open


class MockWindow:
    """Mock ttkbootstrap Window，模拟所有常用的窗口及控件方法."""

    def __init__(self, *args, **kwargs):
        pass

    def title(self, *args):
        pass

    def state(self, *args):
        pass

    def minsize(self, *args):
        pass

    def configure(self, **kwargs):
        pass

    def protocol(self, *args):
        pass

    def mainloop(self):
        pass

    def destroy(self):
        pass

    def update_idletasks(self):
        pass

    def update(self):
        pass

    def after(self, *args):
        pass

    def pack_propagate(self, *args):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def winfo_children(self):
        return []

    def winfo_exists(self):
        return 1

    def winfo_x(self):
        return 0

    def winfo_y(self):
        return 0

    def geometry(self, *args):
        pass

    def grab_set(self):
        pass

    def transient(self, *args):
        pass

    def withdraw(self):
        pass

    def deiconify(self):
        pass

    def resizable(self, *args):
        pass

    def focus_force(self):
        pass

    def lift(self):
        pass

    def config(self, **kwargs):
        pass

    def bind(self, *args):
        pass

    def unbind(self, *args):
        pass

    def cget(self, *args):
        return ""

    def children(self):
        return {}


class MockStyle:
    """Mock ttkbootstrap Style，用于替换主题样式对象."""

    def __init__(self, *args, **kwargs):
        pass

    def configure(self, *args, **kwargs):
        pass

    def map(self, *args, **kwargs):
        pass

    def lookup(self, *args, **kwargs):
        return ""


class MockTreeview:
    """Mock ttk Treeview，模拟表格控件的常用操作."""

    def __init__(self, *args, **kwargs):
        self._items = {}
        self._next_iid = 1
        self.master = MagicMock()

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def column(self, *args, **kwargs):
        pass

    def heading(self, *args, **kwargs):
        pass

    def insert(self, parent, index, values=None, tags=None):
        iid = f"I{self._next_iid}"
        self._next_iid += 1
        self._items[iid] = values
        return iid

    def delete(self, *items):
        pass

    def get_children(self, item=None):
        return list(self._items.keys())

    def item(self, item, **kwargs):
        if "values" in kwargs:
            self._items[item] = kwargs["values"]
        return self._items.get(item)

    def set(self, item, column=None, value=None):
        return ""

    def selection(self):
        return list(self._items.keys())[:1]

    def bind(self, *args):
        pass

    def yview(self, *args):
        pass

    def xview(self, *args):
        pass

    def tag_configure(self, *args, **kwargs):
        pass

    def focus(self, *args):
        return ""

    def identify(self, *args):
        return ""

    def bbox(self, *args):
        return (0, 0, 10, 10)

    def see(self, *args):
        pass

    def index(self, *args):
        return 0

    def winfo_exists(self):
        return 1

    def __getitem__(self, key):
        return ["col1", "col2"]


class MockScrollbar:
    """Mock ttk Scrollbar，用于模拟滚动条."""

    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def set(self, *args):
        pass


# 构造 tkinter 及子模块的 mock 对象，统一替换 sys.modules 中的真实模块
tk_mock = MagicMock()
tk_mock.TclError = type("TclError", (Exception,), {})
tk_mock.Frame = MockWindow
tk_mock.Label = MockWindow
tk_mock.Button = MockWindow
tk_mock.Entry = MockWindow
tk_mock.Text = MockWindow
tk_mock.Canvas = MockWindow
tk_mock.Toplevel = MockWindow
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
    Frame=MockWindow,
    Label=MockWindow,
    Button=MockWindow,
    Entry=MockWindow,
    Combobox=MockWindow,
    Treeview=MockTreeview,
    Scrollbar=MockScrollbar,
    Style=MockStyle,
    Notebook=MockWindow,
)
tk_mock.Event = MagicMock

_mock_modules = {
    "ttkbootstrap": MagicMock(Window=MockWindow, Style=MockStyle),
    "tkinter": tk_mock,
    "tkinter.messagebox": tk_mock.messagebox,
    "tkinter.filedialog": tk_mock.filedialog,
    "tkinter.simpledialog": tk_mock.simpledialog,
    "tkinter.ttk": tk_mock.ttk,
}


def _make_base_app_instance(BaseApp):
    """创建一个 BaseApp 具体子类的裸实例（绕过 ABC 和 __init__）.

    用于测试需要手动设置属性的 BaseApp 方法。
    """
    class _Concrete(BaseApp):
        def _get_window_title(self):
            return "Test"

        def _get_header_title(self):
            return "Test"

        def _get_user_display_name(self):
            return "Test"

        def _get_avatar_data(self):
            return {"name": "Test", "avatar": ""}

        def _save_avatar(self, path):
            pass

        def _get_profile_page_title(self):
            return "Test"

        def _get_avatar_label_text(self):
            return "Test"

        def _get_profile_id_label(self):
            return "Test"

        def _get_profile_id_value(self):
            return "Test"

        def _get_profile_pwd_label(self):
            return "Test"

        def _get_profile_name_label(self):
            return "Test"

        def _get_profile_name_value(self):
            return "Test"

        def _get_profile_data(self):
            return {}

        def _save_profile_entity(self, name, phone, email, password):
            pass

        def _get_current_password(self):
            return ""

        def _update_password(self, new_password):
            pass

    return object.__new__(_Concrete)


class ConcreteBaseApp:
    """用于测试的 BaseApp 具体子类，实现所有抽象钩子方法."""

    def __init__(self, base_app_cls, dm, user_info):
        self._dm = dm
        self._user_info = user_info
        # 创建一个具体子类实例来绕过 ABC 限制
        class _Concrete(base_app_cls):
            def _get_window_title(self):
                return "Test"

            def _get_header_title(self):
                return "Test"

            def _get_user_display_name(self):
                return "Test"

            def _get_avatar_data(self):
                return {"name": "Test", "avatar": ""}

            def _save_avatar(self, path):
                pass

            def _get_profile_page_title(self):
                return "Test"

            def _get_avatar_label_text(self):
                return "Test"

            def _get_profile_id_label(self):
                return "Test"

            def _get_profile_id_value(self):
                return "Test"

            def _get_profile_pwd_label(self):
                return "Test"

            def _get_profile_name_label(self):
                return "Test"

            def _get_profile_name_value(self):
                return "Test"

            def _get_profile_data(self):
                return {}

            def _save_profile_entity(self, name, phone, email, password):
                pass

            def _get_current_password(self):
                return ""

            def _update_password(self, new_password):
                pass

        self._app = object.__new__(_Concrete)
        self._app.dm = dm
        self._app.user_info = user_info or {}
        self._app._logout = False
        self._app.win = MockWindow()
        self._app.logger = MagicMock()
        self._app.nav_buttons = []
        self._app.content_area = MagicMock()
        self._app.page_builders = {
            "仪表盘": MagicMock(),
            "学生管理": MagicMock(),
        }

    def __getattr__(self, name):
        return getattr(self._app, name)


class TestBaseAppHooks(unittest.TestCase):
    """测试 BaseApp 的钩子方法默认行为."""

    @patch.dict("sys.modules", _mock_modules)
    def test_hooks_are_abstract(self):
        """测试所有钩子方法为抽象方法，BaseApp 无法直接实例化."""
        from src.utils.base_app import BaseApp

        # BaseApp 是抽象类，不能直接实例化
        with self.assertRaises(TypeError):
            BaseApp()

        # 验证抽象方法存在
        abstract_methods = {
            "_get_window_title",
            "_get_header_title",
            "_get_user_display_name",
            "_get_avatar_data",
            "_save_avatar",
        }
        for method_name in abstract_methods:
            with self.subTest(method=method_name):
                self.assertIn(method_name, BaseApp.__abstractmethods__)


class TestBaseAppInit(unittest.TestCase):
    """测试 BaseApp 初始化逻辑."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("src.utils.base_app.Window", MockWindow)
    @patch("src.utils.base_app.Style", MockStyle)
    @patch("src.utils.base_app.DataManager")
    def test_init_auto_creates_dm(self, mock_dm_cls):
        """测试 __init__ 在 data_manager 为 None 时自动创建 DataManager."""
        from src.utils.base_app import BaseApp

        mock_dm = MagicMock()
        mock_dm_cls.return_value = mock_dm

        # 创建实现所有抽象钩子方法的子类
        class TestApp(BaseApp):
            def _get_window_title(self):
                return "Test"

            def _get_header_title(self):
                return "Test"

            def _get_user_display_name(self):
                return "Test"

            def _get_avatar_data(self):
                return {"name": "Test", "avatar": ""}

            def _save_avatar(self, path):
                pass

            def _get_profile_page_title(self):
                return "Test"

            def _get_avatar_label_text(self):
                return "Test"

            def _get_profile_id_label(self):
                return "Test"

            def _get_profile_id_value(self):
                return "Test"

            def _get_profile_pwd_label(self):
                return "Test"

            def _get_profile_name_label(self):
                return "Test"

            def _get_profile_name_value(self):
                return "Test"

            def _get_profile_data(self):
                return {}

            def _save_profile_entity(self, name, phone, email, password):
                pass

            def _get_current_password(self):
                return ""

            def _update_password(self, new_password):
                pass

        app = TestApp(data_manager=None, user_info=None)

        # 验证自动创建了 DataManager
        mock_dm_cls.assert_called_once()
        self.assertEqual(app.dm, mock_dm)
        self.assertEqual(app.user_info, {})
        self.assertFalse(app._logout)

    @patch.dict("sys.modules", _mock_modules)
    def test_init_uses_provided_dm(self):
        """测试 __init__ 使用传入的 data_manager."""
        from src.utils.base_app import BaseApp

        mock_dm = MagicMock()
        app = _make_base_app_instance(BaseApp)
        app.dm = mock_dm
        app.user_info = {"name": "test"}
        app._logout = False
        app.win = MockWindow()
        app.logger = MagicMock()

        self.assertEqual(app.dm, mock_dm)
        self.assertEqual(app.user_info["name"], "test")


class TestBaseAppStyles(unittest.TestCase):
    """测试样式配置方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_setup_styles(self):
        """测试 _setup_styles 调用 Style.configure 和 Style.map."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.logger = MagicMock()

        with patch("src.utils.base_app.Style") as mock_style_cls:
            mock_style = MagicMock()
            mock_style_cls.return_value = mock_style
            app._setup_styles()
            mock_style.configure.assert_called()
            mock_style.map.assert_called()


class TestBaseAppPageSwitch(unittest.TestCase):
    """测试页面切换与导航按钮逻辑."""

    @patch.dict("sys.modules", _mock_modules)
    def test_switch_page_clears_and_builds(self):
        """测试 _switch_page 清空旧内容并调用 builder."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.content_area = MagicMock()
        app.content_area.winfo_children.return_value = [MagicMock(), MagicMock()]
        app.win = MockWindow()

        builder = MagicMock()
        app._switch_page(builder)

        # 验证清空了旧内容
        for child in app.content_area.winfo_children.return_value:
            child.destroy.assert_called_once()
        # 验证调用了 builder
        builder.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    def test_set_active_button_first(self):
        """测试 _set_active_button 设置第一个按钮为活动状态."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()

        btn0 = MagicMock()
        btn1 = MagicMock()
        app.nav_buttons = [btn0, btn1]

        app._set_active_button(0)

        btn0.configure.assert_called_once_with(style="Sidebar.Active.TButton")
        btn1.configure.assert_called_once_with(
            font=("微软雅黑", 12), fg="#495057", bg="#f8f9fa"
        )

    @patch.dict("sys.modules", _mock_modules)
    def test_set_active_button_second(self):
        """测试 _set_active_button 设置第二个按钮为活动状态."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()

        btn0 = MagicMock()
        btn1 = MagicMock()
        app.nav_buttons = [btn0, btn1]

        app._set_active_button(1)

        btn0.configure.assert_called_once_with(style="Sidebar.TButton")
        btn1.configure.assert_called_once_with(
            font=("微软雅黑", 12, "bold"), fg="#00BFA5",
            bg="#E2E8F0",
        )


class TestBaseAppStatusBar(unittest.TestCase):
    """测试状态栏相关方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_show_status(self):
        """测试 _show_status 正确设置状态文本."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.status = MagicMock()

        app._show_status("测试信息", "ok")
        app.status.set.assert_called_once_with("  ✅  测试信息")

    @patch.dict("sys.modules", _mock_modules)
    def test_show_status_default_level(self):
        """测试 _show_status 默认级别为 info."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.status = MagicMock()

        app._show_status("默认信息")
        app.status.set.assert_called_once_with("  ℹ️  默认信息")

    @patch.dict("sys.modules", _mock_modules)
    def test_update_status(self):
        """测试 _update_status 使用 dm.classes（合并去重后）更新状态."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.status = MagicMock()
        app.dm = MagicMock()
        app.dm.data = {"students": {"S001": {}, "S002": {}}, "classes": ["一班", "二班"]}
        # _update_status 现在用 self.dm.classes（属性），而非独立列表
        app.dm.classes = ["一班", "二班"]

        app._update_status()
        app.status.set.assert_called_once_with("  学生 2 人 | 班级 2 个")

    @patch.dict("sys.modules", _mock_modules)
    def test_update_clock(self):
        """测试 _update_clock 设置时钟并注册 after 回调."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.clock = MagicMock()
        app.win = MockWindow()

        app._update_clock()
        app.clock.set.assert_called_once()


class TestBaseAppTreeview(unittest.TestCase):
    """测试 Treeview 辅助方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_calc_subject_widths(self):
        """测试 _calc_subject_widths 计算列宽."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        subjects = ["语文", "数学", "英语"]
        widths = app._calc_subject_widths(subjects)

        self.assertEqual(len(widths), 3)
        self.assertEqual(widths[0], max(72, len("语文") * 14))

    @patch.dict("sys.modules", _mock_modules)
    def test_calc_subject_widths_min(self):
        """测试 _calc_subject_widths 最小宽度限制."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        subjects = ["A", "B"]
        widths = app._calc_subject_widths(subjects, min_width=72)

        self.assertEqual(widths, [72, 72])

    @patch.dict("sys.modules", _mock_modules)
    def test_create_treeview(self):
        """测试 _create_treeview 创建 Treeview 并返回."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        parent = MagicMock()

        with patch("src.utils.base_app.ttk.Treeview", MockTreeview):
            tree = app._create_treeview(
                parent, columns=["学号", "姓名"], widths=[100, 80]
            )
            self.assertIsInstance(tree, MockTreeview)


class TestBaseAppExport(unittest.TestCase):
    """测试导出相关方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_export_excel_by_class_no_openpyxl(self):
        """测试 _export_excel_by_class 在 openpyxl 不可用时返回 False."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()

        with patch("src.utils.base_app.openpyxl", None):
            result = app._export_excel_by_class("/tmp/test.xlsx", "一班")
            self.assertFalse(result)

    @patch.dict("sys.modules", _mock_modules)
    def test_export_csv_by_class_success(self):
        """测试 _export_csv_by_class 成功导出 CSV."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()
        app.dm.subjects = ["语文"]
        app.dm.get_students_by_class.return_value = [
            ("S001", {"name": "张三", "scores": {"语文": 85}})
        ]
        app.dm.stats.return_value = {"total": 85, "avg": 85.0}

        m = mock_open()
        with patch("builtins.open", m):
            result = app._export_csv_by_class("/tmp/test.csv", "一班")
            self.assertTrue(result)
            m.assert_called_once_with("/tmp/test.csv", "w", newline="", encoding="utf-8-sig")

    @patch.dict("sys.modules", _mock_modules)
    def test_export_csv_by_class_empty_class(self):
        """测试 _export_csv_by_class 班级无学生时仍成功导出表头."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()
        app.dm.subjects = ["语文"]
        app.dm.get_students_by_class.return_value = []

        m = mock_open()
        with patch("builtins.open", m):
            result = app._export_csv_by_class("/tmp/test.csv", "一班")
            self.assertTrue(result)

    @patch.dict("sys.modules", _mock_modules)
    def test_export_csv_by_class_failure(self):
        """测试 _export_csv_by_class 文件写入异常时返回 False."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()
        app.dm.subjects = ["语文"]

        with patch("builtins.open", side_effect=IOError("disk full")):
            result = app._export_csv_by_class("/tmp/test.csv", "一班")
            self.assertFalse(result)


class TestBaseAppAvatar(unittest.TestCase):
    """测试头像相关方法."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("src.utils.base_app.load_avatar")
    def test_load_avatar_updates_both(self, mock_load_avatar):
        """测试 _load_avatar 同时更新个人中心和侧边栏头像."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app._get_avatar_data = MagicMock(return_value={"avatar": "/path/avatar.png"})
        app.avatar_label = MagicMock()
        app.sidebar_avatar_label = MagicMock()

        app._load_avatar()

        self.assertEqual(mock_load_avatar.call_count, 2)

    @patch.dict("sys.modules", _mock_modules)
    @patch("src.utils.base_app.load_avatar")
    def test_load_avatar_no_labels(self, mock_load_avatar):
        """测试 _load_avatar 在没有头像标签时不报错."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app._get_avatar_data = MagicMock(return_value={"avatar": ""})

        app._load_avatar()
        mock_load_avatar.assert_not_called()


class TestBaseAppLifecycle(unittest.TestCase):
    """测试生命周期方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_run_returns_dict(self):
        """测试 run 返回包含 logout 标志的字典."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app._logout = True

        result = app.run()
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("logout"))

    @patch.dict("sys.modules", _mock_modules)
    def test_on_close_saves_and_destroys(self):
        """测试 _on_close 保存数据并销毁窗口."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()
        app.win = MockWindow()
        app.logger = MagicMock()

        app._on_close()
        app.dm.save.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    def test_on_close_save_error(self):
        """测试 _on_close 保存失败时记录警告."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()
        app.dm.save.side_effect = Exception("save failed")
        app.win = MockWindow()
        app.logger = MagicMock()

        app._on_close()
        app.logger.warning.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    @patch("src.utils.base_app.confirm")
    def test_confirm_logout_yes(self, mock_confirm):
        """测试 _confirm_logout 用户确认后设置标志并关闭窗口."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()
        app.win = MockWindow()
        app.logger = MagicMock()
        app._logout = False
        mock_confirm.return_value = True

        app._confirm_logout()
        self.assertTrue(app._logout)
        app.dm.save.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    @patch("src.utils.base_app.confirm")
    def test_confirm_logout_no(self, mock_confirm):
        """测试 _confirm_logout 用户取消后不执行任何操作."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.dm = MagicMock()
        app.win = MockWindow()
        app.logger = MagicMock()
        app._logout = False
        mock_confirm.return_value = False

        app._confirm_logout()
        self.assertFalse(app._logout)
        app.dm.save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
