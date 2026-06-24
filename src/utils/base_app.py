"""Base application module for Student Grade Management System.

本模块提供 BaseApp 基类，封装了管理员、教师、学生三个端共通的
UI 构建、页面切换、导航按钮、Treeview 创建、导出对话框、头像加载等
功能，减少跨文件代码重复。

主要组件:
    BaseApp: 应用基类，提供所有公共方法与钩子接口。
"""

import csv
import datetime
import abc
import logging
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import openpyxl
except ImportError:
    openpyxl = None  # type: ignore

from ttkbootstrap import Window, Style

from modules.data_manager import DataManager
from src.utils.avatar_utils import load_avatar, change_avatar
from src.utils.excel_handler import (
    export_to_excel,
    get_default_filename as get_excel_filename,
    is_excel_available,
    create_template,
)
from src.utils.export import export_to_csv, get_default_filename as get_csv_filename
from src.config import UI_COLORS, FONTS, DIALOG_SIZES, DIALOG_OFFSET
from src.utils.ui_utils import (
    create_dialog,
    show_info,
    show_warning,
    show_error,
    confirm,
    validate_password,
)

# 模块级日志记录器（所有子类共享同一配置）
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(_handler)

# 界面主题色常量
TEAL_COLOR = UI_COLORS["teal"]
TEAL_DARK = UI_COLORS["teal_dark"]
TEAL_LIGHT = UI_COLORS["teal_light"]

# Excel 库可用性标志
EX_OK: bool = is_excel_available()

# 尝试导入 matplotlib 用于图表展示
try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np

    # 根据操作系统自动选择中文字体
    if sys.platform.startswith("win"):
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    elif sys.platform.startswith("darwin"):
        plt.rcParams["font.sans-serif"] = [
            "PingFang SC",
            "Heiti TC",
            "Arial Unicode MS",
        ]
    else:
        plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    MAT_OK: bool = True
except ImportError as e:
    print(f"Matplotlib 导入失败: {e}")
    plt = None  # type: ignore
    Figure = None  # type: ignore
    np = None  # type: ignore
    FigureCanvasTkAgg = None  # type: ignore
    MAT_OK = False


