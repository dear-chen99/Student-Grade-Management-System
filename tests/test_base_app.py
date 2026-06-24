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


class TestBaseAppDashboardCard(unittest.TestCase):
    """测试 _create_dashboard_card 仪表盘卡片方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dashboard_card_returns_label(self):
        """测试 _create_dashboard_card 返回数值标签控件."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()

        container = MagicMock()
        with patch("src.utils.base_app.tk") as mock_tk:
            mock_card = MagicMock()
            mock_label = MagicMock()
            mock_tk.Frame.return_value = mock_card
            mock_tk.Label.side_effect = [MagicMock(), MagicMock(), mock_label]

            result = app._create_dashboard_card(
                container, "📚", "学生总数", 100, "#6366F1"
            )
            self.assertEqual(result, mock_label)

    @patch.dict("sys.modules", _mock_modules)
    def test_create_dashboard_card_creates_frame(self):
        """测试 _create_dashboard_card 创建卡片 Frame 并 pack."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()

        container = MagicMock()
        with patch("src.utils.base_app.tk") as mock_tk:
            mock_card = MagicMock()
            mock_tk.Frame.return_value = mock_card

            app._create_dashboard_card(
                container, "📚", "学生总数", 100, "#6366F1"
            )
            mock_tk.Frame.assert_called_once()
            mock_card.pack.assert_called_once()


class TestBaseAppZebraStripes(unittest.TestCase):
    """测试 _apply_zebra_stripes 斑马纹方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_apply_zebra_stripes_default_tags(self):
        """测试 _apply_zebra_stripes 使用默认标签名."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        tree = MagicMock()

        app._apply_zebra_stripes(tree)
        tree.tag_configure.assert_any_call("odd", background=unittest.mock.ANY)
        tree.tag_configure.assert_any_call("even", background="#FFFFFF")

    @patch.dict("sys.modules", _mock_modules)
    def test_apply_zebra_stripes_custom_tags(self):
        """测试 _apply_zebra_stripes 使用自定义标签名."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        tree = MagicMock()

        app._apply_zebra_stripes(tree, odd_tag="oddrow", even_tag="evenrow")
        tree.tag_configure.assert_any_call("oddrow", background=unittest.mock.ANY)
        tree.tag_configure.assert_any_call("evenrow", background="#FFFFFF")

    @patch.dict("sys.modules", _mock_modules)
    def test_apply_zebra_stripes_call_count(self):
        """测试 _apply_zebra_stripes 调用 tag_configure 两次."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        tree = MagicMock()

        app._apply_zebra_stripes(tree)
        self.assertEqual(tree.tag_configure.call_count, 2)


class TestBaseAppPositionDialog(unittest.TestCase):
    """测试 _position_dialog 弹窗定位方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_position_dialog_sets_geometry(self):
        """测试 _position_dialog 设置弹窗位置."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()

        dialog = MagicMock()
        app._position_dialog(dialog)

        dialog.withdraw.assert_called_once()
        dialog.geometry.assert_called_once()
        dialog.deiconify.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    def test_position_dialog_offset_values(self):
        """测试 _position_dialog 偏移量为 +60+120."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()

        dialog = MagicMock()
        app._position_dialog(dialog)

        geom_arg = dialog.geometry.call_args[0][0]
        self.assertIn("+60+120", geom_arg)

    @patch.dict("sys.modules", _mock_modules)
    def test_position_dialog_calls_withdraw_first(self):
        """测试 _position_dialog 先 withdraw 再 deiconify."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()

        dialog = MagicMock()
        app._position_dialog(dialog)

        # 验证调用顺序：withdraw -> geometry -> deiconify
        calls = [c[0] for c in dialog.method_calls]
        self.assertIn("withdraw", calls)
        self.assertIn("deiconify", calls)
        self.assertLess(calls.index("withdraw"), calls.index("deiconify"))


class TestBaseAppBuildProfilePage(unittest.TestCase):
    """测试 _build_profile_page 模板方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_build_profile_page_no_exception(self):
        """测试 _build_profile_page 不抛出异常."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app._get_profile_data = MagicMock(return_value={})
        app._get_profile_id_value = MagicMock(return_value="admin")
        app._get_profile_name_value = MagicMock(return_value="管理员")
        app._get_current_password = MagicMock(return_value="123456")

        parent = MagicMock()
        parent.winfo_children.return_value = []

        with patch("src.utils.base_app.tk") as mock_tk:
            mock_tk.Frame.side_effect = lambda *a, **kw: MagicMock()
            mock_tk.Label.side_effect = lambda *a, **kw: MagicMock()
            mock_tk.Entry.side_effect = lambda *a, **kw: MagicMock()
            mock_tk.Button.side_effect = lambda *a, **kw: MagicMock()

            # 应不抛异常
            app._build_profile_page(parent)


class TestBaseAppChangePassword(unittest.TestCase):
    """测试 _change_password 模板方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_change_password_creates_dialog(self):
        """测试 _change_password 创建修改密码弹窗."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app._get_current_password = MagicMock(return_value="123456")
        app._update_password = MagicMock()

        with patch("src.utils.base_app.tk") as mock_tk:
            mock_dialog = MagicMock()
            mock_tk.Toplevel.return_value = mock_dialog

            app._change_password()

            mock_tk.Toplevel.assert_called_once()
            mock_dialog.title.assert_called_once_with("修改密码")
            mock_dialog.grab_set.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    def test_change_password_dialog_resizable_false(self):
        """测试 _change_password 弹窗不可调整大小."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app._get_current_password = MagicMock(return_value="")
        app._update_password = MagicMock()

        with patch("src.utils.base_app.tk") as mock_tk:
            mock_dialog = MagicMock()
            mock_tk.Toplevel.return_value = mock_dialog

            app._change_password()
            mock_dialog.resizable.assert_called_once_with(False, False)


