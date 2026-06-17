"""Admin App (app.py) 单元测试.

使用 mock 绕过 Tkinter GUI 初始化，测试业务逻辑和模块导入。
"""

import sys
import unittest
from unittest.mock import MagicMock, patch, PropertyMock


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

    def columnconfigure(self, *args, **kwargs):
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

    def delete(self, *args):
        pass

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

    def winfo_x(self):
        return 0

    def winfo_y(self):
        return 0


class MockStyle:
    """Mock ttkbootstrap Style."""

    def __init__(self, *args, **kwargs):
        pass

    def configure(self, *args, **kwargs):
        pass

    def map(self, *args, **kwargs):
        pass

    def lookup(self, *args, **kwargs):
        return ""


class MockCTkImage:
    """Mock customtkinter CTkImage，用于替换图片对象。"""

    def __init__(self, *args, **kwargs):
        pass


class MockCTkFrame:
    """Mock customtkinter CTkFrame，模拟框架容器。"""

    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def winfo_children(self):
        return []

    def destroy(self):
        pass


class MockCTkLabel:
    """Mock customtkinter CTkLabel，模拟标签控件。"""

    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass


class MockCTkEntry:
    """Mock customtkinter CTkEntry，模拟输入框控件。"""

    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def get(self):
        return ""

    def delete(self, *args):
        pass

    def insert(self, *args):
        pass


class MockCTkButton:
    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass


class MockCTkComboBox:
    def __init__(self, *args, **kwargs):
        self._values = kwargs.get("values", [])
        self._var = kwargs.get("variable")

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def get(self):
        return self._values[0] if self._values else ""

    def set(self, *args):
        pass


class MockCTkTextbox:
    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def get(self, *args):
        return ""

    def delete(self, *args):
        pass

    def insert(self, *args):
        pass


class MockCTkScrollableFrame:
    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def winfo_children(self):
        return []


class MockCTkSwitch:
    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def get(self):
        return 0


class MockCTkTabview:
    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def add(self, *args):
        return MockWindow()

    def get(self):
        return ""

    def configure(self, **kwargs):
        pass

    def set(self, *args):
        pass


class MockCTkToplevel:
    def __init__(self, *args, **kwargs):
        pass

    def title(self, *args):
        pass

    def geometry(self, *args):
        pass

    def protocol(self, *args):
        pass

    def grab_set(self):
        pass

    def focus_set(self):
        pass

    def destroy(self):
        pass

    def withdraw(self):
        pass

    def deiconify(self):
        pass

    def update_idletasks(self):
        pass

    def after(self, *args):
        pass

    def winfo_x(self):
        return 0

    def winfo_y(self):
        return 0


class MockTreeview:
    """Mock ttk Treeview，模拟表格控件的常用操作。"""

    def __init__(self, *args, **kwargs):
        self._columns = kwargs.get("columns", [])
        self._items = {}
        self._next_iid = 1

    def __getitem__(self, key):
        if key == "columns":
            return self._columns
        return self._columns

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


