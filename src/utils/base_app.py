"""Base application module for Student Grade Management System.

本模块提供 BaseApp 基类，封装了管理员、教师、学生三个端共通的
UI 构建、页面切换、导航按钮、Treeview 创建、导出对话框、头像加载等
功能，减少跨文件代码重复。

主要组件:
    BaseApp: 应用基类，提供所有公共方法与钩子接口。
"""

import csv
import datetime
import logging
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
)
from src.utils.export import export_to_csv, get_default_filename as get_csv_filename

TEAL_COLOR = "#00BFA5"
TEAL_DARK = "#00897B"


class BaseApp:
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
        self.win.configure(bg="#F3F4F6")

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

    def _get_window_title(self) -> str:
        """返回主窗口标题.

        Returns:
            窗口标题字符串。
        """
        raise NotImplementedError

    def _get_header_title(self) -> str:
        """返回顶部横幅标题文本.

        Returns:
            横幅标题字符串。
        """
        raise NotImplementedError

    def _get_user_display_name(self) -> str:
        """返回右上角显示的用户名称.

        Returns:
            用户名字符串。
        """
        raise NotImplementedError

    def _get_avatar_data(self) -> dict:
        """返回头像相关数据.

        Returns:
            包含 "name" 与 "avatar" 键的字典。
        """
        raise NotImplementedError

    def _save_avatar(self, path: str) -> None:
        """保存头像路径到对应用户数据.

        Args:
            path: 新头像文件的绝对路径。
        """
        raise NotImplementedError

    # ========== 样式与 UI 构建 ==========

    def _setup_styles(self) -> None:
        """配置全局 ttk 样式.

        统一 Treeview、Treeview.Heading 及侧边栏按钮的外观。
        """
        style = Style("cosmo")
        style.configure("Treeview", font=("微软雅黑", 12), rowheight=36)
        style.configure(
            "Treeview.Heading",
            font=("微软雅黑", 12, "bold"),
            background="#E6F7F0",
            foreground="#0F766E",
        )
        style.configure(
            "Sidebar.TButton",
            font=("微软雅黑", 12),
            background="#0F766E",
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
            font=("微软雅黑", 12, "bold"),
            padding=(15, 12),
            relief="flat",
            borderwidth=0,
            background="#065F46",
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
            font=("微软雅黑", 16, "bold"),
            fg="white",
            bg=TEAL_COLOR,
        ).pack(side="left", padx=20, pady=12)

        # 右上角用户信息及退出登录按钮
        user_frame = tk.Frame(header, bg=TEAL_COLOR)
        user_frame.pack(side="right", padx=20, pady=12)

        tk.Label(
            user_frame,
            text=f"👤 {self._get_user_display_name()}",
            font=("微软雅黑", 11),
            fg="white",
            bg=TEAL_COLOR,
        ).pack(side="left", padx=(0, 15))

        tk.Button(
            user_frame,
            text="退出登录",
            font=("微软雅黑", 10),
            bg="white",
            fg=TEAL_COLOR,
            activebackground="#E6F7F0",
            activeforeground=TEAL_COLOR,
            relief="flat",
            cursor="hand2",
            command=self._confirm_logout,
            padx=12,
            pady=4,
        ).pack(side="left")

        # ---------- 主容器：侧边栏 + 内容区 ----------
        main_container = tk.Frame(self.win, bg="#F3F4F6")
        main_container.pack(fill="both", expand=True)

        sidebar = tk.Frame(main_container, width=200, bg="#0F766E")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content_area = tk.Frame(main_container, bg="white")
        self.content_area.pack(side="right", fill="both", expand=True)

        # ---------- 侧边栏顶部头像区域 ----------
        avatar_data = self._get_avatar_data()
        avatar_frame = tk.Frame(sidebar, bg="#0F766E", height=80)
        avatar_frame.pack(fill="x", pady=(15, 5))
        avatar_frame.pack_propagate(False)
        try:
            self.sidebar_avatar_label = tk.Label(avatar_frame, bg="#0F766E")
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
                font=("微软雅黑", 28),
                bg="#0F766E",
                fg="white",
            ).pack(pady=5)
        tk.Label(
            avatar_frame,
            text=avatar_data.get("name", ""),
            font=("微软雅黑", 11, "bold"),
            fg="white",
            bg="#0F766E",
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
        spacer = tk.Frame(sidebar, height=20, bg="#0F766E")
        spacer.pack(fill="x")

        # 3. 其他菜单（tk.Label）
        for idx, (text, builder) in enumerate(
            list(self.page_builders.items())[1:], start=1
        ):
            btn = tk.Label(
                sidebar,
                text=text,
                font=("微软雅黑", 12),
                bg="#f8f9fa",
                fg="#495057",
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
                        font=("微软雅黑", 12, "bold"),
                        fg=TEAL_COLOR,
                        bg="#dee2e6",
                    )
            else:
                if idx == 0:
                    btn.configure(style="Sidebar.TButton")
                else:
                    btn.configure(
                        font=("微软雅黑", 12),
                        fg="#495057",
                        bg="#f8f9fa",
                    )
        self.win.update_idletasks()

    def _build_status_bar(self) -> None:
        """构建底部状态栏，显示提示信息、数据统计和实时时钟."""
        bar = tk.Frame(self.win, bg="#E2E8F0", height=60)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status: tk.StringVar = tk.StringVar(value="就绪")
        status_label = tk.Label(
            bar, textvariable=self.status, font=("微软雅黑", 9), bg="#E2E8F0"
        )
        status_label.pack(side="left", padx=12)

        self.clock: tk.StringVar = tk.StringVar()
        clock_label = tk.Label(
            bar, textvariable=self.clock, font=("微软雅黑", 9), bg="#E2E8F0"
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
        """更新状态栏为当前学生和班级数量统计."""
        self.status.set(
            f"  学生 {len(self.dm.students)} 人 | 班级 " f"{len(self.dm.classes)} 个"
        )

    def _update_clock(self) -> None:
        """更新时钟标签为当前日期时间."""
        self.clock.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.win.after(1000, self._update_clock)

    # ========== Treeview 辅助方法 ==========

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

        tree.tag_configure("odd", background="#F8FAFC")
        tree.tag_configure("even", background="#FFFFFF")
        return tree

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
        self.mg_tree.tag_configure("fail", foreground="#EF4444")
        self.mg_tree.tag_configure("warn", foreground="#F59E0B")
        self.mg_tree.tag_configure("good", foreground="#10B981")
        self.mg_tree.tag_configure("empty_all", foreground="#9CA3AF")
        self.mg_tree.tag_configure("odd", background="#F8FAFC")
        self.mg_tree.tag_configure("even", background="#FFFFFF")

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

        self.win.update_idletasks()
        win_x = self.win.winfo_x()
        win_y = self.win.winfo_y()
        dialog.geometry(f"+{win_x + 210}+{win_y + 200}")

        tk.Label(
            dialog,
            text="请选择导出范围",
            font=("微软雅黑", 12, "bold"),
        ).pack(pady=12)

        selected_class = tk.StringVar(value="全部")

        tk.Radiobutton(
            dialog,
            text="导出全部班级",
            variable=selected_class,
            value="全部",
            font=("微软雅黑", 13),
        ).pack(anchor="w", padx=40, pady=4)

        class_frame = tk.Frame(dialog)
        class_frame.pack(anchor="w", padx=40, pady=4, fill="x")
        tk.Radiobutton(
            class_frame,
            text="导出指定班级：",
            variable=selected_class,
            value="指定",
            font=("微软雅黑", 13),
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
            dialog.destroy()
            class_name = ""
            if selected_class.get() == "指定":
                class_name = class_combo.get()
                if not class_name or class_name == "无班级":
                    messagebox.showwarning("提示", "请先选择一个班级")
                    return

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
                messagebox.showinfo("成功", "Excel 导出成功")
            else:
                self.logger.error("Excel 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")
        else:
            if self._export_excel_by_class(filepath, class_name):
                self._show_status(f"Excel 导出成功（{class_name}）", "ok")
                self.logger.info("Excel 导出成功（%s）: %s", class_name, filepath)
                messagebox.showinfo("成功", f"Excel 导出成功（{class_name}）")
            else:
                self.logger.error("Excel 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")

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
                messagebox.showinfo("成功", "CSV 导出成功")
            else:
                self.logger.error("CSV 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")
        else:
            if self._export_csv_by_class(filepath, class_name):
                self._show_status(f"CSV 导出成功（{class_name}）", "ok")
                self.logger.info("CSV 导出成功（%s）: %s", class_name, filepath)
                messagebox.showinfo("成功", f"CSV 导出成功（{class_name}）")
            else:
                self.logger.error("CSV 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")

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
        except Exception:
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
        except Exception:
            return False

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
                messagebox.showinfo("成功", "头像已更新并保存")
            except Exception as e:
                print("ERROR in save_callback:", e)
                messagebox.showerror("保存失败", f"无法保存头像：{e}")

        try:
            result = change_avatar(self.win, current, save_callback)
            if result is None and current:
                pass
        except Exception as e:
            messagebox.showerror(
                "错误",
                f"更换头像时发生异常：{e}\n请检查是否安装了 Pillow 库。",
            )

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
        if messagebox.askyesno("确认退出", "确定要退出登录吗？"):
            self._logout = True
            try:
                self.dm.save()
            except Exception as e:
                self.logger.warning("退出登录时保存数据失败: %s", e)
            self.win.destroy()
