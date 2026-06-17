"""Teacher App (teacher_app.py) 单元测试.

使用 mock 绕过 Tkinter GUI 初始化，测试教师端业务逻辑和模块导入，
涵盖页面构建、静态方法、业务方法及生命周期等各个方面。
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

    def iconbitmap(self, *args):
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

    def create_image(self, *args, **kwargs):
        pass

    def create_text(self, *args, **kwargs):
        pass

    def create_window(self, *args, **kwargs):
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

    def winfo_exists(self):
        return 1

    def __getitem__(self, key):
        return ["col1", "col2"]


class MockScrollbar:
    """Mock ttk Scrollbar，用于模拟滚动条。"""

    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def config(self, **kwargs):
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


class TestTeacherAppImportAndInit(unittest.TestCase):
    """测试 teacher_app.py 的导入和基本初始化。"""

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    def test_teacher_app_imports(self):
        """测试 teacher_app.py 可以成功导入。

        预期结果：teacher_app 模块暴露 TeacherApp 类。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertTrue(hasattr(teacher_app, "TeacherApp"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_teacher_app_init(self, mock_change, mock_load):
        """测试 TeacherApp 类能初始化（mock GUI）。

        使用完整 mock 的 DataManager 构造 TeacherApp，
        预期实例不为 None，且 teacher_id 与 teacher_name 被正确赋值。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.data = {"teachers": {}}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_teacher.return_value = {"name": "王老师"}
        mock_dm.get_course.return_value = None
        mock_dm.get_student.return_value = None
        mock_dm.get_attendance.return_value = {}
        mock_dm.get_attendance_dates.return_value = []
        mock_dm.get_student_attendance.return_value = []
        mock_dm.get_attendance_stats.return_value = {
            "total": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "rate": 0.0,
        }
        instance = teacher_app.TeacherApp(
            data_manager=mock_dm,
            user_info={"teacher_id": "T001", "name": "王老师"},
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.teacher_id, "T001")
        self.assertEqual(instance.teacher_name, "王老师")

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_teacher_app_run(self, mock_change, mock_load):
        """测试 TeacherApp.run 返回字典。

        预期结果：run() 返回包含 logout 键的字典。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.data = {"teachers": {}}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_teacher.return_value = {"name": "王老师"}
        mock_dm.get_course.return_value = None
        mock_dm.get_student.return_value = None
        mock_dm.get_attendance.return_value = {}
        mock_dm.get_attendance_dates.return_value = []
        mock_dm.get_student_attendance.return_value = []
        mock_dm.get_attendance_stats.return_value = {
            "total": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "rate": 0.0,
        }
        instance = teacher_app.TeacherApp(
            data_manager=mock_dm,
            user_info={"teacher_id": "T001", "name": "王老师"},
        )
        result = instance.run()
        self.assertIsInstance(result, dict)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_teacher_app_logout_flag(self, mock_change, mock_load):
        """测试退出登录标志初始为 False。

        预期结果：新创建的 TeacherApp 实例 _logout_flag 为 False。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.data = {"teachers": {}}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_teacher.return_value = {"name": "王老师"}
        mock_dm.get_course.return_value = None
        mock_dm.get_student.return_value = None
        mock_dm.get_attendance.return_value = {}
        mock_dm.get_attendance_dates.return_value = []
        mock_dm.get_student_attendance.return_value = []
        mock_dm.get_attendance_stats.return_value = {
            "total": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "rate": 0.0,
        }
        instance = teacher_app.TeacherApp(
            data_manager=mock_dm,
            user_info={"teacher_id": "T001", "name": "王老师"},
        )
        self.assertFalse(instance._logout_flag)


class TestTeacherAppConstants(unittest.TestCase):
    """测试 teacher_app.py 的模块级常量。"""

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    def test_colors_defined(self):
        """测试颜色常量已定义。

        预期结果：模块包含 TEAL_COLOR 和 TEAL_DARK 属性。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertTrue(hasattr(teacher_app, "TEAL_COLOR"))
        self.assertTrue(hasattr(teacher_app, "TEAL_DARK"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    def test_excel_flag(self):
        """测试 EX_OK 标志。

        预期结果：EX_OK 为布尔值之一。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertIn(teacher_app.EX_OK, [True, False])

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    def test_matplotlib_flag(self):
        """测试 MAT_OK 标志。

        预期结果：MAT_OK 为布尔值之一。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertIn(teacher_app.MAT_OK, [True, False])


# ==================== 新增测试类 ====================


class TestTeacherStaticMethods(unittest.TestCase):
    """测试 TeacherApp 的静态方法和工具方法。"""

    def _create_mock_dm(self):
        """创建 mock DataManager，提供教师端常用的默认返回值。"""
        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.data = {"teachers": {}}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_teacher.return_value = {"name": "王老师", "avatar": ""}
        mock_dm.get_course.return_value = None
        mock_dm.get_student.return_value = None
        mock_dm.get_attendance.return_value = {}
        mock_dm.get_attendance_dates.return_value = []
        mock_dm.get_student_attendance.return_value = []
        mock_dm.get_attendance_stats.return_value = {
            "total": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "rate": 0.0,
        }
        mock_dm.get_students_by_class.return_value = []
        mock_dm.authenticate_teacher.return_value = True
        mock_dm.save = MagicMock()
        mock_dm.update_teacher = MagicMock()
        return mock_dm

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    def test_get_level(self):
        """测试 _get_level 静态方法。

        验证各分数段对应的等级，并确认 None 输入会触发 TypeError。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertEqual(teacher_app.TeacherApp._get_level(95), "优秀")
        self.assertEqual(teacher_app.TeacherApp._get_level(85), "良好")
        self.assertEqual(teacher_app.TeacherApp._get_level(75), "良好")
        self.assertEqual(teacher_app.TeacherApp._get_level(65), "及格")
        self.assertEqual(teacher_app.TeacherApp._get_level(55), "不及格")
        # None 会触发 TypeError（None >= 90）
        with self.assertRaises(TypeError):
            teacher_app.TeacherApp._get_level(None)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    def test_get_level_tag(self):
        """测试 _get_level_tag 静态方法。

        验证各分数段对应的 (tag, level) 元组。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertEqual(
            teacher_app.TeacherApp._get_level_tag(95),
            ("excellent", "优秀"),
        )
        self.assertEqual(
            teacher_app.TeacherApp._get_level_tag(85),
            ("good", "良好"),
        )
        self.assertEqual(
            teacher_app.TeacherApp._get_level_tag(75),
            ("good", "良好"),
        )
        self.assertEqual(
            teacher_app.TeacherApp._get_level_tag(65),
            ("pass_", "及格"),
        )
        self.assertEqual(
            teacher_app.TeacherApp._get_level_tag(55),
            ("fail", "不及格"),
        )
        self.assertEqual(
            teacher_app.TeacherApp._get_level_tag(50),
            ("fail", "不及格"),
        )

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    def test_mg_sort_key(self):
        """测试 _mg_sort_key 静态方法。

        验证数字值转为 float、字符串转为小写、"-"/空/None 返回 -1 等分支。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        # 数字值
        self.assertEqual(
            teacher_app.TeacherApp._mg_sort_key(["张三", "85"], 1),
            85.0,
        )
        # 字符串值
        self.assertEqual(
            teacher_app.TeacherApp._mg_sort_key(["张三", "A"], 1),
            "a",
        )
        # "-" 返回 -1
        self.assertEqual(
            teacher_app.TeacherApp._mg_sort_key(["张三", "-"], 1),
            -1,
        )
        # 空字符串返回 -1
        self.assertEqual(
            teacher_app.TeacherApp._mg_sort_key(["张三", ""], 1),
            -1,
        )
        # None 返回 -1
        self.assertEqual(
            teacher_app.TeacherApp._mg_sort_key(["张三", None], 1),
            -1,
        )


class TestTeacherPageBuilders(unittest.TestCase):
    """测试 TeacherApp 的各个页面构建方法。

    每个页面构建方法在 mock 环境下应能正常执行，不抛出异常。
    """

    def _create_mock_dm(self):
        """创建 mock DataManager，配置教师端常用默认值。"""
        mock_dm = MagicMock()
        mock_dm.subjects = ["语文", "数学", "英语"]
        mock_dm.students = {}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.data = {"teachers": {}}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_teacher.return_value = {"name": "王老师", "avatar": ""}
        mock_dm.get_course.return_value = None
        mock_dm.get_student.return_value = None
        mock_dm.get_attendance.return_value = {}
        mock_dm.get_attendance_dates.return_value = []
        mock_dm.get_student_attendance.return_value = []
        mock_dm.get_attendance_stats.return_value = {
            "total": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "rate": 0.0,
        }
        mock_dm.get_students_by_class.return_value = []
        mock_dm.authenticate_teacher.return_value = True
        mock_dm.save = MagicMock()
        mock_dm.update_teacher = MagicMock()
        return mock_dm

    def _create_app(self, teacher_app_module, mock_dm):
        """创建 TeacherApp 实例。

        Args:
            teacher_app_module: 已导入的 teacher_app 模块。
            mock_dm: mock DataManager 实例。

        Returns:
            TeacherApp 实例。
        """
        instance = teacher_app_module.TeacherApp(
            data_manager=mock_dm,
            user_info={"teacher_id": "T001", "name": "王老师"},
        )
        return instance

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_dashboard_page(self, mock_change, mock_load):
        """测试 _build_dashboard_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_dashboard_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_grade_input_page(self, mock_change, mock_load):
        """测试 _build_grade_input_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_grade_input_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_class_stats_page(self, mock_change, mock_load):
        """测试 _build_class_stats_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_class_stats_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_profile_page(self, mock_change, mock_load):
        """测试 _build_profile_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.get_teacher.return_value = {
            "name": "王老师",
            "avatar": "",
            "password": "pass123",
            "phone": "13800138000",
            "email": "wang@school.edu",
        }
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_profile_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_attendance_page(self, mock_change, mock_load):
        """测试 _build_attendance_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.get_teacher_courses = MagicMock(return_value={})
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_attendance_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_grade_report_page(self, mock_change, mock_load):
        """测试 _build_grade_report_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_grade_report_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_student_comments_page(self, mock_change, mock_load):
        """测试 _build_student_comments_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_student_comments_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_notices_page(self, mock_change, mock_load):
        """测试 _build_notices_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_notices_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_schedule_view_page(self, mock_change, mock_load):
        """测试 _build_schedule_view_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_schedule_view_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_excel_page(self, mock_change, mock_load):
        """测试 _build_excel_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_excel_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_class_page(self, mock_change, mock_load):
        """测试 _build_class_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_class_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_manage_page(self, mock_change, mock_load):
        """测试 _build_manage_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_manage_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_search_page(self, mock_change, mock_load):
        """测试 _build_search_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_search_page(parent)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_build_chart_page(self, mock_change, mock_load):
        """测试 _build_chart_page 页面构建。

        预期结果：页面构建不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        app._build_chart_page(parent)
        self.assertTrue(True)


class TestTeacherMethods(unittest.TestCase):
    """测试 TeacherApp 的业务方法。"""

    def _create_mock_dm(self):
        """创建 mock DataManager，提供教师端常用默认值。"""
        mock_dm = MagicMock()
        mock_dm.subjects = ["语文", "数学", "英语"]
        mock_dm.students = {}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.data = {"teachers": {}}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_teacher.return_value = {"name": "王老师", "avatar": ""}
        mock_dm.get_course.return_value = None
        mock_dm.get_student.return_value = None
        mock_dm.get_attendance.return_value = {}
        mock_dm.get_attendance_dates.return_value = []
        mock_dm.get_student_attendance.return_value = []
        mock_dm.get_attendance_stats.return_value = {
            "total": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "rate": 0.0,
        }
        mock_dm.get_students_by_class.return_value = []
        mock_dm.authenticate_teacher.return_value = True
        mock_dm.save = MagicMock()
        mock_dm.update_teacher = MagicMock()
        return mock_dm

    def _create_app(self, teacher_app_module, mock_dm):
        """创建 TeacherApp 实例。

        Args:
            teacher_app_module: 已导入的 teacher_app 模块。
            mock_dm: mock DataManager 实例。

        Returns:
            TeacherApp 实例。
        """
        instance = teacher_app_module.TeacherApp(
            data_manager=mock_dm,
            user_info={"teacher_id": "T001", "name": "王老师"},
        )
        return instance

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_get_avg_pass_rate_no_courses(self, mock_change, mock_load):
        """测试 _get_avg_pass_rate 无课程时返回 0。

        当教师没有任何课程时，预期平均及格率为 0。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        result = app._get_avg_pass_rate()
        self.assertEqual(result, 0)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_get_avg_pass_rate_with_courses(self, mock_change, mock_load):
        """测试 _get_avg_pass_rate 有课程时计算平均值。

        模拟两门课程及格率分别为 80% 和 90%，预期平均为 85.0%。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.data = {
            "teachers": {
                "T001": {
                    "name": "王老师",
                    "course_ids": ["C001", "C002"],
                }
            }
        }
        mock_dm.courses = {
            "C001": {"name": "语文", "class_name": "一班"},
            "C002": {"name": "数学", "class_name": "二班"},
        }
        # 先创建 app（init 阶段会调用 _get_avg_pass_rate，但 analyze_subject 返回 None）
        app = self._create_app(teacher_app, mock_dm)
        # 再设置 side_effect 用于后续测试调用
        mock_dm.analyze_subject.side_effect = [
            {"pass_rate": 80},
            {"pass_rate": 90},
        ]
        result = app._get_avg_pass_rate()
        self.assertEqual(result, 85.0)
        mock_dm.analyze_subject.side_effect = None

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_get_teacher_courses_no_teacher(self, mock_change, mock_load):
        """测试 _get_teacher_courses 教师不存在时返回空字典。

        当 data["teachers"] 中不存在当前教师时，预期返回 {}。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.data = {"teachers": {}}
        app = self._create_app(teacher_app, mock_dm)
        result = app._get_teacher_courses()
        self.assertEqual(result, {})

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_get_teacher_courses_with_data(self, mock_change, mock_load):
        """测试 _get_teacher_courses 有课程数据时返回正确映射。

        预期返回包含课程 ID 及名称的字典。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.data = {
            "teachers": {
                "T001": {
                    "name": "王老师",
                    "course_ids": ["C001", "C002"],
                }
            }
        }
        mock_dm.courses = {
            "C001": {"name": "语文", "class_name": "一班"},
            "C002": {"name": "数学", "class_name": "二班"},
        }
        app = self._create_app(teacher_app, mock_dm)
        result = app._get_teacher_courses()
        self.assertEqual(len(result), 2)
        self.assertIn("C001", result)
        self.assertIn("C002", result)
        self.assertEqual(result["C001"]["name"], "语文")

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_load_avatar(self, mock_change, mock_load):
        """测试 _load_avatar 方法。

        预期结果：调用 load_avatar 工具函数完成头像加载。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.get_teacher.return_value = {"name": "王老师", "avatar": "avatar.png"}
        app = self._create_app(teacher_app, mock_dm)
        app.avatar_label = MockWindow()
        app.sidebar_avatar_label = MockWindow()
        app._load_avatar()
        mock_load.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_change_avatar(self, mock_change, mock_load):
        """测试 _change_avatar 方法。

        预期结果：调用 change_avatar 工具函数完成头像更换。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.get_teacher.return_value = {"name": "王老师", "avatar": ""}
        app = self._create_app(teacher_app, mock_dm)
        app.avatar_label = MockWindow()
        app._change_avatar()
        mock_change.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_change_password(self, mock_change, mock_load):
        """测试 _change_password 方法。

        预期结果：创建修改密码对话框，不抛异常即可。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        app._change_password()
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_switch_page(self, mock_change, mock_load):
        """测试 _switch_page 方法。

        预期结果：传入页面构建函数后能正常切换，不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)

        def dummy_builder(parent):
            pass

        app._switch_page(dummy_builder)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_set_active_button(self, mock_change, mock_load):
        """测试 _set_active_button 方法。

        预期结果：切换激活按钮索引后不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        app._set_active_button(0)
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_show_status(self, mock_change, mock_load):
        """测试 _show_status 方法。

        预期结果：不同级别（info/ok/warn/err）均能正常设置状态栏文本。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        app.status = MagicMock()
        app._show_status("测试消息", "info")
        app.status.set.assert_called_once()
        app._show_status("成功", "ok")
        app._show_status("警告", "warn")
        app._show_status("错误", "err")

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_update_status(self, mock_change, mock_load):
        """测试 _update_status 方法。

        预期结果：根据学生数和班级数更新状态栏文本。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.students = {"S001": {}, "S002": {}}
        mock_dm.classes = ["一班", "二班"]
        app = self._create_app(teacher_app, mock_dm)
        app.status = MagicMock()
        app._update_status()
        app.status.set.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_refresh_all_pages_no_attrs(self, mock_change, mock_load):
        """测试 _refresh_all_pages 无属性时静默跳过。

        当实例尚未构建任何页面时，预期方法安全返回，不抛异常。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        app._refresh_all_pages()
        self.assertTrue(True)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_calc_subject_widths(self, mock_change, mock_load):
        """测试 _calc_subject_widths 方法。

        验证返回的列宽列表长度与科目数一致，且每项不小于最小宽度 72。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        subjects = ["语文", "数学", "英语综合"]
        result = app._calc_subject_widths(subjects)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(w >= 72 for w in result))

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_create_treeview(self, mock_change, mock_load):
        """测试 _create_treeview 方法。

        预期结果：返回非 None 的 Treeview 实例（mock）。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        parent = MockWindow()
        columns = ["学号", "姓名", "成绩"]
        widths = [80, 100, 80]
        tree = app._create_treeview(parent, columns, widths)
        self.assertIsNotNone(tree)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_check_excel_available_true(self, mock_change, mock_load):
        """测试 _check_excel_available 当 EX_OK 为 True。

        预期结果：返回 True，表示 Excel 功能可用。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        with patch.object(teacher_app, "EX_OK", True):
            result = app._check_excel_available()
            self.assertTrue(result)

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_check_excel_available_false(self, mock_change, mock_load):
        """测试 _check_excel_available 当 EX_OK 为 False。

        预期结果：返回 False，表示 Excel 功能不可用。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        with patch.object(teacher_app, "EX_OK", False):
            result = app._check_excel_available()
            self.assertFalse(result)


class TestTeacherLifecycle(unittest.TestCase):
    """测试 TeacherApp 的生命周期方法，包括 run()、关闭和退出登录。"""

    def _create_mock_dm(self):
        """创建 mock DataManager，提供教师端常用默认值。"""
        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.data = {"teachers": {}}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.get_teacher.return_value = {"name": "王老师", "avatar": ""}
        mock_dm.get_course.return_value = None
        mock_dm.get_student.return_value = None
        mock_dm.get_attendance.return_value = {}
        mock_dm.get_attendance_dates.return_value = []
        mock_dm.get_student_attendance.return_value = []
        mock_dm.get_attendance_stats.return_value = {
            "total": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "rate": 0.0,
        }
        mock_dm.get_students_by_class.return_value = []
        mock_dm.authenticate_teacher.return_value = True
        mock_dm.save = MagicMock()
        mock_dm.update_teacher = MagicMock()
        return mock_dm

    def _create_app(self, teacher_app_module, mock_dm):
        """创建 TeacherApp 实例。

        Args:
            teacher_app_module: 已导入的 teacher_app 模块。
            mock_dm: mock DataManager 实例。

        Returns:
            TeacherApp 实例。
        """
        instance = teacher_app_module.TeacherApp(
            data_manager=mock_dm,
            user_info={"teacher_id": "T001", "name": "王老师"},
        )
        return instance

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_run(self, mock_change, mock_load):
        """测试 run 方法。

        预期结果：返回字典，包含 logout 键且默认值为 False。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        result = app.run()
        self.assertIsInstance(result, dict)
        self.assertIn("logout", result)
        self.assertFalse(result["logout"])

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_on_close(self, mock_change, mock_load):
        """测试 _on_close 方法。

        预期结果：调用 DataManager.save() 保存数据。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        app._on_close()
        mock_dm.save.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_on_close_save_error(self, mock_change, mock_load):
        """测试 _on_close 保存异常时仍能正常销毁。

        模拟 save() 抛出异常，预期不会阻断窗口关闭流程。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        mock_dm.save.side_effect = Exception("保存失败")
        app = self._create_app(teacher_app, mock_dm)
        app._on_close()
        mock_dm.save.assert_called_once()

    @patch.dict("sys.modules", _mock_modules)
    @patch("teacher_app.messagebox", tk_mock.messagebox)
    @patch("teacher_app.filedialog", tk_mock.filedialog)
    @patch("teacher_app.simpledialog", tk_mock.simpledialog)
    @patch("teacher_app.Window", MockWindow)
    @patch("teacher_app.Style", MockStyle)
    @patch("teacher_app.load_avatar")
    @patch("teacher_app.change_avatar")
    def test_logout(self, mock_change, mock_load):
        """测试 _logout 方法。

        预期结果：设置 _logout_flag 为 True 并调用 save()。
        """
        import teacher_app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = self._create_mock_dm()
        app = self._create_app(teacher_app, mock_dm)
        self.assertFalse(app._logout_flag)
        app._logout()
        self.assertTrue(app._logout_flag)
        mock_dm.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