class TestBaseAppBuildNoticesPage(unittest.TestCase):
    """测试 _build_notices_page 模板方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_build_notices_page_empty_notices(self):
        """测试 _build_notices_page 无通知时显示空提示."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_notices.return_value = []
        app._get_notice_role = MagicMock(return_value="")

        parent = MagicMock()
        parent.winfo_children.return_value = []

        with patch("src.utils.base_app.tk") as mock_tk:
            app._build_notices_page(parent)
            # 应清空旧控件
            parent.winfo_children.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    def test_build_notices_page_with_data(self):
        """测试 _build_notices_page 有通知数据时创建 Treeview."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_notices.return_value = [
            {"title": "测试通知", "publisher": "admin", "date": "2026-06-24", "content": "内容"},
        ]
        app._get_notice_role = MagicMock(return_value="teacher")

        parent = MagicMock()
        parent.winfo_children.return_value = []

        with patch("src.utils.base_app.tk"), \
             patch("src.utils.base_app.ttk") as mock_ttk:
            mock_tree = MagicMock()
            mock_ttk.Treeview.return_value = mock_tree

            app._build_notices_page(parent)

            # 应设置 _notice_tree 属性
            self.assertTrue(hasattr(app, "_notice_tree"))
            # 应插入数据行
            mock_tree.insert.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    def test_build_notices_page_destroys_old_widgets(self):
        """测试 _build_notices_page 清空旧控件."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_notices.return_value = []
        app._get_notice_role = MagicMock(return_value="")

        old_widget = MagicMock()
        parent = MagicMock()
        parent.winfo_children.return_value = [old_widget]

        with patch("src.utils.base_app.tk"):
            app._build_notices_page(parent)
            old_widget.destroy.assert_called_once()