class BaseApp(abc.ABC):
    """学生成绩管理系统应用基类.

    封装三个端（管理员、教师、学生）共通的窗口管理、侧边栏导航、
    页面切换、表格创建、数据导出及头像处理等逻辑。子类通过重写
    钩子方法（如 _get_window_title、_get_avatar_data 等）实现
    差异化定制。

    Attributes:
        dm (DataManager): 数据管理器实例。
        user_info (dict): 当前登录用户信息。
        win (Window): ttkbootstrap 主窗口。
        content_area (tk.Frame): 右侧内容展示区域。
        page_builders (dict): 页面名称到构建函数的映射。
        nav_buttons (list): 导航按钮/标签控件列表。
        logger (logging.Logger): 实例级日志记录器。
    """

    def __init__(
        self,
        data_manager: DataManager | None = None,
        user_info: dict | None = None,
    ) -> None:
        """初始化应用基类.

        创建主窗口、配置全局样式，并初始化公共属性。
        子类应在调用本方法后设置 page_builders 并调用 _build_ui。

        Args:
            data_manager: 数据管理器实例。若为 None，则自动创建。
            user_info: 当前登录用户信息字典。
        """
        self.dm = data_manager if data_manager else DataManager()
        self.user_info = user_info or {}
        self._logout = False

        self.win = Window(themename="cosmo")
        self.win.title(self._get_window_title())
        self.win.state("zoomed")
        self.win.minsize(1024, 768)
        self.win.configure(bg=UI_COLORS["page_bg"])

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            _handler = logging.StreamHandler()
            _handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(_handler)

        self._setup_styles()

    # ========== 钩子方法（子类必须重写） ==========

    @abc.abstractmethod
    def _get_window_title(self) -> str:
        """返回主窗口标题.

        Returns:
            窗口标题字符串。
        """
        ...

    @abc.abstractmethod
    def _get_header_title(self) -> str:
        """返回顶部横幅标题文本.

        Returns:
            横幅标题字符串。
        """
        ...

    @abc.abstractmethod
    def _get_user_display_name(self) -> str:
        """返回右上角显示的用户名称.

        Returns:
            用户名字符串。
        """
        ...

    @abc.abstractmethod
    def _get_avatar_data(self) -> dict:
        """返回头像相关数据.

        Returns:
            包含 "name" 与 "avatar" 键的字典。
        """
        ...

    @abc.abstractmethod
    def _save_avatar(self, path: str) -> None:
        """保存头像路径到对应用户数据.

        Args:
            path: 新头像文件的绝对路径。
        """
        ...

    # ========== 样式与 UI 构建 ==========

    def _setup_styles(self) -> None:
        """配置全局 ttk 样式.

        统一 Treeview、Treeview.Heading 及侧边栏按钮的外观。
        """
        style = Style("cosmo")
        style.configure("Treeview", font=FONTS["normal"], rowheight=36)
        style.configure(
            "Treeview.Heading",
            font=FONTS["normal_bold"],
            background=UI_COLORS["heading_bg"],
            foreground=UI_COLORS["sidebar_bg"],
        )
        style.configure(
            "Sidebar.TButton",
            font=FONTS["normal"],
            background=UI_COLORS["sidebar_bg"],
            padding=(15, 12),
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Sidebar.TButton",
            background=[("active", "#e9ecef")],
            foreground=[("active", "#00897B")],
        )
        style.configure(
            "Sidebar.Active.TButton",
            font=FONTS["normal_bold"],
            padding=(15, 12),
            relief="flat",
            borderwidth=0,
            background=UI_COLORS["sidebar_active"],
            foreground="white",
        )

    def _build_ui(self) -> None:
        """构建应用程序主界面布局.

        包括顶部标题栏、左侧导航侧边栏、右侧内容区域，
        并默认显示第一个页面（仪表盘）。
        """
        # ---------- 顶部标题栏 ----------
        header = tk.Frame(self.win, bg=TEAL_COLOR, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text=self._get_header_title(),
            font=FONTS["header"],
            fg="white",
            bg=TEAL_COLOR,
        ).pack(side="left", padx=20, pady=12)

        # 右上角用户信息及退出登录按钮
        user_frame = tk.Frame(header, bg=TEAL_COLOR)
        user_frame.pack(side="right", padx=20, pady=12)

        tk.Label(
            user_frame,
            text=f"👤 {self._get_user_display_name()}",
            font=FONTS["body"],
            fg="white",
            bg=TEAL_COLOR,
        ).pack(side="left", padx=(0, 15))

        tk.Button(
            user_frame,
            text="退出登录",
            font=FONTS["caption"],
            bg="white",
            fg=TEAL_COLOR,
            activebackground=UI_COLORS["heading_bg"],
            activeforeground=TEAL_COLOR,
            relief="flat",
            cursor="hand2",
            command=self._confirm_logout,
            padx=12,
            pady=4,
        ).pack(side="left")

        # ---------- 主容器：侧边栏 + 内容区 ----------
        main_container = tk.Frame(self.win, bg=UI_COLORS["page_bg"])
        main_container.pack(fill="both", expand=True)

        sidebar = tk.Frame(main_container, width=200, bg=UI_COLORS["sidebar_bg"])
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content_area = tk.Frame(main_container, bg="white")
        self.content_area.pack(side="right", fill="both", expand=True)

        # ---------- 侧边栏顶部头像区域 ----------
        avatar_data = self._get_avatar_data()
        avatar_frame = tk.Frame(sidebar, bg=UI_COLORS["sidebar_bg"], height=80)
        avatar_frame.pack(fill="x", pady=(15, 5))
        avatar_frame.pack_propagate(False)
        try:
            self.sidebar_avatar_label = tk.Label(
                avatar_frame, bg=UI_COLORS["sidebar_bg"]
            )
            self.sidebar_avatar_label.pack(pady=5)
            load_avatar(
                self.sidebar_avatar_label,
                avatar_data.get("avatar", ""),
                size=(50, 50),
            )
        except Exception:
            tk.Label(
                avatar_frame,
                text="👤",
                font=FONTS["avatar"],
                bg=UI_COLORS["sidebar_bg"],
                fg="white",
            ).pack(pady=5)
        tk.Label(
            avatar_frame,
            text=avatar_data.get("name", ""),
            font=FONTS["body_bold"],
            fg="white",
            bg=UI_COLORS["sidebar_bg"],
        ).pack()

        # ---------- 页面映射与导航按钮初始化 ----------
        self.nav_buttons = []

        # 1. 先单独放【仪表盘】（ttk.Button）
        idx = 0
        text, builder = list(self.page_builders.items())[idx]

        def cmd(b=builder, btn_idx=idx):
            """导航按钮点击命令.

            Args:
                b: 页面构建函数，由闭包捕获。
                btn_idx: 当前按钮在导航栏中的索引。
            """
            self._switch_page(b)
            self._set_active_button(btn_idx)

        btn = ttk.Button(sidebar, text=text, style="Sidebar.TButton", command=cmd)
        btn.pack(fill="x", padx=15, ipady=5)
        self.nav_buttons.append(btn)

        # 2. 仪表盘与其他菜单之间的空隙
        spacer = tk.Frame(sidebar, height=20, bg=UI_COLORS["sidebar_bg"])
        spacer.pack(fill="x")

        # 3. 其他菜单（tk.Label）
        for idx, (text, builder) in enumerate(
            list(self.page_builders.items())[1:], start=1
        ):
            btn = tk.Label(
                sidebar,
                text=text,
                font=FONTS["normal"],
                bg=UI_COLORS["sidebar_inactive_bg"],
                fg=UI_COLORS["sidebar_inactive_fg"],
                cursor="hand2",
            )
            btn.bind(
                "<Button-1>",
                lambda e, b=builder, i=idx: (
                    self._switch_page(b),
                    self._set_active_button(i),
                ),
            )
            btn.pack(fill="x", padx=15, ipady=8)
            self.nav_buttons.append(btn)

        # 默认选中第一个页面
        self._set_active_button(0)
        first_builder = list(self.page_builders.values())[0]
        self._switch_page(first_builder)

        # 状态栏（子类可重写以提供实际实现）
        self._build_status_bar()

    def _switch_page(self, builder_func) -> None:
        """切换右侧内容页面.

        清空内容区后调用指定构建函数重新渲染页面。

        Args:
            builder_func: 页面构建函数，接收父 Frame 作为参数。
        """
        for widget in self.content_area.winfo_children():
            widget.destroy()
        page_frame = tk.Frame(self.content_area, bg="white")
        page_frame.pack(fill="both", expand=True, padx=10, pady=10)
        builder_func(page_frame)

    def _set_active_button(self, active_idx: int) -> None:
        """设置导航按钮的选中状态样式.

        根据索引将对应按钮设为高亮样式，其余恢复默认样式。
        索引 0 为 ttk.Button，其余为 tk.Label，配置方式不同。

        Args:
            active_idx: 当前选中按钮的索引。
        """
        for idx, btn in enumerate(self.nav_buttons):
            if idx == active_idx:
                if idx == 0:
                    btn.configure(style="Sidebar.Active.TButton")
                else:
                    btn.configure(
                        font=FONTS["normal_bold"],
                        fg=TEAL_COLOR,
                        bg=UI_COLORS["border"],
                    )
            else:
                if idx == 0:
                    btn.configure(style="Sidebar.TButton")
                else:
                    btn.configure(
                        font=FONTS["normal"],
                        fg=UI_COLORS["sidebar_inactive_fg"],
                        bg=UI_COLORS["sidebar_inactive_bg"],
                    )
        self.win.update_idletasks()

    def _build_status_bar(self) -> None:
        """构建底部状态栏，显示提示信息、数据统计和实时时钟."""
        bar = tk.Frame(self.win, bg=UI_COLORS["status_bar_bg"], height=60)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status: tk.StringVar = tk.StringVar(value="就绪")
        status_label = tk.Label(
            bar,
            textvariable=self.status,
            font=FONTS["small"],
            bg=UI_COLORS["status_bar_bg"],
        )
        status_label.pack(side="left", padx=12)

        self.clock: tk.StringVar = tk.StringVar()
        clock_label = tk.Label(
            bar,
            textvariable=self.clock,
            font=FONTS["small"],
            bg=UI_COLORS["status_bar_bg"],
        )
        clock_label.pack(side="right", padx=12)

        self._update_clock()
        self._update_status()

    def _show_status(self, text: str, level: str = "info") -> None:
        """在底部状态栏显示带图标的提示信息.

        Args:
            text: 要显示的提示文本。
            level: 提示级别，可选值为 "info"、"ok"、"warn"、"err"。
        """
        icons = {"info": "ℹ️", "ok": "✅", "warn": "⚠️", "err": "❌"}
        self.status.set(f"  {icons.get(level, 'ℹ️')}  {text}")

    def _update_status(self) -> None:
        """更新状态栏为当前学生和班级数量统计.

        班级数使用 self.dm.classes（合并去重后），
        而非独立 classes 列表长度，避免空班级导致统计偏差.
        """
        class_count = len(self.dm.classes) if hasattr(self.dm, "classes") else 0
        self.status.set(
            f"  学生 {len(self.dm.data.get('students', {}))} 人 | 班级 "
            f"{class_count} 个"
        )

    def _update_clock(self) -> None:
        """更新时钟标签为当前日期时间."""
        self.clock.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.win.after(1000, self._update_clock)

    def _position_dialog(self, dialog) -> None:
        """将弹窗固定在主窗口左上角区域.

        位置偏移：左侧 60 像素，顶部 120 像素，
        确保所有弹窗显示在一致的固定位置。

        为避免弹窗先在默认位置闪现再跳转，
        先调用 withdraw 隐藏窗口，设置好位置后再 deiconify 显示。

        Args:
            dialog: 要定位的 Toplevel 弹窗对象。
        """
        dialog.withdraw()
        self.win.update_idletasks()
        win_x = self.win.winfo_x()
        win_y = self.win.winfo_y()
        dialog.geometry(f"+{win_x + 60}+{win_y + 120}")
        dialog.deiconify()

    # ========== Treeview 辅助方法 ==========

    def _apply_zebra_stripes(self, tree, odd_tag: str = "odd", even_tag: str = "even") -> None:
        """为 Treeview 应用斑马纹样式.

        奇偶行使用不同背景色，提升可读性。
        统一替代各子类中散点的 tag_configure 调用。

        Args:
            tree: ttk.Treeview 控件。
            odd_tag: 奇数行标签名，默认 "odd"。
            even_tag: 偶数行标签名，默认 "even"。
        """
        tree.tag_configure(odd_tag, background=UI_COLORS["row_odd"])
        tree.tag_configure(even_tag, background="#FFFFFF")

    def _calc_subject_widths(
        self, subjects: list[str], min_width: int = 72
    ) -> list[int]:
        """计算科目列宽度.

        根据科目名称长度计算合适的列宽，保证最小宽度。

        Args:
            subjects: 科目名称列表。
            min_width: 最小列宽像素值。

        Returns:
            各科目对应列宽的列表。
        """
        return [max(min_width, len(s) * 14) for s in subjects]

    def _create_treeview(
        self,
        parent: tk.Frame,
        columns: list[str],
        widths: list[int],
        height: int = 14,
        pack_frame: bool = True,
    ) -> ttk.Treeview:
        """创建并配置 Treeview 表格控件.

        自动添加垂直与水平滚动条，配置表头与列宽，并应用斑马纹样式。

        Args:
            parent: 父容器 Frame。
            columns: 列标识符列表。
            widths: 对应各列的宽度列表。
            height: 表格显示行数。
            pack_frame: 是否自动将内部 Frame 打包到 parent。

        Returns:
            配置完成的 ttk.Treeview 实例。
        """
        frame = tk.Frame(parent, bg="white")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        if pack_frame:
            frame.pack(fill="both", expand=True, pady=(15, 0))

        tree.tag_configure("odd", background=UI_COLORS["row_odd"])
        tree.tag_configure("even", background=UI_COLORS["row_even"])
        return tree

    def _create_dashboard_card(self, container, icon, title, value, color):
        """创建仪表盘中的信息卡片组件.

        每个卡片包含图标、标题与数值，水平排列在卡片行中。
        子类仪表盘页面调用此方法替代各自的局部 create_card() 函数。

        Args:
            container: 卡片行容器 Frame。
            icon: 卡片图标字符串。
            title: 卡片标题。
            value: 卡片显示数值。
            color: 数值文本颜色。

        Returns:
            tk.Label: 数值标签控件，可用于后续动态更新。
        """
        card = tk.Frame(container, bg="white", relief="solid", bd=1)
        card.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(
            card,
            text=icon,
            font=("微软雅黑", 20),
            bg="white",
        ).pack(anchor="w", padx=10, pady=5)
        tk.Label(
            card,
            text=title,
            font=FONTS["caption"],
            fg=UI_COLORS["text_gray"],
            bg="white",
        ).pack(anchor="w", padx=10)
        val_lbl = tk.Label(
            card,
            text=str(value),
            font=("微软雅黑", 24, "bold"),
            fg=color,
            bg="white",
        )
        val_lbl.pack(anchor="w", padx=10, pady=5)
        return val_lbl

    def _rebuild_mg_tree(self) -> None:
        """重建成绩管理 Treeview 表格 UI.

        当科目列表发生变化（如重置数据）后调用，销毁旧表格
        并根据当前 ``self.dm.subjects`` 重新创建表头和列宽。
        子类可通过重写 ``_get_mg_tree_double_click_handler`` 与
        ``_get_mg_tree_sort_handler`` 自定义事件绑定。
        """
        if not hasattr(self, "mg_tree"):
            return

        parent = self.mg_tree.master
        self.mg_tree.destroy()

        new_subjects = self.dm.subjects
        columns = ["学号", "姓名", "班级"] + new_subjects + ["总分", "平均分"]
        base_widths = [110, 90, 90]
        widths = base_widths + self._calc_subject_widths(new_subjects) + [80, 80]

        self.mg_tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)
        self.mg_tree.tag_configure("fail", foreground=UI_COLORS["danger"])
        self.mg_tree.tag_configure("warn", foreground=UI_COLORS["warning"])
        self.mg_tree.tag_configure("good", foreground=UI_COLORS["success"])
        self.mg_tree.tag_configure("empty_all", foreground=UI_COLORS["placeholder"])
        self.mg_tree.tag_configure("odd", background=UI_COLORS["row_odd"])
        self.mg_tree.tag_configure("even", background=UI_COLORS["row_even"])

        double_click = getattr(self, "_manage_cell_double_click", None)
        if double_click:
            self.mg_tree.bind("<Double-1>", double_click)

        for col, width in zip(columns, widths):
            self.mg_tree.heading(col, text=col)
            self.mg_tree.column(col, width=width, anchor="center")

        sort_handler = getattr(self, "_manage_sort_tree", None)
        if sort_handler:
            for col in columns:
                self.mg_tree.heading(col, command=lambda c=col: sort_handler(c))

        self.mg_tree.pack(fill="both", expand=True)

    # ========== 导出功能 ==========

    def _show_export_dialog(self, export_type: str) -> None:
        """显示导出选项对话框（全部或指定班级）.

        弹窗固定在主窗口左上区域，用户可选择导出全部班级，
        或从下拉框中选择特定班级进行导出。

        Args:
            export_type: 导出类型，取值为 "excel" 或 "csv"。
        """
        dialog = tk.Toplevel(self.win)
        dialog.title("导出选项")
        dialog.geometry("380x230")
        dialog.grab_set()
        dialog.transient(self.win)
        self._position_dialog(dialog)

        tk.Label(
            dialog,
            text="请选择导出范围",
            font=FONTS["normal_bold"],
        ).pack(pady=12)

        selected_class = tk.StringVar(value="全部")

        tk.Radiobutton(
            dialog,
            text="导出全部班级",
            variable=selected_class,
            value="全部",
            font=FONTS["large"],
        ).pack(anchor="w", padx=40, pady=4)

        class_frame = tk.Frame(dialog)
        class_frame.pack(anchor="w", padx=40, pady=4, fill="x")
        tk.Radiobutton(
            class_frame,
            text="导出指定班级：",
            variable=selected_class,
            value="指定",
            font=FONTS["large"],
        ).pack(side="left")

        classes = self.dm.classes
        class_combo = ttk.Combobox(
            class_frame,
            values=classes if classes else ["无班级"],
            state="readonly",
            width=15,
        )
        if classes:
            class_combo.current(0)
        class_combo.pack(side="left", padx=5)

        def do_export() -> None:
            """执行导出操作."""
            class_name = ""
            if selected_class.get() == "指定":
                class_name = class_combo.get()
                if not class_name or class_name == "无班级":
                    show_warning("提示", "请先选择一个班级", parent=dialog)
                    return

            dialog.destroy()
            if export_type == "excel":
                self._do_export_excel(class_name)
            else:
                self._do_export_csv(class_name)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="导出", command=do_export).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(
            side="left", padx=8
        )

    def _do_export_excel(self, class_name: str = "") -> None:
        """执行 Excel 导出（可选按班级过滤）.

        Args:
            class_name: 要导出的班级名称。空字符串表示导出全部班级。
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=get_excel_filename(),
        )
        if not filepath:
            return

        if not class_name:
            if export_to_excel(filepath, self.dm):
                self._show_status("Excel 导出成功", "ok")
                self.logger.info("Excel 导出成功: %s", filepath)
                show_info("成功", "Excel 导出成功")
            else:
                self.logger.error("Excel 导出失败: %s", filepath)
                show_error("错误", "导出失败")
        else:
            if self._export_excel_by_class(filepath, class_name):
                self._show_status(f"Excel 导出成功（{class_name}）", "ok")
                self.logger.info("Excel 导出成功（%s）: %s", class_name, filepath)
                show_info("成功", f"Excel 导出成功（{class_name}）")
            else:
                self.logger.error("Excel 导出失败: %s", filepath)
                show_error("错误", "导出失败")

    def _do_export_csv(self, class_name: str = "") -> None:
        """执行 CSV 导出（可选按班级过滤）.

        Args:
            class_name: 要导出的班级名称。空字符串表示导出全部班级。
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=get_csv_filename(),
        )
        if not filepath:
            return

        if not class_name:
            if export_to_csv(filepath, self.dm):
                self._show_status("CSV 导出成功", "ok")
                self.logger.info("CSV 导出成功: %s", filepath)
                show_info("成功", "CSV 导出成功")
            else:
                self.logger.error("CSV 导出失败: %s", filepath)
                show_error("错误", "导出失败")
        else:
            if self._export_csv_by_class(filepath, class_name):
                self._show_status(f"CSV 导出成功（{class_name}）", "ok")
                self.logger.info("CSV 导出成功（%s）: %s", class_name, filepath)
                show_info("成功", f"CSV 导出成功（{class_name}）")
            else:
                self.logger.error("CSV 导出失败: %s", filepath)
                show_error("错误", "导出失败")

    def _export_excel_by_class(self, filepath: str, class_name: str) -> bool:
        """按班级导出 Excel.

        Args:
            filepath: 导出的文件保存路径。
            class_name: 要过滤并导出的班级名称。

        Returns:
            True 表示导出成功，False 表示导出失败。
        """
        if openpyxl is None:
            return False
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            if ws is None:
                return False
            ws.title = f"{class_name}成绩表"

            subjects = list(self.dm.subjects)
            ws.append(
                ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分", "等级"]
            )

            class_students = self.dm.get_students_by_class(class_name)
            class_students.sort(
                key=lambda x: (
                    self.dm.stats(x[0]).get("total", 0) if self.dm.stats(x[0]) else 0
                ),
                reverse=True,
            )

            for rank, (sid, stu) in enumerate(class_students, 1):
                st = self.dm.stats(sid)
                if st is None:
                    continue
                avg = st["avg"]
                if avg >= 90:
                    level = "优秀"
                elif avg >= 75:
                    level = "良好"
                elif avg >= 60:
                    level = "及格"
                else:
                    level = "不及格"
                row_data = (
                    [rank, sid, stu["name"], class_name]
                    + [stu["scores"].get(s, "-") for s in subjects]
                    + [st["total"], st["avg"], level]
                )
                ws.append(row_data)

            wb.save(filepath)
            return True
        except Exception as e:
            logger.warning("Excel导出失败: %s", e, exc_info=True)
            return False

    def _export_csv_by_class(self, filepath: str, class_name: str) -> bool:
        """按班级导出 CSV.

        Args:
            filepath: 导出的文件保存路径。
            class_name: 要过滤并导出的班级名称。

        Returns:
            True 表示导出成功，False 表示导出失败。
        """
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                subjects = list(self.dm.subjects)
                header = (
                    ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
                )
                writer.writerow(header)

                class_students = self.dm.get_students_by_class(class_name)
                class_students.sort(
                    key=lambda x: (
                        self.dm.stats(x[0]).get("total", 0)
                        if self.dm.stats(x[0])
                        else 0
                    ),
                    reverse=True,
                )

                for rank, (sid, stu) in enumerate(class_students, 1):
                    st = self.dm.stats(sid)
                    if st is None:
                        continue
                    row_data = (
                        [rank, sid, stu["name"], class_name]
                        + [stu["scores"].get(s, "-") for s in subjects]
                        + [st["total"], st["avg"]]
                    )
                    writer.writerow(row_data)

            return True
        except Exception as e:
            logger.warning("CSV导出失败: %s", e, exc_info=True)
            return False

    # ========== Excel 依赖检查与模板导出（子类共享） ==========

    def _check_excel_available(self) -> bool:
        """检查 Excel 相关依赖是否已安装.

        Returns:
            True 表示 openpyxl 可用，False 表示未安装。

        若不可用，会弹出提示框引导用户安装依赖。
        """
        if not EX_OK:
            logger.error("Excel 操作失败: 库未安装")
            show_error("缺少库", "请执行：pip install openpyxl")
            return False
        return True

    def _export_template(self) -> None:
        """导出成绩录入模板 Excel 文件.

        弹出保存对话框，生成包含当前系统科目的空成绩表模板，
        供用户填写后通过导入功能批量录入学生成绩。
        """
        if not self._check_excel_available():
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="成绩模板.xlsx",
        )
        if not filepath:
            return
        if create_template(filepath, self.dm.subjects):
            self._show_status("模板已保存", "ok")
            logger.info("模板已导出: %s", filepath)
        else:
            logger.error("模板创建失败: %s", filepath)
            show_error("错误", "模板创建失败")

    def _export_excel(self) -> None:
        """导出当前成绩数据为 Excel 文件.

        先检查 Excel 相关依赖是否可用，然后弹出导出选项对话框，
        支持导出全部班级或指定班级的成绩数据。
        """
        if not self._check_excel_available():
            return
        self._show_export_dialog("excel")

    def _export_csv(self) -> None:
        """导出当前成绩数据为 CSV 文件.

        弹出导出选项对话框，支持导出全部班级或指定班级的成绩数据。
        """
        self._show_export_dialog("csv")

    # ========== 头像功能 ==========

    def _load_avatar(self) -> None:
        """加载并显示用户头像.

        同时更新个人中心头像与侧边栏头像（若已初始化）。
        """
        avatar_data = self._get_avatar_data()
        avatar_path = avatar_data.get("avatar", "")
        # 更新个人中心头像
        if hasattr(self, "avatar_label"):
            load_avatar(self.avatar_label, avatar_path)
        # 更新侧边栏头像
        if hasattr(self, "sidebar_avatar_label"):
            load_avatar(self.sidebar_avatar_label, avatar_path, size=(50, 50))
        self.win.update_idletasks()

    def _change_avatar(self) -> None:
        """更换用户头像.

        打开头像更换对话框，用户选择新头像后通过回调保存路径并刷新显示。
        """
        avatar_data = self._get_avatar_data()
        current = avatar_data.get("avatar", "")

        def save_callback(path: str) -> None:
            """头像保存回调函数.

            Args:
                path: 新头像文件的绝对路径。
            """
            try:
                self._save_avatar(path)
                self._load_avatar()
                show_info("成功", "头像已更新并保存")
            except Exception as e:
                logger.warning("头像保存失败: %s", e, exc_info=True)
                show_error("保存失败", f"无法保存头像：{e}")

        try:
            result = change_avatar(self.win, current, save_callback)
            if result is None and current:
                pass
        except Exception as e:
            show_error(
                "错误",
                f"更换头像时发生异常：{e}\n请检查是否安装了 Pillow 库。",
            )

    # ========== 个人中心页面（模板方法 + 钩子） ==========

    def _build_profile_page(self, parent: tk.Frame) -> None:
        """构建个人中心页面（模板方法）.

        展示并允许编辑用户头像、账号（只读）、密码、姓名、手机号与邮箱。
        子类通过实现钩子方法提供差异化标签文本、数据获取与保存逻辑。

        Args:
            parent: 页面父容器 Frame。
        """
        tk.Label(
            parent,
            text=self._get_profile_page_title(),
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        # 头像区域
        avatar_frame = tk.Frame(parent, bg="white")
        avatar_frame.pack(pady=15)
        tk.Label(
            avatar_frame,
            text=self._get_avatar_label_text(),
            font=FONTS["body"],
            bg="white",
        ).pack(side="left", padx=(0, 15))
        self.avatar_label = tk.Label(avatar_frame, bg="white")
        self.avatar_label.pack(side="left")
        self._load_avatar()
        ttk.Button(
            avatar_frame, text="更换头像", command=self._change_avatar
        ).pack(side="left", padx=15)

        # 表单区域
        form_frame = tk.Frame(parent, bg="white")
        form_frame.pack(pady=10, padx=40)

        entry_opts = {"width": 35, "relief": "solid", "bd": 1, "font": FONTS["body"]}

        # 获取个人资料数据
        data = self._get_profile_data()

        # 账号（只读）
        tk.Label(
            form_frame, text=self._get_profile_id_label(), font=FONTS["body"], bg="white"
        ).grid(row=0, column=0, sticky="e", pady=8, padx=10)
        id_entry = tk.Entry(
            form_frame, font=FONTS["body"], width=35, relief="solid", bd=1
        )
        id_entry.insert(0, self._get_profile_id_value())
        id_entry.config(state="readonly", readonlybackground=UI_COLORS["page_bg"])
        id_entry.grid(row=0, column=1, sticky="w")

        # 密码（带显示/隐藏切换）
        tk.Label(
            form_frame, text=self._get_profile_pwd_label(), font=FONTS["body"], bg="white"
        ).grid(row=1, column=0, sticky="e", pady=8, padx=10)
        pwd_frame = tk.Frame(form_frame, bg="white")
        pwd_frame.grid(row=1, column=1, sticky="w")
        pwd_var = tk.StringVar(value=data.get("password", ""))
        pwd_entry = tk.Entry(pwd_frame, textvariable=pwd_var, show="*", **entry_opts)
        pwd_entry.pack(side="left")

        def toggle_pwd():
            if pwd_entry.cget("show") == "*":
                pwd_entry.config(show="")
                toggle_btn.config(text="🙈")
            else:
                pwd_entry.config(show="*")
                toggle_btn.config(text="👁")

        toggle_btn = tk.Button(
            pwd_frame,
            text="👁",
            font=("Segoe UI Emoji", 11),
            bg="white",
            relief="flat",
            cursor="hand2",
            command=toggle_pwd,
        )
        toggle_btn.pack(side="left", padx=5)

        # 密码强度提示（初始隐藏）
        pwd_hint = tk.Label(
            form_frame,
            text="",
            font=FONTS["caption"],
            fg="#E53E3E",
            bg="white",
        )
        pwd_hint.grid(row=1, column=2, sticky="w", padx=8)

        # 姓名
        tk.Label(
            form_frame,
            text=self._get_profile_name_label(),
            font=FONTS["body"],
            bg="white",
        ).grid(row=2, column=0, sticky="e", pady=8, padx=10)
        name_var = tk.StringVar(value=self._get_profile_name_value())
        tk.Entry(form_frame, textvariable=name_var, **entry_opts).grid(
            row=2, column=1, sticky="w"
        )

        # 手机号
        tk.Label(form_frame, text="手机号", font=FONTS["body"], bg="white").grid(
            row=3, column=0, sticky="e", pady=8, padx=10
        )
        phone_var = tk.StringVar(value=data.get("phone", ""))
        tk.Entry(form_frame, textvariable=phone_var, **entry_opts).grid(
            row=3, column=1, sticky="w"
        )

        # 邮箱
        tk.Label(form_frame, text="邮箱", font=FONTS["body"], bg="white").grid(
            row=4, column=0, sticky="e", pady=8, padx=10
        )
        email_var = tk.StringVar(value=data.get("email", ""))
        tk.Entry(form_frame, textvariable=email_var, **entry_opts).grid(
            row=4, column=1, sticky="w"
        )

        def save_profile():
            new_pwd = pwd_var.get().strip()
            valid, msg = validate_password(new_pwd)
            if not valid:
                pwd_hint.config(text=msg)
                return
            try:
                self._save_profile_entity(
                    name=name_var.get().strip(),
                    phone=phone_var.get().strip(),
                    email=email_var.get().strip(),
                    password=new_pwd,
                )
                self._on_profile_saved(name_var.get().strip())
                show_info("成功", "个人信息已保存")
            except Exception as e:
                show_error("错误", f"保存失败：{e}")

        # 实时密码校验（绑定到保存按钮）
        save_btn_ref = []

        def _on_pwd_change(*_):
            new_pwd = pwd_var.get()
            valid, msg = validate_password(new_pwd)
            if valid:
                pwd_hint.config(text="")
                if save_btn_ref:
                    save_btn_ref[0].config(state="normal", bg=UI_COLORS["success"])
            else:
                pwd_hint.config(text=msg)
                if save_btn_ref:
                    save_btn_ref[0].config(state="disabled", bg="#A0AEC0")

        pwd_var.trace_add("write", _on_pwd_change)

        # 保存按钮
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=20)
        save_btn = tk.Button(
            btn_frame,
            text="保存",
            font=FONTS["body"],
            bg=UI_COLORS["success"],
            fg="white",
            activebackground=UI_COLORS["danger_dark"],
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=10,
            command=save_profile,
        )
        save_btn.pack()
        save_btn_ref.append(save_btn)
        # 初始化时触发一次校验（当前密码可能不符合新规则）
        _on_pwd_change()

    # ----- 个人中心钩子方法（子类必须实现） -----

    @abc.abstractmethod
    def _get_profile_page_title(self) -> str:
        """返回个人中心页面标题（如"个人中心"/"个人信息"）."""
        ...

    @abc.abstractmethod
    def _get_avatar_label_text(self) -> str:
        """返回头像区域标签文本（如"管理员头像"/"教师头像"/"学生头像"）."""
        ...

    @abc.abstractmethod
    def _get_profile_id_label(self) -> str:
        """返回账号字段标签文本（如"管理员账号"/"教师工号"/"学生账号"）."""
        ...

    @abc.abstractmethod
    def _get_profile_id_value(self) -> str:
        """返回账号字段只读值."""
        ...

    @abc.abstractmethod
    def _get_profile_pwd_label(self) -> str:
        """返回密码字段标签文本（如"管理员密码"/"教师密码"/"学生密码"）."""
        ...

    @abc.abstractmethod
    def _get_profile_name_label(self) -> str:
        """返回姓名字段标签文本（如"管理员名称"/"教师名称"/"学生名称"）."""
        ...

    @abc.abstractmethod
    def _get_profile_name_value(self) -> str:
        """返回姓名字段初始值."""
        ...

    @abc.abstractmethod
    def _get_profile_data(self) -> dict:
        """返回个人资料数据字典（含 password, phone, email 键）."""
        ...

    @abc.abstractmethod
    def _save_profile_entity(
        self, name: str, phone: str, email: str, password: str
    ) -> None:
        """保存个人资料到数据管理器.

        Args:
            name: 姓名值。
            phone: 手机号值。
            email: 邮箱值。
            password: 密码值。
        """
        ...

    def _on_profile_saved(self, name: str) -> None:
        """保存个人资料后的回调（子类可重写以更新标题等）.

        Args:
            name: 刚保存的姓名值。
        """
        pass

    def _update_header_title_text(self, search_text: str, new_title: str) -> None:
        """更新窗口顶部标题栏中的标签文本.

        遍历主窗口子控件，查找包含 search_text 的 Label 并更新其文本。

        Args:
            search_text: 要搜索的标签文本片段。
            new_title: 替换后的完整标题文本。
        """
        for w in self.win.winfo_children():
            if isinstance(w, tk.Frame) and w.winfo_children():
                for child in w.winfo_children():
                    if isinstance(child, tk.Label) and search_text in child.cget(
                        "text"
                    ):
                        child.config(text=new_title)
                        return

    # ========== 修改密码对话框（模板方法） ==========

    def _change_password(self) -> None:
        """弹出修改密码对话框（模板方法）.

        包含原密码、新密码、确认新密码三个输入框，验证原密码正确性、
        新密码非空且两次输入一致后，调用子类钩子保存新密码。
        """
        dialog = tk.Toplevel(self.win)
        dialog.title("修改密码")
        dialog.geometry("300x220")
        dialog.transient(self.win)
        dialog.grab_set()
        dialog.resizable(False, False)
        win_x = self.win.winfo_x()
        win_y = self.win.winfo_y()
        dialog.geometry(f"300x220+{win_x + 60}+{win_y + 120}")

        tk.Label(dialog, text="原密码：", font=FONTS["body"]).pack(pady=(15, 2))
        old_var = tk.StringVar()
        tk.Entry(dialog, textvariable=old_var).pack()

        tk.Label(dialog, text="新密码：", font=FONTS["body"]).pack(pady=(10, 2))
        new_var = tk.StringVar()
        tk.Entry(dialog, textvariable=new_var).pack()

        tk.Label(dialog, text="确认新密码：", font=FONTS["body"]).pack(pady=(10, 2))
        confirm_var = tk.StringVar()
        tk.Entry(dialog, textvariable=confirm_var).pack()

        def do_change():
            old = old_var.get().strip()
            new = new_var.get().strip()
            confirm = confirm_var.get().strip()
            if old != self._get_current_password():
                show_error("错误", "原密码不正确")
                return
            if not new:
                show_warning("提示", "新密码不能为空")
                return
            if new != confirm:
                show_error("错误", "两次输入的新密码不一致")
                return
            self._update_password(new)
            show_info("成功", "密码已修改")
            dialog.destroy()

        ttk.Button(
            dialog,
            text="确认修改",
            style="primary.TButton",
            command=do_change,
        ).pack(pady=15)

    @abc.abstractmethod
    def _get_current_password(self) -> str:
        """返回当前用户密码（用于原密码验证）."""
        ...

    @abc.abstractmethod
    def _update_password(self, new_password: str) -> None:
        """更新用户密码.

        Args:
            new_password: 新密码明文。
        """
        ...

    # ========== 通知公告页面（只读列表） ==========

    def _build_notices_page(self, parent):
        """构建通知公告页面（只读列表）.

        以 Treeview 展示面向当前角色的通知公告，支持双击查看详情。
        子类通过 _get_notice_role() 钩子提供角色过滤。

        Args:
            parent: 页面父容器 Frame。
        """
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="📢 通知公告", font=FONTS["header"], bg="white").pack(
            anchor="w", padx=20, pady=(15, 10)
        )

        notices = (
            self.dm.get_notices(role=self._get_notice_role())
            if hasattr(self.dm, "get_notices")
            else []
        )

        if not notices:
            tk.Label(
                parent,
                text="暂无通知公告",
                font=FONTS["normal"],
                bg="white",
                fg="#888888",
            ).pack(pady=20)
            return

        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ["标题", "发布者", "日期", "接收对象"]
        self._notice_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=18
        )
        widths = [250, 100, 120, 100]
        for col, width in zip(columns, widths):
            self._notice_tree.heading(col, text=col)
            self._notice_tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self._notice_tree.yview
        )
        self._notice_tree.configure(yscrollcommand=vsb.set)

        self._notice_tree.tag_configure("odd", background=UI_COLORS["row_odd"])
        self._notice_tree.tag_configure("even", background="#FFFFFF")
        self._notice_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for idx, notice in enumerate(notices):
            tag = "odd" if idx % 2 == 0 else "even"
            self._notice_tree.insert(
                "",
                "end",
                values=(
                    notice.get("title", ""),
                    notice.get("publisher", ""),
                    notice.get("date", ""),
                    notice.get("target", "all"),
                ),
                tags=(tag,),
            )

        def _on_double_click(event):
            selection = self._notice_tree.selection()
            if not selection:
                return
            values = self._notice_tree.item(selection[0], "values")
            title = values[0]

            for n in notices:
                if n.get("title") == title:
                    dialog = tk.Toplevel(self.win)
                    dialog.title(f"通知详情 - {title}")
                    dialog.geometry("500x400")
                    dialog.transient(self.win)
                    self._position_dialog(dialog)

                    tk.Label(
                        dialog, text=title, font=FONTS["title"], bg="white"
                    ).pack(anchor="w", padx=20, pady=(20, 10))

                    info = f"发布者：{n.get('publisher', '')}  |  日期：{n.get('date', '')}"
                    tk.Label(
                        dialog,
                        text=info,
                        font=FONTS["caption"],
                        bg="white",
                        fg="#666666",
                    ).pack(anchor="w", padx=20, pady=(0, 15))

                    content_text = tk.Text(dialog, font=FONTS["body"], wrap="word")
                    content_text.insert("1.0", n.get("content", ""))
                    content_text.config(state="disabled")
                    content_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                    break

        self._notice_tree.bind("<Double-1>", _on_double_click)

    def _get_notice_role(self) -> str:
        """返回通知过滤角色（如"teacher"/"student"）.

        子类重写此方法以提供角色特定的通知列表。
        默认返回空字符串，表示获取所有通知。
        """
        return ""

    # ========== 课表查看页面（只读） ==========

    def _build_schedule_view_page(self, parent):
        """构建课表查看页面（只读）.

        提供刷新与查看历史功能，以 Treeview 展示课表信息。
        子类通过 _get_schedule_filter_classes() 控制是否显示班级选择器，
        通过 _get_schedule_class_name() 和 _filter_schedule_entries() 定制数据。

        Args:
            parent: 页面父容器 Frame。
        """
        # 标题和工具栏
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))

        tk.Label(
            header_frame,
            text="📅 课表查看",
            font=("微软雅黑", 18, "bold"),
            fg=TEAL_COLOR,
            bg="white",
        ).pack(side="left")

        # 班级选择器（仅当子类返回非空列表时显示）
        filter_classes = self._get_schedule_filter_classes()
        if filter_classes:
            class_frame = tk.Frame(header_frame, bg="white")
            class_frame.pack(side="right", padx=(0, 5))
            tk.Label(
                class_frame, text="班级:", font=FONTS["body"], bg="white"
            ).pack(side="left", padx=(0, 5))
            self._schedule_class_var = tk.StringVar()
            class_combo = ttk.Combobox(
                class_frame,
                textvariable=self._schedule_class_var,
                values=filter_classes,
                state="readonly",
                width=15,
                font=FONTS["caption"],
            )
            class_combo.pack(side="left")
            if filter_classes:
                self._schedule_class_var.set(filter_classes[0])
            class_combo.bind(
                "<<ComboboxSelected>>", lambda e: self._refresh_schedule_tree()
            )

        tk.Button(
            header_frame,
            text="📜 查看历史",
            font=FONTS["body"],
            bg="#3498DB",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._schedule_show_history,
            padx=16,
            pady=6,
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            header_frame,
            text="🔄 刷新",
            font=FONTS["body"],
            bg="#95A5A6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._refresh_schedule_tree,
            padx=16,
            pady=6,
        ).pack(side="right")

        # Treeview 表格（只读，无ID列）
        columns = ("weekday", "session", "period", "course", "teacher", "room")
        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ysb = ttk.Scrollbar(tree_frame, orient="vertical")

        self._schedule_view_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=ysb.set,
        )
        ysb.config(command=self._schedule_view_tree.yview)

        headings = {
            "weekday": ("星期", 80),
            "session": ("时段", 50),
            "period": ("节次", 50),
            "course": ("课程名", 160),
            "teacher": ("教师", 100),
            "room": ("教室", 80),
        }
        for col, (text, width) in headings.items():
            self._schedule_view_tree.heading(col, text=text)
            self._schedule_view_tree.column(col, width=width, anchor="center")

        self._schedule_view_tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y")

        # 斑马纹样式
        self._schedule_view_tree.tag_configure(
            "oddrow", background=UI_COLORS["row_odd"]
        )
        self._schedule_view_tree.tag_configure("evenrow", background="#FFFFFF")

        # 加载数据
        self._refresh_schedule_tree()

    def _refresh_schedule_tree(self):
        """刷新课表 Treeview.

        获取当前班级的课表数据，经子类过滤后填充到表格中。
        """
        tree = getattr(self, "_schedule_view_tree", None)
        if tree is None:
            return
        for item in tree.get_children():
            tree.delete(item)

        class_name = self._get_schedule_class_name()
        schedules = (
            self.dm.get_schedules(class_name=class_name) if class_name else []
        )
        schedules = self._filter_schedule_entries(schedules)

        for i, s in enumerate(schedules):
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            tree.insert(
                "",
                "end",
                values=(
                    s.get("weekday", ""),
                    s.get("session", ""),
                    s.get("period", ""),
                    s.get("course", ""),
                    s.get("teacher", ""),
                    s.get("room", ""),
                ),
                tags=(tag,),
            )

    # ----- 课表钩子方法（子类可选重写） -----

    def _get_schedule_filter_classes(self) -> list:
        """返回课表筛选班级列表。

        空列表表示不显示班级选择器（如学生端只有固定班级）。
        默认返回空列表，子类可重写以提供班级选择器。
        """
        return []

    def _get_schedule_class_name(self) -> str:
        """返回当前选中的班级名称（用于课表查询）。

        默认从 _schedule_class_var 读取（班级选择器选中值）。
        子类可重写为固定班级名称（如学生端）。
        """
        selected = getattr(self, "_schedule_class_var", None)
        if selected:
            return selected.get()
        return ""

    def _filter_schedule_entries(self, schedules: list) -> list:
        """对课表条目进行二次过滤。

        默认不过滤，子类可重写以实现角色特定过滤（如教师仅显示自己教授的课程）。

        Args:
            schedules: 原始课表列表。

        Returns:
            过滤后的课表列表。
        """
        return schedules

    # ========== 生命周期与事件 ==========

    def run(self) -> dict:
        """启动应用程序主循环.

        进入 tkinter 主事件循环，等待用户交互。窗口关闭后返回注销标志。

        Returns:
            包含 logout 标志的字典。
        """
        self.win.mainloop()
        return {"logout": getattr(self, "_logout", False)}

    def _on_close(self) -> None:
        """窗口关闭时的回调处理.

        尝试保存数据并销毁主窗口。若保存失败则记录警告日志。
        """
        try:
            self.dm.save()
            self.logger.info("数据已保存")
        except Exception as e:
            self.logger.warning("窗口关闭时保存数据失败: %s", e)
        self.win.destroy()

    def _confirm_logout(self) -> None:
        """确认退出登录.

        弹出确认对话框，用户确认后保存数据、设置注销标志并关闭窗口。
        """
        if confirm("确认退出", "确定要退出登录吗？"):
            self._logout = True
            try:
                self.dm.save()
            except Exception as e:
                self.logger.warning("退出登录时保存数据失败: %s", e)
            self.win.destroy()