class MockScrollbar:
    def __init__(self, *args, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def place(self, **kwargs):
        pass

    def grid(self, **kwargs):
        pass

    def configure(self, **kwargs):
        pass

    def config(self, **kwargs):
        pass

    def set(self, *args):
        pass


class MockFigureCanvasTkAgg:
    def __init__(self, *args, **kwargs):
        pass

    def get_tk_widget(self):
        return MockWindow()

    def draw(self):
        pass


class MockFigure:
    def __init__(self, *args, **kwargs):
        pass

    def add_subplot(self, *args, **kwargs):
        return MockAxes()

    def set_size_inches(self, *args):
        pass

    def savefig(self, *args, **kwargs):
        pass

    def clear(self):
        pass


class MockAxes:
    def __init__(self):
        pass

    def bar(self, *args, **kwargs):
        return []

    def pie(self, *args, **kwargs):
        return []

    def plot(self, *args, **kwargs):
        return []

    def set_title(self, *args, **kwargs):
        pass

    def set_xlabel(self, *args, **kwargs):
        pass

    def set_ylabel(self, *args, **kwargs):
        pass

    def set_xticks(self, *args):
        pass

    def set_xticklabels(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        pass

    def axis(self, *args):
        pass

    def text(self, *args, **kwargs):
        pass

    def annotate(self, *args, **kwargs):
        pass

    def set_ylim(self, *args):
        pass

    def grid(self, *args, **kwargs):
        pass

    def axhline(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def get_figure(self):
        return MockFigure()

    def add_line(self, *args):
        pass

    def set_prop_cycle(self, *args):
        pass

    def add_patch(self, *args):
        pass


class MockImage:
    def __init__(self, *args, **kwargs):
        pass

    def resize(self, *args, **kwargs):
        return self

    def save(self, *args, **kwargs):
        pass

    @classmethod
    def open(cls, *args, **kwargs):
        return cls()


class MockImageTk:
    @staticmethod
    def PhotoImage(*args, **kwargs):
        return MagicMock()


# Patch modules before importing app
_mock_modules = {
    "ttkbootstrap": MagicMock(
        Window=MockWindow,
        Style=MockStyle,
    ),
    "customtkinter": MagicMock(
        CTkImage=MockCTkImage,
        CTkFrame=MockCTkFrame,
        CTkLabel=MockCTkLabel,
        CTkEntry=MockCTkEntry,
        CTkButton=MockCTkButton,
        CTkComboBox=MockCTkComboBox,
        CTkTextbox=MockCTkTextbox,
        CTkScrollableFrame=MockCTkScrollableFrame,
        CTkSwitch=MockCTkSwitch,
        CTkTabview=MockCTkTabview,
        CTkToplevel=MockCTkToplevel,
    ),
    "PIL.Image": MagicMock(
        Image=MockImage,
        Resampling=MagicMock(LANCZOS=1),
    ),
    "PIL.ImageTk": MagicMock(
        ImageTk=MockImageTk,
    ),
    "PIL": MagicMock(
        Image=MockImage,
        ImageTk=MockImageTk,
    ),
    "matplotlib.pyplot": MagicMock(),
    "matplotlib.figure": MagicMock(Figure=MockFigure),
    "matplotlib.backends.backend_tkagg": MagicMock(
        FigureCanvasTkAgg=MockFigureCanvasTkAgg,
    ),
    "numpy": MagicMock(),
}

# Also patch tkinter components
tk_mock = MagicMock()
tk_mock.Frame = MockWindow
tk_mock.Label = MockWindow
tk_mock.Button = MockWindow
tk_mock.Entry = MockWindow
tk_mock.Text = MockWindow
tk_mock.Canvas = MockWindow
tk_mock.Toplevel = MockCTkToplevel
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
tk_mock.simpledialog = MagicMock(
    askstring=MagicMock(return_value=""),
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

_mock_modules["tkinter"] = tk_mock
_mock_modules["tkinter.messagebox"] = tk_mock.messagebox
_mock_modules["tkinter.filedialog"] = tk_mock.filedialog
_mock_modules["tkinter.simpledialog"] = tk_mock.simpledialog
_mock_modules["tkinter.ttk"] = tk_mock.ttk


class TestAppImportAndInit(unittest.TestCase):
    """测试 app.py 的导入和基本初始化."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_app_imports(self):
        """测试 app.py 可以成功导入."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertTrue(hasattr(app, "App"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_app_init(self, mock_change, mock_load):
        """测试 App 类能初始化（mock GUI）."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.get_admin.return_value = {"name": "管理员", "avatar": ""}
        mock_dm.get_course.return_value = None
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.authenticate_admin.return_value = True
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        self.assertIsNotNone(instance)
        self.assertEqual(instance.dm, mock_dm)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_app_run_returns_dict(self, mock_change, mock_load):
        """测试 App.run 返回字典."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.get_admin.return_value = {"name": "管理员", "avatar": ""}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        result = instance.run()
        self.assertIsInstance(result, dict)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_app_logout_flag(self, mock_change, mock_load):
        """测试退出登录标志初始为 False."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = MagicMock()
        mock_dm.subjects = []
        mock_dm.students = {}
        mock_dm.get_notices.return_value = []
        mock_dm.get_schedules.return_value = []
        mock_dm.get_schedule_history.return_value = []
        mock_dm.get_admin.return_value = {"name": "管理员", "avatar": ""}
        mock_dm.courses = {}
        mock_dm.teachers = {}
        mock_dm.classes = []
        mock_dm.ranking.return_value = []
        mock_dm.get_warnings.return_value = []
        mock_dm.analyze_subject.return_value = None
        mock_dm.get_class_stats.return_value = None
        mock_dm.search.return_value = []
        mock_dm.get_history.return_value = []
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        self.assertFalse(instance._logout_flag)


class TestAppConstants(unittest.TestCase):
    """测试 app.py 的模块级常量."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_colors_defined(self):
        """测试颜色常量已定义."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertTrue(hasattr(app, "TEAL_COLOR"))
        self.assertTrue(hasattr(app, "TEAL_DARK"))
        self.assertTrue(hasattr(app, "TEAL_LIGHT"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_excel_flag(self):
        """测试 EX_OK 标志."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertIn(app.EX_OK, [True, False])

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_matplotlib_flag(self):
        """测试 MAT_OK 标志."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertIn(app.MAT_OK, [True, False])

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_base_dir(self):
        """测试 BASE_DIR 已定义."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        self.assertTrue(hasattr(app, "BASE_DIR"))
        self.assertTrue(isinstance(app.BASE_DIR, str))


# ============================================================
# Helper: create a properly configured mock DataManager
# ============================================================
def _create_mock_dm():
    """返回一个配置完整的 mock DataManager."""
    mock_dm = MagicMock()
    mock_dm.subjects = []
    mock_dm.students = {}
    mock_dm.courses = {}
    mock_dm.teachers = {}
    mock_dm.classes = []
    mock_dm.fp = "/tmp/test_grades.json"
    mock_dm.get_notices.return_value = []
    mock_dm.get_schedules.return_value = []
    mock_dm.get_schedule_history.return_value = []
    mock_dm.ranking.return_value = []
    mock_dm.get_warnings.return_value = []
    mock_dm.analyze_subject.return_value = None
    mock_dm.get_class_stats.return_value = None
    mock_dm.search.return_value = []
    mock_dm.get_history.return_value = []
    mock_dm.get_admin.return_value = {"name": "管理员", "avatar": ""}
    mock_dm.get_course.return_value = None
    mock_dm.authenticate_admin.return_value = True
    mock_dm.get_student.return_value = None
    mock_dm.get_teacher.return_value = None
    mock_dm._create_empty_data.return_value = {
        "subjects": [],
        "students": {},
        "history": [],
        "admin": {"username": "admin", "password": "123456", "name": "管理员"},
        "teachers": {},
        "courses": {},
        "classes": [],
    }
    mock_dm.save = MagicMock()
    mock_dm.load = MagicMock()
    mock_dm.stats = MagicMock(return_value=None)
    mock_dm.data = {
        "subjects": [],
        "students": {},
        "history": [],
        "admin": {"username": "admin", "password": "123456", "name": "管理员"},
    }
    return mock_dm


# ============================================================
# 新测试类：静态方法测试
# ============================================================
class TestAppStaticMethods(unittest.TestCase):
    """测试 App 类的静态方法和工具方法."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_get_level_tag_excellent(self):
        """测试 _get_level_tag: 95分 → 优秀."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        tag, level = app.App._get_level_tag(95)
        self.assertEqual(tag, "excellent")
        self.assertEqual(level, "优秀")

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_get_level_tag_good(self):
        """测试 _get_level_tag: 85分 → 良好."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        tag, level = app.App._get_level_tag(85)
        self.assertEqual(tag, "good")
        self.assertEqual(level, "良好")

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_get_level_tag_pass_75(self):
        """测试 _get_level_tag: 75分 → 良好（≥75为良好）."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        tag, level = app.App._get_level_tag(75)
        self.assertEqual(tag, "good")
        self.assertEqual(level, "良好")

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_get_level_tag_pass_65(self):
        """测试 _get_level_tag: 65分 → 及格（边界）."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        tag, level = app.App._get_level_tag(65)
        self.assertEqual(tag, "pass_")
        self.assertEqual(level, "及格")

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_get_level_tag_fail_55(self):
        """测试 _get_level_tag: 55分 → 不及格."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        tag, level = app.App._get_level_tag(55)
        self.assertEqual(tag, "fail")
        self.assertEqual(level, "不及格")

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    def test_get_level_tag_fail_50(self):
        """测试 _get_level_tag: 50分 → 不及格."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        tag, level = app.App._get_level_tag(50)
        self.assertEqual(tag, "fail")
        self.assertEqual(level, "不及格")

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_manage_sort_key_numeric(self, mock_change, mock_load):
        """测试 _manage_sort_key: 数字值."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        result = instance._manage_sort_key(["S001", "张三", "一班", "95"], 3)
        self.assertEqual(result, 95.0)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_manage_sort_key_dash(self, mock_change, mock_load):
        """测试 _manage_sort_key: "-" 返回 -1."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        result = instance._manage_sort_key(["S001", "张三", "一班", "-"], 3)
        self.assertEqual(result, -1)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_manage_sort_key_empty(self, mock_change, mock_load):
        """测试 _manage_sort_key: 空字符串返回 -1."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        result = instance._manage_sort_key(["S001", "张三", "一班", ""], 3)
        self.assertEqual(result, -1)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_manage_sort_key_string(self, mock_change, mock_load):
        """测试 _manage_sort_key: 非数字字符串直接返回."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        result = instance._manage_sort_key(["S001", "张三", "abc", "xyz"], 3)
        self.assertEqual(result, "xyz")

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_calc_subject_widths_default(self, mock_change, mock_load):
        """测试 _calc_subject_widths: 默认最小宽度."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        widths = instance._calc_subject_widths(["数学", "语文"])
        self.assertEqual(widths, [72, 72])

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_calc_subject_widths_long_name(self, mock_change, mock_load):
        """测试 _calc_subject_widths: 长科目名."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        # "高等数学进阶课程" = 8 chars, 8*14 = 112
        widths = instance._calc_subject_widths(["高等数学进阶课程"])
        self.assertEqual(widths, [112])

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_calc_subject_widths_custom_min(self, mock_change, mock_load):
        """测试 _calc_subject_widths: 自定义最小宽度."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        widths = instance._calc_subject_widths(["数学"], min_width=100)
        self.assertEqual(widths, [100])


# ============================================================
# 新测试类：页面构建方法测试
# ============================================================
class TestAppPageBuilders(unittest.TestCase):
    """测试 App 类的各个页面构建方法."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_dashboard_page(self, mock_change, mock_load):
        """测试 _build_dashboard_page 构建仪表盘."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.subjects = ["数学", "语文"]
        mock_dm.students = {"S001": {"name": "张三", "class": "一班", "scores": {}}}
        mock_dm.classes = ["一班"]
        mock_dm.teachers = {"T001": {"name": "李老师"}}
        mock_dm.courses = {"C001": {"name": "数学课"}}
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_dashboard_page(parent)
        self.assertTrue(hasattr(instance, "da_cards"))
        self.assertIn("students", instance.da_cards)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_account_page(self, mock_change, mock_load):
        """测试 _build_account_page 构建账号管理页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.teachers = {"T001": {"name": "李老师", "course_ids": []}}
        mock_dm.students = {"S001": {"name": "张三", "class": "一班", "scores": {}}}
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_account_page(parent)
        self.assertTrue(hasattr(instance, "acc_tree"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_course_mgmt_page(self, mock_change, mock_load):
        """测试 _build_course_mgmt_page 构建课程管理页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.courses = {}
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_course_mgmt_page(parent)
        self.assertTrue(hasattr(instance, "co_tree"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_analysis_page(self, mock_change, mock_load):
        """测试 _build_analysis_page 构建分析页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.subjects = ["数学"]
        mock_dm.students = {}
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_analysis_page(parent)
        self.assertTrue(hasattr(instance, "alab"))
        self.assertTrue(hasattr(instance, "adt"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_notice_mgmt_page(self, mock_change, mock_load):
        """测试 _build_notice_mgmt_page 构建通知管理页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_notice_mgmt_page(parent)
        self.assertTrue(hasattr(instance, "_notice_tree"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_schedule_mgmt_page(self, mock_change, mock_load):
        """测试 _build_schedule_mgmt_page 构建课表管理页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_schedule_mgmt_page(parent)
        self.assertTrue(hasattr(instance, "_schedule_tree"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_excel_page(self, mock_change, mock_load):
        """测试 _build_excel_page 构建 Excel 导入导出页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.subjects = ["数学"]
        mock_dm.students = {}
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_excel_page(parent)
        self.assertTrue(hasattr(instance, "ex_tree"))
        self.assertTrue(hasattr(instance, "_excel_parent"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_manage_page(self, mock_change, mock_load):
        """测试 _build_manage_page 构建成绩管理页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.subjects = ["数学"]
        mock_dm.students = {}
        mock_dm.classes = []
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_manage_page(parent)
        self.assertTrue(hasattr(instance, "mg_tree"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_admin_profile_page(self, mock_change, mock_load):
        """测试 _build_admin_profile_page 构建个人中心页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.get_admin.return_value = {
            "username": "admin",
            "password": "123456",
            "name": "管理员",
            "phone": "",
            "email": "",
            "avatar": "",
        }
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_admin_profile_page(parent)
        self.assertTrue(hasattr(instance, "admin_avatar_label"))

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_build_settings_page(self, mock_change, mock_load):
        """测试 _build_settings_page 构建设置页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        instance._build_settings_page(parent)
        # 设置页面构建成功即可，不抛出异常


# ============================================================
# 新测试类：业务方法测试
# ============================================================
class TestAppMethods(unittest.TestCase):
    """测试 App 类的业务方法."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_check_excel_available_true(self, mock_change, mock_load):
        """测试 _check_excel_available: EX_OK=True 时返回 True."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        with patch.object(app, "EX_OK", True):
            result = instance._check_excel_available()
            self.assertTrue(result)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_check_excel_available_false(self, mock_change, mock_load):
        """测试 _check_excel_available: EX_OK=False 时返回 False."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        with patch.object(app, "EX_OK", False):
            result = instance._check_excel_available()
            self.assertFalse(result)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_show_status_info(self, mock_change, mock_load):
        """测试 _show_status: info 级别."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance._show_status("测试消息", "info")
        # status.set 被调用过
        instance.status.set.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_show_status_ok(self, mock_change, mock_load):
        """测试 _show_status: ok 级别."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance._show_status("操作成功", "ok")
        instance.status.set.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_show_status_warn(self, mock_change, mock_load):
        """测试 _show_status: warn 级别."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance._show_status("警告", "warn")
        instance.status.set.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_update_status(self, mock_change, mock_load):
        """测试 _update_status 更新状态栏."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.students = {"S001": {"name": "张三"}, "S002": {"name": "李四"}}
        mock_dm.classes = ["一班", "二班"]
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance._update_status()
        instance.status.set.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_switch_page(self, mock_change, mock_load):
        """测试 _switch_page 切换页面."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        # 设置 content_area
        instance.content_area = MockWindow()
        # 调用 _switch_page 传入一个简单的 builder
        called = []

        def dummy_builder(parent):
            called.append(True)

        instance._switch_page(dummy_builder)
        self.assertTrue(len(called) > 0)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_set_active_button_first(self, mock_change, mock_load):
        """测试 _set_active_button: 激活第一个按钮."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        # 创建 mock 按钮
        btn0 = MagicMock()
        btn1 = MagicMock()
        instance.nav_buttons = [btn0, btn1]
        instance._set_active_button(0)
        btn0.configure.assert_called()
        btn1.configure.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_set_active_button_second(self, mock_change, mock_load):
        """测试 _set_active_button: 激活第二个按钮."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        btn0 = MagicMock()
        btn1 = MagicMock()
        instance.nav_buttons = [btn0, btn1]
        instance._set_active_button(1)
        btn0.configure.assert_called()
        btn1.configure.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_refresh_all_pages_no_trees(self, mock_change, mock_load):
        """测试 _refresh_all_pages: 无表格时不报错."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        # 不设置 mg_tree 和 ex_tree，应该静默跳过
        instance._refresh_all_pages()
        # 不抛异常即为成功

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_refresh_all_pages_with_mg_tree(self, mock_change, mock_load):
        """测试 _refresh_all_pages: 有 mg_tree 时刷新."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.students = {}
        mock_dm.subjects = []
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        # 创建 mock mg_tree
        mock_tree = MagicMock()
        mock_tree.winfo_exists.return_value = True
        mock_tree.__getitem__ = MagicMock(return_value=[])
        mock_tree.get_children.return_value = []
        instance.mg_tree = mock_tree
        instance._mg_sort_col = ""
        instance._mg_sort_asc = True
        instance._refresh_all_pages()
        # 不抛异常即为成功

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_refresh_dashboard(self, mock_change, mock_load):
        """测试 _refresh_dashboard 刷新仪表盘."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.subjects = ["数学"]
        mock_dm.students = {"S001": {"name": "张三", "class": "一班", "scores": {}}}
        mock_dm.classes = ["一班"]
        mock_dm.teachers = {"T001": {"name": "李老师"}}
        mock_dm.courses = {"C001": {"name": "数学课"}}
        mock_dm.get_warnings.return_value = []
        mock_dm.get_history.return_value = []
        mock_dm.analyze_subject.return_value = {"avg": 85.5}
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        # 设置仪表盘相关属性
        instance.da_cards = {
            "students": MagicMock(),
            "subjects": MagicMock(),
            "classes": MagicMock(),
            "warnings": MagicMock(),
            "teachers": MagicMock(),
            "courses": MagicMock(),
        }
        instance.da_subj_frame = MockWindow()
        instance.da_warn_frame = MockWindow()
        instance.da_hist_frame = MockWindow()
        instance._refresh_dashboard()
        # 不抛异常即为成功

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_analyze_subject_no_subject(self, mock_change, mock_load):
        """测试 _analyze_subject: 无科目时弹出警告."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance.an_subj = MagicMock()
        instance.an_subj.get.return_value = ""
        instance._analyze_subject()
        tk_mock.messagebox.showwarning.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_analyze_subject_no_data(self, mock_change, mock_load):
        """测试 _analyze_subject: 无成绩数据时弹出提示."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.analyze_subject.return_value = None
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance.an_subj = MagicMock()
        instance.an_subj.get.return_value = "数学"
        instance._analyze_subject()
        tk_mock.messagebox.showinfo.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_analyze_subject_with_data(self, mock_change, mock_load):
        """测试 _analyze_subject: 有成绩数据时正常分析."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.analyze_subject.return_value = {
            "count": 10,
            "max": 95,
            "min": 45,
            "avg": 75.5,
            "pass_rate": 80.0,
            "excellent_rate": 20.0,
            "distribution": {
                "0-59": 2,
                "60-69": 2,
                "70-79": 2,
                "80-89": 2,
                "90-100": 2,
            },
        }
        mock_dm.students = {
            "S001": {"name": "张三", "class": "一班", "scores": {"数学": 95}},
            "S002": {"name": "李四", "class": "一班", "scores": {"数学": 45}},
        }
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance.an_subj = MagicMock()
        instance.an_subj.get.return_value = "数学"
        # 设置分析页面标签
        instance.alab = {
            "cnt": MagicMock(),
            "mx": MagicMock(),
            "mn": MagicMock(),
            "av": MagicMock(),
            "ps": MagicMock(),
            "ex": MagicMock(),
        }
        instance.adist = MagicMock()
        instance.adist.get_children.return_value = []
        instance.adt = MagicMock()
        instance.adt.get_children.return_value = []
        instance._analyze_subject()
        # 验证各标签被更新
        instance.alab["cnt"].config.assert_called()
        instance.alab["mx"].config.assert_called()
        instance.alab["mn"].config.assert_called()
        instance.alab["av"].config.assert_called()
        instance.alab["ps"].config.assert_called()
        instance.alab["ex"].config.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_create_treeview(self, mock_change, mock_load):
        """测试 _create_treeview 创建表格."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        parent = MockWindow()
        tree = instance._create_treeview(
            parent, ["学号", "姓名"], [100, 100], height=10
        )
        self.assertIsNotNone(tree)

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_settings_backup(self, mock_change, mock_load):
        """测试 _settings_backup 备份数据."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI
        import tempfile
        import os

        mock_dm = _create_mock_dm()
        # 创建临时文件作为源文件
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            src_path = f.name
            f.write(b'{"test": true}')
        mock_dm.fp = src_path
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        try:
            instance._settings_backup()
            # 验证 showinfo 被调用
            tk_mock.messagebox.showinfo.assert_called()
        finally:
            # 清理临时文件
            if os.path.exists(src_path):
                os.unlink(src_path)
            import glob

            bak_dir = os.path.dirname(src_path)
            for bak in glob.glob(os.path.join(bak_dir, "*.bak")):
                try:
                    os.unlink(bak)
                except Exception:
                    pass

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_settings_restore_no_file(self, mock_change, mock_load):
        """测试 _settings_restore: 未选择文件时返回."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        mock_dm.fp = "/tmp/test.json"
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        tk_mock.filedialog.askopenfilename.return_value = ""
        instance._settings_restore()
        # 未选择文件，不会调用 askyesno

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_settings_reset(self, mock_change, mock_load):
        """测试 _settings_reset 重置数据."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance._settings_reset()
        # 验证 save 被调用
        mock_dm.save.assert_called()
        tk_mock.messagebox.showinfo.assert_called()


# ============================================================
# 新测试类：生命周期方法测试
# ============================================================
class TestAppLifecycle(unittest.TestCase):
    """测试 App 类的生命周期方法."""

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_run_returns_dict(self, mock_change, mock_load):
        """测试 run() 返回字典."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        result = instance.run()
        self.assertIsInstance(result, dict)
        self.assertIn("logout", result)
        self.assertFalse(result["logout"])

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_on_close(self, mock_change, mock_load):
        """测试 _on_close 保存数据并销毁窗口."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance.win = MagicMock()
        instance._on_close()
        mock_dm.save.assert_called()
        instance.win.destroy.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_logout_confirm(self, mock_change, mock_load):
        """测试 _logout: 确认退出登录."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance.win = MagicMock()
        tk_mock.messagebox.askyesno.return_value = True
        instance._logout()
        self.assertTrue(instance._logout_flag)
        mock_dm.save.assert_called()
        instance.win.destroy.assert_called()

    @patch.dict("sys.modules", _mock_modules)
    @patch("app.messagebox", tk_mock.messagebox)
    @patch("app.filedialog", tk_mock.filedialog)
    @patch("app.simpledialog", tk_mock.simpledialog)
    @patch("app.Window", MockWindow)
    @patch("app.Style", MockStyle)
    @patch("app.load_avatar")
    @patch("app.change_avatar")
    def test_logout_cancel(self, mock_change, mock_load):
        """测试 _logout: 取消退出登录."""
        import app  # 在 mock 环境就绪后导入，避免提前初始化 GUI

        mock_dm = _create_mock_dm()
        instance = app.App(data_manager=mock_dm, user_info={"username": "admin"})
        instance.win = MagicMock()
        tk_mock.messagebox.askyesno.return_value = False
        instance._logout()
        self.assertFalse(instance._logout_flag)
        instance.win.destroy.assert_not_called()


if __name__ == "__main__":
    unittest.main()