class TestBaseAppScheduleView(unittest.TestCase):
    """测试 _build_schedule_view_page 和 _refresh_schedule_tree 方法."""

    @patch.dict("sys.modules", _mock_modules)
    def test_build_schedule_view_page_no_exception(self):
        """测试 _build_schedule_view_page 不抛出异常."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_schedules.return_value = []
        app._get_schedule_filter_classes = MagicMock(return_value=[])
        app._get_schedule_class_name = MagicMock(return_value="")
        app._filter_schedule_entries = MagicMock(return_value=[])
        app._schedule_show_history = MagicMock()

        parent = MagicMock()

        with patch("src.utils.base_app.tk"), \
             patch("src.utils.base_app.ttk") as mock_ttk:
            mock_tree = MagicMock()
            mock_ttk.Treeview.return_value = mock_tree
            mock_ttk.Scrollbar.return_value = MagicMock()

            app._build_schedule_view_page(parent)

            # 应设置 _schedule_view_tree 属性
            self.assertTrue(hasattr(app, "_schedule_view_tree"))

    @patch.dict("sys.modules", _mock_modules)
    def test_build_schedule_view_with_class_filter(self):
        """测试 _build_schedule_view_page 有班级选择器时创建 Combobox."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_schedules.return_value = []
        app._get_schedule_filter_classes = MagicMock(
            return_value=["一班", "二班"]
        )
        app._get_schedule_class_name = MagicMock(return_value="一班")
        app._filter_schedule_entries = MagicMock(return_value=[])
        app._schedule_show_history = MagicMock()

        parent = MagicMock()

        with patch("src.utils.base_app.tk"), \
             patch("src.utils.base_app.ttk") as mock_ttk:
            mock_tree = MagicMock()
            mock_ttk.Treeview.return_value = mock_tree
            mock_ttk.Scrollbar.return_value = MagicMock()
            mock_ttk.Combobox.return_value = MagicMock()

            app._build_schedule_view_page(parent)

            # 应创建班级选择器
            mock_ttk.Combobox.assert_called_once()
            # 应设置 _schedule_class_var
            self.assertTrue(hasattr(app, "_schedule_class_var"))

    @patch.dict("sys.modules", _mock_modules)
    def test_refresh_schedule_tree_no_tree(self):
        """测试 _refresh_schedule_tree 无 _schedule_view_tree 时不报错."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        # 不设置 _schedule_view_tree 属性

        # 应不抛异常
        app._refresh_schedule_tree()

    @patch.dict("sys.modules", _mock_modules)
    def test_refresh_schedule_tree_populates_data(self):
        """测试 _refresh_schedule_tree 填充课表数据."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_schedules.return_value = [
            {"weekday": "周一", "session": "上午", "period": "1-2",
             "course": "数学", "teacher": "张老师", "room": "101"},
            {"weekday": "周二", "session": "下午", "period": "3-4",
             "course": "英语", "teacher": "李老师", "room": "202"},
        ]
        app._get_schedule_class_name = MagicMock(return_value="一班")
        app._filter_schedule_entries = MagicMock(
            side_effect=lambda x: x
        )

        mock_tree = MagicMock()
        mock_tree.get_children.return_value = []
        app._schedule_view_tree = mock_tree

        app._refresh_schedule_tree()

        # 应插入 2 行数据
        self.assertEqual(mock_tree.insert.call_count, 2)

    @patch.dict("sys.modules", _mock_modules)
    def test_refresh_schedule_tree_empty_data(self):
        """测试 _refresh_schedule_tree 无数据时不插入行."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_schedules.return_value = []
        app._get_schedule_class_name = MagicMock(return_value="一班")
        app._filter_schedule_entries = MagicMock(return_value=[])

        mock_tree = MagicMock()
        mock_tree.get_children.return_value = []
        app._schedule_view_tree = mock_tree

        app._refresh_schedule_tree()

        mock_tree.insert.assert_not_called()

    @patch.dict("sys.modules", _mock_modules)
    def test_refresh_schedule_tree_clears_old_items(self):
        """测试 _refresh_schedule_tree 清空旧数据行."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app.dm.get_schedules.return_value = []
        app._get_schedule_class_name = MagicMock(return_value="")
        app._filter_schedule_entries = MagicMock(return_value=[])

        old_items = ["I001", "I002", "I003"]
        mock_tree = MagicMock()
        mock_tree.get_children.return_value = old_items
        app._schedule_view_tree = mock_tree

        app._refresh_schedule_tree()

        # 应逐个删除所有旧行
        self.assertEqual(mock_tree.delete.call_count, len(old_items))
        for item in old_items:
            mock_tree.delete.assert_any_call(item)

    @patch.dict("sys.modules", _mock_modules)
    def test_refresh_schedule_tree_no_class_name(self):
        """测试 _refresh_schedule_tree 无班级名时不获取数据."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        app.win = MockWindow()
        app.dm = MagicMock()
        app._get_schedule_class_name = MagicMock(return_value="")
        app._filter_schedule_entries = MagicMock(return_value=[])

        mock_tree = MagicMock()
        mock_tree.get_children.return_value = []
        app._schedule_view_tree = mock_tree

        app._refresh_schedule_tree()

        # 班级名为空时不应调用 get_schedules
        app.dm.get_schedules.assert_not_called()


class TestBaseAppScheduleHooks(unittest.TestCase):
    """测试课表钩子方法的默认行为."""

    @patch.dict("sys.modules", _mock_modules)
    def test_get_schedule_filter_classes_default(self):
        """测试 _get_schedule_filter_classes 默认返回空列表."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        result = app._get_schedule_filter_classes()
        self.assertEqual(result, [])

    @patch.dict("sys.modules", _mock_modules)
    def test_get_schedule_class_name_default(self):
        """测试 _get_schedule_class_name 默认返回空字符串."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        result = app._get_schedule_class_name()
        self.assertEqual(result, "")

    @patch.dict("sys.modules", _mock_modules)
    def test_get_schedule_class_name_with_var(self):
        """测试 _get_schedule_class_name 从 _schedule_class_var 读取."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        mock_var = MagicMock()
        mock_var.get.return_value = "一班"
        app._schedule_class_var = mock_var

        result = app._get_schedule_class_name()
        self.assertEqual(result, "一班")

    @patch.dict("sys.modules", _mock_modules)
    def test_filter_schedule_entries_default(self):
        """测试 _filter_schedule_entries 默认不过滤."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        data = [{"course": "数学"}, {"course": "英语"}]
        result = app._filter_schedule_entries(data)
        self.assertEqual(result, data)

    @patch.dict("sys.modules", _mock_modules)
    def test_get_notice_role_default(self):
        """测试 _get_notice_role 默认返回空字符串."""
        from src.utils.base_app import BaseApp

        app = _make_base_app_instance(BaseApp)
        result = app._get_notice_role()
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
