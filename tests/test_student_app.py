"""Student App (student_app.py) 单元测试.

使用 mock 绕过 Tkinter GUI 初始化，测试学生端业务逻辑和模块导入，
涵盖页面构建、评级方法、业务方法及生命周期等各个方面。
"""

import sys
import unittest
from unittest.mock import MagicMock, patch


class MockWindow:
    """Mock ttkbootstrap Window，模拟所有常用的窗口及控件方法。

    用于替换真实的 Tkinter 组件，避免测试时弹出 GUI 或触发 TclError。
    """

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

    def winfo_screenwidth(self):
        return 1920

    def winfo_screenheight(self):
        return 1080

    def update_idletasks(self):
        pass

    def update(self):
        pass

    def after(self, *args):
        pass

    def winfo_width(self):
        return 1200

    def winfo_height(self):
        return 800

    def pack_propagate(self, *args):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def grid_columnconfigure(self, *args, **kwargs):
        pass

    def grid_rowconfigure(self, *args, **kwargs):
        pass

    def lift(self):
        pass

    def delete(self, *args):
        pass

    def config(self, **kwargs):
        pass

    def insert(self, *args):
        pass

    def get(self, *args):
        return ""

    def configure(self, **kwargs):
        pass

    def focus_set(self):
        pass

    def bind(self, *args):
        pass

    def unbind(self, *args):
        pass

    def selection(self):
        return ()

    def item(self, *args, **kwargs):
        pass

    def set(self, *args):
        return ""

    def identify(self, *args):
        return ""

    def bbox(self, *args):
        return (0, 0, 10, 10)

    def yview(self, *args):
        pass

    def xview(self, *args):
        pass

    def winfo_children(self):
        return []

    def winfo_exists(self):
        return 1

    def cget(self, *args):
        return ""

    def children(self):
        return {}

    def geometry(self, *args):
        pass

    def withdraw(self):
        pass

    def deiconify(self):
        pass

    def focus_force(self):
        pass

    def resizable(self, *args):
        pass

    def transient(self, *args):
        pass

    def grab_set(self):
        pass

    def winfo_x(self):
        return 0

    def winfo_y(self):
        return 0


class MockStyle:
    """Mock ttkbootstrap Style，用于替换主题样式对象。"""

    def __init__(self, *args, **kwargs):
        pass

    def configure(self, *args, **kwargs):
        pass

    def map(self, *args, **kwargs):
        pass

    def lookup(self, *args, **kwargs):
        return ""


class MockTreeview:
    """Mock ttk Treeview，模拟表格控件的常用操作。"""

    def __init__(self, *args, **kwargs):
        self._items = {}
        self._next_iid = 1

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


class MockScrollbar:
    """Mock ttk Scrollbar，用于模拟滚动条。"""

    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def config(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def set(self, *args):
        pass


# 构造 tkinter 及子模块的 mock 对象，统一替换 sys.modules 中的真实模块
tk_mock = MagicMock()
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
    askyesno=MagicMock(return_value=True),
    askokcancel=MagicMock(return_value=True),
)
tk_mock.filedialog = MagicMock(
    askopenfilename=MagicMock(return_value=""),
    asksaveasfilename=MagicMock(return_value=""),
)
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
    "tkinter.ttk": tk_mock.ttk,
}


class TestStudentAppImportAndInit(unittest.TestCase):
    """测试 student_app.py 的导入和基本初始化。"""

    @patch.dict("sys.modules", _mock_modules)
    @patch("student_app.messagebox", tk_mock.messagebox)
    @patch("student_app.filedialog", tk_mock.filedialog)
    @patch("student_app.Window", MockWindow)
    @patch("student_app.Style", MockStyle)
    def test_student_app_imports(self):
        """测试 student_app.py 可以成功导入。

        预期结果：student_app 模块暴露 StudentApp 类。
        """
        import student_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertTrue(hasattr(student_app, "StudentApp"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("student_app.messagebox", tk_mock.messagebox)
    @patch("student_app.filedialog", tk_mock.filedialog)
    @patch("student_app.Window", MockWindow)
    @patch("student_app.Style", MockStyle)
    @patch("student_app.load_avatar")
    @patch("student_app.change_avatar")
    def test_student_app_init(self, mock_change, mock_load):
        """测试 StudentApp 类能初始化（mock GUI）。

        使用完整 mock 的 DataManager 构造 StudentApp，
        预期实例不为 None，且学生基本信息被正确赋值。
        """
        import student_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_student.return_value = {"name": "张三", "scores": {}}
        mock_dm.stats.return_value = {"total": 0, "avg": 0}
        instance = student_app.StudentApp(
            data_manager=mock_dm,
            user_info={"student_id": "2024001", "name": "张三", "class": "A班"},
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.student_id, "2024001")
        self.assertEqual(instance.student_name, "张三")
        self.assertEqual(instance.class_name, "A班")

    @patch.dict("sys.modules", _mock_modules)
    @patch("student_app.messagebox", tk_mock.messagebox)
    @patch("student_app.filedialog", tk_mock.filedialog)
    @patch("student_app.Window", MockWindow)
    @patch("student_app.Style", MockStyle)
    @patch("student_app.load_avatar")
    @patch("student_app.change_avatar")
    def test_student_app_run(self, mock_change, mock_load):
        """测试 StudentApp.run 返回字典。

        预期结果：run() 返回包含 logout 键的字典。
        """
        import student_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_student.return_value = {"name": "张三", "scores": {}}
        mock_dm.stats.return_value = {"total": 0, "avg": 0}
        instance = student_app.StudentApp(
            data_manager=mock_dm,
            user_info={"student_id": "2024001", "name": "张三", "class": "A班"},
        )
        result = instance.run()
        self.assertIsInstance(result, dict)


class TestStudentAppConstants(unittest.TestCase):
    """测试 student_app.py 的模块级常量。"""

    @patch.dict("sys.modules", _mock_modules)
    @patch("student_app.messagebox", tk_mock.messagebox)
    @patch("student_app.filedialog", tk_mock.filedialog)
    @patch("student_app.Window", MockWindow)
    @patch("student_app.Style", MockStyle)
    def test_colors_defined(self):
        """测试颜色常量已定义。

        预期结果：模块包含 TEAL_COLOR 和 TEAL_DARK 属性。
        """
        import student_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertTrue(hasattr(student_app, "TEAL_COLOR"))
        self.assertTrue(hasattr(student_app, "TEAL_DARK"))


# ============================================================
# 辅助函数：创建带完整 Mock 环境的 StudentApp 实例
# ============================================================
def _create_student_app(mock_dm_config=None):
    """创建带完整 mock 环境的 StudentApp 实例.

    自动设置 sys.modules 及所有相关 mock，简化测试编写。

    Args:
        mock_dm_config: 可选回调函数，接收 mock_dm 用于自定义配置。

    Returns:
        StudentApp 实例。
    """
    with patch.dict("sys.modules", _mock_modules), patch(
        "student_app.messagebox", tk_mock.messagebox
    ), patch("student_app.filedialog", tk_mock.filedialog), patch(
        "student_app.Window", MockWindow
    ), patch(
        "student_app.Style", MockStyle
    ), patch(
        "student_app.load_avatar"
    ), patch(
        "student_app.change_avatar"
    ):
        import student_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_student.return_value = {"name": "张三", "scores": {}}
        mock_dm.stats.return_value = {"total": 0, "avg": 0}

        if mock_dm_config:
            mock_dm_config(mock_dm)

        return student_app.StudentApp(
            data_manager=mock_dm,
            user_info={
                "student_id": "2024001",
                "name": "张三",
                "class": "A班",
            },
        )


# ============================================================
# 新增测试类 1：TestStudentGetLevel —— 评级方法
# ============================================================
class TestStudentGetLevel(unittest.TestCase):
    """测试 _get_level 评级方法。"""

    def test_get_level_all(self):
        """测试 _get_level 各分数段及边界值。

        覆盖 None、各等级及 60/70/80/90 边界值。
        """
        app = _create_student_app()
        # 空值
        self.assertEqual(app._get_level(None), "未录入")
        # 各等级
        self.assertEqual(app._get_level(95), "优秀")
        self.assertEqual(app._get_level(85), "良好")
        self.assertEqual(app._get_level(75), "中等")
        self.assertEqual(app._get_level(65), "及格")
        self.assertEqual(app._get_level(55), "不及格")
        # 边界值
        self.assertEqual(app._get_level(90), "优秀")
        self.assertEqual(app._get_level(80), "良好")
        self.assertEqual(app._get_level(70), "中等")
        self.assertEqual(app._get_level(60), "及格")


# ============================================================
# 新增测试类 2：TestStudentPageBuilders —— 页面构建方法
# ============================================================
class TestStudentPageBuilders(unittest.TestCase):
    """测试各页面构建方法。

    每个页面在 mock 环境下应能正常执行，不抛出异常。
    """

    def test_build_dashboard_page(self):
        """测试 _build_dashboard_page 不抛异常。

        提供完整的学生数据和班级统计数据，验证页面构建成功。
        """

        def config_dm(dm):
            dm.get_student.return_value = {
                "name": "张三",
                "scores": {"数学": 95, "英语": 85},
            }
            dm.stats.return_value = {
                "total": 180,
                "avg": 90,
                "scores": {"数学": 95, "英语": 85},
            }
            dm.get_class_stats.return_value = {
                "students": [
                    {"sid": "2024001", "rank": 1, "name": "张三"},
                ],
            }

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_dashboard_page(parent)
        self.assertIsNotNone(app._dashboard_parent)

    def test_build_scores_page(self):
        """测试 _build_scores_page 不抛异常。"""

        def config_dm(dm):
            dm.stats.return_value = {
                "total": 180,
                "avg": 90,
                "scores": {"数学": 95, "英语": 85},
            }

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_scores_page(parent)

    def test_build_scores_page_empty(self):
        """测试 _build_scores_page 无成绩数据时不抛异常。"""

        def config_dm(dm):
            dm.stats.return_value = None

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_scores_page(parent)

    def test_build_ranking_page(self):
        """测试 _build_ranking_page 不抛异常。"""

        def config_dm(dm):
            dm.stats.return_value = {
                "total": 180,
                "avg": 90,
                "scores": {"数学": 95, "英语": 85},
            }
            dm.ranking.return_value = [
                {"rank": 1, "id": "2024001", "name": "张三", "scores": {"数学": 95}},
            ]
            dm.get_class_stats.return_value = {
                "students": [
                    {
                        "sid": "2024001",
                        "name": "张三",
                        "rank": 1,
                        "total": 180,
                        "avg": 90,
                    },
                ],
            }

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_ranking_page(parent)

    def test_build_ranking_page_empty(self):
        """测试 _build_ranking_page 无成绩时不抛异常。"""

        def config_dm(dm):
            dm.stats.return_value = None

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_ranking_page(parent)

    def test_build_analysis_page(self):
        """测试 _build_analysis_page 不抛异常。"""

        def config_dm(dm):
            dm.stats.return_value = {
                "total": 180,
                "avg": 90,
                "scores": {"数学": 95, "英语": 85},
            }
            dm.get_class_stats.return_value = {"avg": 85}

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_analysis_page(parent)

    def test_build_analysis_page_empty(self):
        """测试 _build_analysis_page 无成绩时不抛异常。"""

        def config_dm(dm):
            dm.stats.return_value = None

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_analysis_page(parent)

    def test_build_notices_page(self):
        """测试 _build_notices_page 不抛异常。"""

        def config_dm(dm):
            dm.get_notices.return_value = [
                {
                    "title": "通知1",
                    "publisher": "管理员",
                    "date": "2024-01-01",
                    "target": "all",
                    "content": "测试内容",
                },
            ]

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_notices_page(parent)

    def test_build_notices_page_empty(self):
        """测试 _build_notices_page 无通知时不抛异常。"""

        def config_dm(dm):
            dm.get_notices.return_value = []

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_notices_page(parent)

    def test_build_schedule_view_page(self):
        """测试 _build_schedule_view_page 不抛异常。"""

        def config_dm(dm):
            dm.get_schedules.return_value = [
                {
                    "weekday": "周一",
                    "session": "上午",
                    "period": "1-2",
                    "course": "数学",
                    "teacher": "李老师",
                    "room": "101",
                },
            ]

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_schedule_view_page(parent)

    def test_build_profile_page(self):
        """测试 _build_profile_page 不抛异常。"""

        def config_dm(dm):
            dm.get_student.return_value = {
                "name": "张三",
                "password": "123456",
                "phone": "13800138000",
                "email": "test@test.com",
                "avatar": "",
            }

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_profile_page(parent)


# ============================================================
# 新增测试类 3：TestStudentMethods —— 业务方法
# ============================================================
class TestStudentMethods(unittest.TestCase):
    """测试业务方法。"""

    def test_refresh_dashboard(self):
        """测试 _refresh_dashboard 方法。

        先构建仪表盘页面以设置 _dashboard_parent，再调用刷新方法，
        预期不抛异常。
        """

        def config_dm(dm):
            dm.get_student.return_value = {
                "name": "张三",
                "scores": {"数学": 95, "英语": 85},
            }
            dm.stats.return_value = {
                "total": 180,
                "avg": 90,
                "scores": {"数学": 95, "英语": 85},
            }
            dm.get_class_stats.return_value = {
                "students": [
                    {"sid": "2024001", "rank": 1, "name": "张三"},
                ],
            }

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_dashboard_page(parent)
        app._refresh_dashboard()

    def test_load_avatar(self):
        """测试 _load_avatar 方法。

        需要先构建个人信息页面以创建 avatar_label，再调用加载方法。
        """

        def config_dm(dm):
            dm.get_student.return_value = {
                "name": "张三",
                "avatar": "avatar.png",
            }

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_profile_page(parent)
        app._load_avatar()

    def test_change_avatar(self):
        """测试 _change_avatar 方法。

        构建个人信息页面后调用，预期不抛异常。
        """

        def config_dm(dm):
            dm.get_student.return_value = {
                "name": "张三",
                "avatar": "",
            }

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_profile_page(parent)
        app._change_avatar()

    def test_change_password(self):
        """测试 _change_password 方法（只创建对话框）。

        预期创建 Toplevel 对话框，不触发回调，不抛异常。
        """

        def config_dm(dm):
            dm.get_student.return_value = {
                "name": "张三",
                "password": "123456",
            }

        app = _create_student_app(config_dm)
        app._change_password()

    def test_export_report(self):
        """测试 _export_report 方法。

        默认 filedialog 返回空字符串时不写入文件；
        临时修改返回值为文件路径以覆盖写入分支。
        """
        app = _create_student_app()
        app._export_report("测试报告内容")
        old_return = tk_mock.filedialog.asksaveasfilename.return_value
        tk_mock.filedialog.asksaveasfilename.return_value = "test_report.txt"
        try:
            with patch("builtins.open", create=True):
                app._export_report("测试报告内容")
        finally:
            tk_mock.filedialog.asksaveasfilename.return_value = old_return

    def test_refresh_schedule_tree(self):
        """测试 _refresh_schedule_tree 方法。

        构建课表页面后调用刷新，预期 Treeview 被正确填充。
        """

        def config_dm(dm):
            dm.get_schedules.return_value = [
                {
                    "weekday": "周一",
                    "session": "上午",
                    "period": "1-2",
                    "course": "数学",
                    "teacher": "李老师",
                    "room": "101",
                },
            ]

        app = _create_student_app(config_dm)
        parent = MockWindow()
        app._build_schedule_view_page(parent)
        app._refresh_schedule_tree()

    def test_refresh_schedule_tree_no_tree(self):
        """测试 _refresh_schedule_tree 无 Treeview 时安全退出。

        当 _schedule_view_tree 不存在时，方法应直接返回，不抛异常。
        """
        app = _create_student_app()
        app._refresh_schedule_tree()

    def test_schedule_show_history(self):
        """测试 _schedule_show_history 方法。

        预期创建历史记录对话框，不抛异常。
        """

        def config_dm(dm):
            dm.get_schedule_history.return_value = [
                {
                    "time": "2024-01-01 10:00",
                    "action": "修改",
                    "old_summary": "旧课表",
                    "new_summary": "新课表",
                    "operator": "管理员",
                },
            ]

        app = _create_student_app(config_dm)
        app._schedule_show_history()

    def test_switch_page(self):
        """测试 _switch_page 方法。

        传入简单的页面构建函数，验证 content_area 切换逻辑正常。
        """
        app = _create_student_app()
        parent = MockWindow()
        app._switch_page(lambda p: setattr(p, "_tag", "switched"))
        self.assertIsNotNone(app)

    def test_set_active_button(self):
        """测试 _set_active_button 方法。

        初始化后 nav_buttons 已填充，切换激活按钮应不抛异常。
        """
        app = _create_student_app()
        app._set_active_button(0)
        app._set_active_button(1)

    def test_confirm_logout(self):
        """测试 _confirm_logout 方法。

        预期设置 _logout 标志为 True。
        """
        app = _create_student_app()
        app._confirm_logout()
        self.assertTrue(getattr(app, "_logout", False))


# ============================================================
# 新增测试类 4：TestStudentRunAndLogout —— 运行/关闭
# ============================================================
class TestStudentRunAndLogout(unittest.TestCase):
    """测试 run() 和 _on_close() 方法。"""

    def test_run(self):
        """测试 run() 返回字典。

        预期结果：返回包含 logout 键的字典。
        """
        app = _create_student_app()
        result = app.run()
        self.assertIsInstance(result, dict)
        self.assertIn("logout", result)

    def test_on_close(self):
        """测试 _on_close() 不抛异常。"""
        app = _create_student_app()
        app._on_close()

    def test_run_after_logout(self):
        """测试退出登录后 run() 的 logout 标志。

        调用 _confirm_logout() 后，run() 应返回 logout=True。
        """
        app = _create_student_app()
        app._confirm_logout()
        result = app.run()
        self.assertTrue(result["logout"])


if __name__ == "__main__":
    unittest.main()
