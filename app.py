#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生成绩管理系统 - Student Grade Management System

主程序入口，提供成绩录入、统计排名、科目分析、图表展示、数据导出等功能。
使用 ttkbootstrap 美化界面，青绿色主题。
"""

import csv
import datetime
import logging
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Any, Callable, Optional

# --- 使用 ttkbootstrap 替换标准 ttk ---
from ttkbootstrap import Window, Style
from ttkbootstrap.constants import *

# 导入自定义模块（保持不变）
from modules.data_manager import (
    DataManager,
    DataManagerError,
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidScoreError,
    InvalidInputError,
    DataSaveError,
    DataLoadError,
    DuplicateSubjectError,
    SubjectNotFoundError,
)
from src.config import COLORS, WINDOW_CONFIG, CHART_CONFIG
from src.ui.components import GradientFrame, ModernCard
from src.utils.excel_handler import (
    is_excel_available,
    create_template,
    import_from_excel,
    export_to_excel,
    get_default_filename as get_excel_filename,
)
from src.utils.export import (
    export_to_csv,
    get_default_filename as get_csv_filename,
)

# Excel 库可用性
EX_OK: bool = is_excel_available()

# 尝试导入 matplotlib 用于图表展示
try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np
    import sys

# 根据操作系统自动选择中文字体
    if sys.platform.startswith('win'):
        # Windows 系统
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    elif sys.platform.startswith('darwin'):
        # macOS 系统
        plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti TC", "Arial Unicode MS"]
    else:
        # Linux 或其他系统
        plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MAT_OK: bool = True
except ImportError as e:
    print(f"Matplotlib 导入失败: {e}")
    MAT_OK = False

# 配置日志
logger = logging.getLogger("App")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(_handler)

# 设置项目基础路径
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# ==================== 颜色常量 ====================
TEAL_COLOR = "#00BFA5"      # 青绿色主色调（顶部横幅背景）
TEAL_DARK = "#00897B"       # 深青绿色（鼠标悬停或文字颜色）
TEAL_LIGHT = "#E0F2F1"      # 浅青绿色（卡片、背景区域可选）


class App:
    """学生成绩管理系统主应用程序类。"""

    def __init__(self) -> None:
        """初始化应用程序，创建窗口、样式和 UI 布局。"""
        try:
            self.dm: DataManager = DataManager()
            logger.info("数据管理器初始化成功")
        except DataLoadError as e:
            logger.error("数据管理器初始化失败: %s", e)
            messagebox.showerror(
                "数据错误",
                f"无法加载数据文件，系统将使用空数据启动。\n\n错误详情: {e}",
            )
            self.dm = DataManager()

        # 使用 ttkbootstrap 的窗口
        self.win = Window(themename="cosmo")  # "cosmo" 主题是青蓝色系
        self.win.title(WINDOW_CONFIG["title"])
        self.win.state("zoomed")
        self.win.minsize(WINDOW_CONFIG["min_width"], WINDOW_CONFIG["min_height"])
        self.win.configure(bg=COLORS["bg"])

        # 自定义样式：强制顶部横幅为青绿色
        style = Style()
        style.configure("Header.TFrame", background=TEAL_COLOR)
        style.configure("Header.TLabel", background=TEAL_COLOR, foreground="white", font=("微软雅黑", 16, "bold"))
        style.configure("Sidebar.TFrame", background="#f8f9fa")
        style.configure("Content.TFrame", background="white")

        style.configure(
            "Treeview",
            font=("微软雅黑", 13),       # 字体变大
            rowheight=40,                # 行高变大（上下距离）
            padding=(12, 6),             # 单元格左右内边距
            background="white",
            fieldbackground="white"
        )
        style.configure(
            "Treeview.Heading",
            font=("微软雅黑", 13, "bold"),  # 表头更大
            padding=(10, 8),
            background="#E6F7F0",         # 淡绿色表头背景
            foreground="#0F766E"          # 深绿色表头文字
        )

        # ========== 侧边栏按钮三套核心样式 ==========
        style.configure("Sidebar.TButton",
            font=("微软雅黑", 12),
            background="#0F766E",
            padding=(15, 12),
            relief="flat",
            borderwidth=0
        )
        style.map("Sidebar.TButton",
            background=[("active", "#e9ecef")],
            foreground=[("active", "#00897B")]
        )
        style.configure("Sidebar.Active.TButton",
            font=("微软雅黑", 12, "bold"),
            padding=(15, 12),
            relief="flat",
            borderwidth=0,
            background="#065F46",
            foreground="white"
        )

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
        logger.info("应用程序初始化完成")

    def run(self) -> None:
        """启动应用程序主循环。"""
        self.win.mainloop()

    def _on_close(self) -> None:
        """窗口关闭时的清理操作。"""
        try:
            self.dm.save()
            logger.info("应用程序正常关闭，数据已保存")
        except DataSaveError as e:
            logger.error("关闭时保存数据失败: %s", e)
        self.win.destroy()

    # ========== UI 构建：顶部横幅 + 左侧菜单 + 右侧内容 ==========

    def _build_ui(self) -> None:
        # 1. 顶部青绿色横幅
        header = tk.Frame(self.win, bg=TEAL_COLOR, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="🎓 学生成绩管理系统",
            font=("微软雅黑", 16, "bold"),
            fg="white",
            bg=TEAL_COLOR,
        ).pack(side="left", padx=20, pady=12)

        # 2. 主容器：左侧菜单 + 右侧内容
        main_container = tk.Frame(self.win, bg=COLORS["bg"])
        main_container.pack(fill="both", expand=True)

        # ========== 美化后左侧侧边栏 ==========
        sidebar = tk.Frame(main_container, width=200, bg="#0F766E")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # 右侧内容区域（保留不变）
        self.content_area = tk.Frame(main_container, bg="white")
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # 页面映射（功能完全不变）
        self.page_builders = {
            "📊 仪表盘": self._build_dashboard_page,
            "📝 录入": self._build_input_page,
            "📥 Excel": self._build_excel_page,
            "🏫 班级": self._build_class_page,
            "📁 管理": self._build_manage_page,
            "🔍 查询": self._build_search_page,
            "📊 分析": self._build_analysis_page,
            "📈 图表": self._build_chart_page,
        }
        
        self.nav_buttons = []
        
        # -------------- 1. 先单独放【仪表盘】--------------
        idx = 0
        text, builder = list(self.page_builders.items())[idx]
        
        def cmd(b=builder, btn_idx=idx):
            self._switch_page(b)
            self._set_active_button(btn_idx)
        
        btn = ttk.Button(
            sidebar,
            text=text,
            style="Sidebar.TButton",
            command=cmd
        )
        # 仪表盘：左右留一点边，上下不要pady，避免多余空隙
        btn.pack(fill="x", padx=15, ipady=5)
        self.nav_buttons.append(btn)
        
        # -------------- 2. 只在这里加空隙（仪表盘 ↔ 录入）--------------
        # 高度你可以改，比如 20、25、30
        spacer = tk.Frame(sidebar, height=20, bg="#0F766E")
        spacer.pack(fill="x")
        
        # -------------- 3. 录入及以下：紧挨着，无空隙 --------------
        for idx, (text, builder) in enumerate(list(self.page_builders.items())[1:], start=1):
            def cmd(b=builder, btn_idx=idx):
                self._switch_page(b)
                self._set_active_button(btn_idx)
        
            btn = tk.Label(
                sidebar,
                text=text,
                font=("微软雅黑", 12),
                bg="#f8f9fa",
                fg="#495057",
                cursor="hand2",
            )
            btn.bind("<Button-1>", lambda e, b=builder, i=idx: (self._switch_page(b), self._set_active_button(i)))
        
            btn.pack(fill="x", padx=15, ipady=8)
            self.nav_buttons.append(btn)
        
        # 默认选中第一个【仪表盘】按钮
        if self.nav_buttons:
            self.nav_buttons[0].configure(style="Sidebar.Active.TButton")
        
        # 默认显示仪表盘
        self._switch_page(self._build_dashboard_page)

        # 5. 状态栏（保留）
        self._build_status_bar()

    def _switch_page(self, builder_func) -> None:
        """切换右侧内容区域。"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        page_frame = tk.Frame(self.content_area, bg="white")
        page_frame.pack(fill="both", expand=True, padx=10, pady=10)
        builder_func(page_frame)

    def _set_active_button(self, active_idx: int) -> None:
        """切换导航按钮选中状态。"""
        for idx, btn in enumerate(self.nav_buttons):
            if idx == active_idx:
                if idx == 0:
                    btn.configure(style="Sidebar.Active.TButton")
                else:
                    btn.configure(font=("微软雅黑", 12, "bold"), fg=TEAL_COLOR, bg="#e9ecef")
            else:
                if idx == 0:
                    btn.configure(style="Sidebar.TButton")
                else:
                    btn.configure(font=("微软雅黑", 12), fg="#495057", bg="#f8f9fa")

    def _build_status_bar(self) -> None:
        """构建底部状态栏。"""
        bar = tk.Frame(self.win, bg="#E2E8F0", height=60)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status: tk.StringVar = tk.StringVar(value="就绪")
        tk.Label(
            bar, textvariable=self.status, font=("微软雅黑", 9), bg="#E2E8F0"
        ).pack(side="left", padx=12)

        self.clock: tk.StringVar = tk.StringVar()
        tk.Label(
            bar, textvariable=self.clock, font=("微软雅黑", 9), bg="#E2E8F0"
        ).pack(side="right", padx=12)

        # 已删除：备份和恢复按钮

        self._update_clock()
        self._update_status()

    # ========== 仪表盘页面（卡片风格） ==========

    def _build_dashboard_page(self, parent: tk.Frame) -> None:
        # 顶部欢迎横幅
        banner = tk.Frame(parent, bg=TEAL_COLOR, height=80)
        banner.pack(fill="x")
        tk.Label(banner, text="👋 欢迎回来，admin", font=("微软雅黑", 18, "bold"),
                 fg="white", bg=TEAL_COLOR).pack(pady=(12, 2))
        tk.Label(banner, text=f"当前角色：管理员 | {datetime.datetime.now().strftime('%Y年%m月%d日')}",
                 font=("微软雅黑", 10), fg="#e0f2f1", bg=TEAL_COLOR).pack()

        # 统计卡片行
        card_row = tk.Frame(parent, bg="white")
        card_row.pack(fill="x", pady=10)

        self.da_cards = {}  # 存储卡片数值标签，便于刷新

        def create_card(container, icon, title, value, color):
            card = tk.Frame(container, bg="white", relief="solid", bd=1)
            card.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(card, text=icon, font=("微软雅黑", 20), bg="white").pack(anchor="w", padx=10, pady=5)
            tk.Label(card, text=title, font=("微软雅黑", 10), fg="#6b7280", bg="white").pack(anchor="w", padx=10)
            val_lbl = tk.Label(card, text=str(value), font=("微软雅黑", 24, "bold"), fg=color, bg="white")
            val_lbl.pack(anchor="w", padx=10, pady=5)
            return val_lbl

        self.da_cards["students"] = create_card(card_row, "👥", "学生总数", len(self.dm.students), TEAL_COLOR)
        self.da_cards["subjects"] = create_card(card_row, "📚", "科目数量", len(self.dm.subjects), "#8B5CF6")
        self.da_cards["classes"] = create_card(card_row, "🏫", "班级数量", len(self.dm.classes), "#10B981")
        self.da_cards["warnings"] = create_card(card_row, "⚠️", "预警人数", len(self.dm.get_warnings()), "#EF4444")

        # 下边区域：左侧图表 + 右侧预警列表
        chart_row = tk.Frame(parent, bg="white")
        chart_row.pack(fill="both", expand=True, pady=10)

        # 左：科目均分图
        left_chart = tk.Frame(chart_row, bg="white", bd=1, relief="solid")
        left_chart.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(left_chart, text="📈 各科目平均分", font=("微软雅黑", 11, "bold"), bg="white").pack(pady=5)
        self.da_subj_frame = tk.Frame(left_chart, bg="white")
        self.da_subj_frame.pack(fill="both", expand=True, padx=8, pady=(0, 5))

        # 右：预警列表
        right_list = tk.Frame(chart_row, bg="white", bd=1, relief="solid")
        right_list.pack(side="right", fill="both", expand=True, padx=5)
        tk.Label(right_list, text="⚠️ 成绩预警", font=("微软雅黑", 11, "bold"), bg="white").pack(pady=5)
        self.da_warn_frame = tk.Frame(right_list, bg="white")
        self.da_warn_frame.pack(fill="both", expand=True, padx=8, pady=(0, 5))

        self._refresh_dashboard()

    # ========== 成绩录入页面 ==========

    def _build_input_page(self, parent: tk.Frame) -> None:
        """构建成绩录入页面。"""
        tk.Label(
            parent,
            text="📝 批量录入",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack()
        buttons = [
            ("➕ 加行", self._input_add_row),
            ("🗑️ 删行", self._input_delete_row),
            ("💾 保存", self._input_save_rows),
            ("🔄 清空", self._input_clear_rows),
        ]
        for text, cmd in buttons:
            ttk.Button(btn_frame, text=text, style="primary.TButton", command=cmd).pack(
                side="left", padx=4
            )

        subjects = self.dm.subjects
        columns = ["行号", "学号*", "姓名*", "班级"] + subjects + ["操作"]
        widths = [45, 100, 90, 90] + self._calc_subject_widths(subjects) + [70]
        self.in_tree = self._create_treeview(parent, columns, widths, 12)
        self.in_tree.bind("<Double-1>", self._input_cell_double_click)

        for _ in range(5):
            self._input_add_row()

    # ========== Excel 导入导出页面 ==========

    def _build_excel_page(self, parent: tk.Frame) -> None:
        """构建 Excel 导入导出页面。"""
        tk.Label(
            parent,
            text="📥 Excel 导入导出",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack()
        ttk.Button(
            btn_frame,
            text="📥 模板",
            style="success.TButton",
            command=self._export_template,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="📥 导入",
            style="primary.TButton",
            command=self._import_excel,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="📤 导出 Excel",
            style="warning.TButton",
            command=self._export_excel,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="📤 导出 CSV",
            style="secondary.TButton",
            command=self._export_csv,
        ).pack(side="left", padx=4)

        subjects = self.dm.subjects
        columns = ["学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        widths = [100, 90, 90] + self._calc_subject_widths(subjects) + [80, 80]
        self.ex_tree = self._create_treeview(parent, columns, widths, 16)
        self._refresh_excel_tree()

    # ========== 班级管理页面 ==========

    def _build_class_page(self, parent: tk.Frame) -> None:
        """构建班级管理页面。"""
        tk.Label(
            parent,
            text="🏫 班级管理",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=(10, 15))  # 按钮栏上下留空隙
        ttk.Button(
            btn_frame,
            text="➕ 添加班级",
            style="success.TButton",
            command=self._class_add,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="🔄 刷新",
            style="primary.TButton",
            command=self._refresh_class_tree,
        ).pack(side="left", padx=4)

        # ========== ✅ 直接创建表格，不调用 _create_treeview ==========
        columns = ["班级名称", "学生人数", "平均分", "最高分", "最低分", "操作"]
        widths = [150, 80, 80, 80, 80, 120]
        
        # 1. 创建外层容器 frame（用于装表格和滚动条）
        frame = tk.Frame(parent, bg="white")
        frame.pack(pady=(0, 10), fill="both", expand=True)
        
        # 2. 创建表格
        self.cl_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # 3. 添加滚动条
        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.cl_tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.cl_tree.xview)
        self.cl_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # 4. 设置列宽
        for col, width in zip(columns, widths):
            self.cl_tree.heading(col, text=col)
            self.cl_tree.column(col, width=width, anchor="center")
        
        # 5. 放置滚动条和表格
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.cl_tree.pack(fill="both", expand=True)
        
        # 6. 添加斑马纹样式
        self.cl_tree.tag_configure("odd", background="#F8FAFC")
        self.cl_tree.tag_configure("even", background="#FFFFFF")
        
        # 7. 绑定双击事件
        self.cl_tree.bind("<Double-1>", self._class_double_click)

        # 8. 刷新数据
        self._refresh_class_tree()

    # ========== 成绩管理页面 ==========

    def _build_manage_page(self, parent: tk.Frame) -> None:
        """构建成绩管理页面。"""
        tk.Label(
            parent,
            text="📁 成绩管理",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        # ====== 过滤 + 操作按钮栏 ======
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=2)

        # 班级过滤
        tk.Label(btn_frame, text="班级过滤：", font=("微软雅黑", 13), bg="white").pack(side="left", padx=(10, 2))
        classes = ["全部班级"] + self.dm.classes
        self.mg_filter_class = tk.StringVar(value="全部班级")
        self.mg_class_cb = ttk.Combobox(
            btn_frame,
            textvariable=self.mg_filter_class,
            values=classes,
            width=10,
            state="readonly",
        )
        self.mg_class_cb.pack(side="left", padx=(0, 8))
        self.mg_class_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_manage_tree())

        # 成绩范围筛选
        tk.Label(btn_frame, text="成绩范围：", font=("微软雅黑", 13), bg="white").pack(side="left", padx=(5, 2))
        self.mg_filter_score = tk.StringVar(value="全部")
        self.mg_score_cb = ttk.Combobox(
            btn_frame,
            textvariable=self.mg_filter_score,
            values=["全部", "不及格 (<60)", "及格 (60-69)", "良好 (70-89)", "优秀 (≥90)"],
            width=12,
            state="readonly",
        )
        self.mg_score_cb.pack(side="left", padx=(0, 15))
        self.mg_score_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_manage_tree())

        ttk.Button(
            btn_frame,
            text="🗑️ 删除",
            style="danger.TButton",
            command=self._manage_delete_selected,
        ).pack(side="left", padx=4)

        subjects = self.dm.subjects
        columns = ["学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        widths = [110, 90, 90] + self._calc_subject_widths(subjects) + [80, 80]
        self.mg_tree = self._create_treeview(parent, columns, widths, 18)
        # ====== ✅ 新增：颜色预警标签 ======
        self.mg_tree.tag_configure("fail", foreground="#EF4444")      # 不及格 → 红色
        self.mg_tree.tag_configure("warn", foreground="#F59E0B")      # 偏低 → 橙色
        self.mg_tree.tag_configure("good", foreground="#10B981")      # 全优 → 绿色
        self.mg_tree.tag_configure("empty_all", foreground="#9CA3AF") # 全部缺考 → 灰色
        # ========================================
        self.mg_tree.bind("<Double-1>", self._manage_cell_double_click)

        # ====== 列头点击排序 ======
        self._mg_sort_asc = True
        self._mg_sort_col = ""
        for col in columns:
            self.mg_tree.heading(col, command=lambda c=col: self._manage_sort_tree(c))

        self._refresh_manage_tree()

    # ========== 查询页面 ==========

    def _build_search_page(self, parent: tk.Frame) -> None:
        """构建搜索查询页面。"""
        tk.Label(
            parent,
            text="🔍 搜索查询",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        search_frame = tk.Frame(parent, bg="white")
        search_frame.pack(pady=3)
        self.se_var = tk.StringVar()
        self.se_entry = ttk.Entry(
            search_frame,
            textvariable=self.se_var,
            font=("微软雅黑", 11),
            width=20,
        )
        self.se_entry.pack(side="left", padx=4)
        self.se_entry.bind("<KeyRelease>", lambda e: self._search_execute())
        ttk.Button(
            search_frame,
            text="🔍 搜索",
            style="primary.TButton",
            command=self._search_execute,
        ).pack(side="left")
        ttk.Button(
            search_frame,
            text="🔄 全部",
            style="warning.TButton",
            command=self._refresh_search_list,
        ).pack(side="left")
        ttk.Button(
            search_frame,
            text="🗑️ 删除",
            style="danger.TButton",
            command=self._search_delete_selected,
        ).pack(side="left", padx=8)

        main_frame = tk.Frame(parent, bg="white")
        main_frame.pack(fill="both", expand=True, padx=5, pady=3)

        # 左侧：学生列表
        left_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        left_frame.pack(side="left", fill="y", padx=3, pady=3)
        self.se_list = tk.Listbox(
            left_frame,
            font=("微软雅黑", 13),
            bg="white",
            selectbackground="#DBEAFE",
            selectborderwidth=3,
            width=32
        )
        self.se_list.pack(fill="both", expand=True, ipady=20)
        self.se_list.bind("<<ListboxSelect>>", self._search_show_detail)
        self.se_list.config(selectbackground="#B6BDC1")
        # 右侧：学生详情
        detail_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        detail_frame.pack(side="right", fill="both", expand=True, padx=3, pady=3)

        # 标题栏（包含历史按钮）
        header_frame = tk.Frame(detail_frame, bg="white")
        header_frame.pack(fill="x", pady=4, padx=10)
        tk.Label(
            header_frame,
            text="📋 学生详情",
            font=("微软雅黑", 13, "bold"),
            bg="white",
        ).pack(side="left")
        ttk.Button(
            header_frame,
            text="📜 查看历史",
            style="primary.TButton",
            command=lambda: self._search_show_history(self.dv["sid"].get() if hasattr(self, "dv") else "")
        ).pack(side="right")

        self.dv = {}
        info_frame = tk.Frame(detail_frame, bg="white")
        info_frame.pack(pady=3)
        for i, (key, label) in enumerate([("sid", "学号"), ("name", "姓名"), ("cls", "班级")]):
            tk.Label(info_frame, text=f"{label}：", bg="white", font=("微软雅黑", 12)).grid(row=i, column=0, sticky="w", padx=10, pady=2)
            self.dv[key] = tk.StringVar(value="—")
            tk.Label(info_frame, textvariable=self.dv[key], font=("微软雅黑", 13, "bold"), bg="white").grid(row=i, column=1, sticky="w", padx=10, pady=2)

        self.stt = ttk.Treeview(
            detail_frame,
            columns=["科目", "成绩", "等级"],
            show="headings",
            height=12,
        )
        for col, width in [("科目", 120), ("成绩", 80), ("等级", 80)]:
            self.stt.heading(col, text=col)
            self.stt.column(col, width=width, anchor="center")
        self.stt.pack(pady=10, padx=10, fill="both", expand=True)

        level_tags = [("excellent", "#D1FAE5"), ("good", "#DBEAFE"), ("pass_", "#FEF9C3"), ("fail", "#FEE2E2")]
        for tag, bg in level_tags:
            self.stt.tag_configure(tag, background=bg)

        summary_frame = tk.Frame(detail_frame, bg="#F0F9FF")
        summary_frame.pack(pady=5, fill="x")
        for label, key in [("总分", "total"), ("平均分", "avg")]:
            tk.Label(summary_frame, text=label + ":", bg="#F0F9FF", font=("微软雅黑", 12)).pack(side="left", padx=30)
            self.dv[key] = tk.StringVar(value="—")
            tk.Label(summary_frame, textvariable=self.dv[key], font=("微软雅黑", 18, "bold"), fg="#1E3A8A", bg="#F0F9FF").pack(side="left", padx=10)

        self._refresh_search_list()

    # ========== 科目分析页面 ==========

    def _build_analysis_page(self, parent: tk.Frame) -> None:
        """构建科目分析页面。"""
        tk.Label(
            parent,
            text="📊 科目分析",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        control_frame = tk.Frame(parent, bg="white")
        control_frame.pack(pady=3)
        tk.Label(control_frame, text="科目：", bg="white").pack(side="left", padx=5)
        first_subject = self.dm.subjects[0] if self.dm.subjects else ""
        self.an_subj = tk.StringVar(value=first_subject)
        self.an_cb = ttk.Combobox(control_frame, textvariable=self.an_subj, values=self.dm.subjects, width=10, state="readonly")
        self.an_cb.pack(side="left", padx=5)
        ttk.Button(control_frame, text="📊 分析", style="primary.TButton", command=self._analyze_subject).pack(side="left", padx=5)
        ttk.Button(control_frame, text="⚙️ 科目管理", style="warning.TButton", command=self._manage_subjects).pack(side="left", padx=5)

        main_frame = tk.Frame(parent, bg="white")
        main_frame.pack(fill="both", expand=True, padx=5, pady=3)

        # 左侧：统计信息
        left_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        left_frame.pack(side="left", fill="y", padx=3, pady=3)
        tk.Label(left_frame, text="📈 统计信息", font=("微软雅黑", 11, "bold"), bg="white").pack(pady=4)
        self.alab = {}
        stat_items = [("人数", "cnt"), ("最高", "mx"), ("最低", "mn"), ("均分", "av"), ("及格率", "ps"), ("优秀率", "ex") ]
        for label, key in stat_items:
            row = tk.Frame(left_frame, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label + "：", bg="white").pack(side="left", padx=10)
            self.alab[key] = tk.Label(row, text="—", font=("微软雅黑", 10, "bold"), bg="white")
            self.alab[key].pack(side="left")

        self.adist = ttk.Treeview(left_frame, columns=["段", "人", "%"], show="headings", height=6)
        for col, width in [("段", 60), ("人", 40), ("%", 50)]:
            self.adist.heading(col, text=col)
            self.adist.column(col, width=width, anchor="center")
        self.adist.pack(pady=6)
        dist_tags = [("0-59", "#FEE2E2"), ("60-69", "#FEF3C7"), ("70-79", "#FEF9C3"), ("80-89", "#DBEAFE"), ("90-100", "#D1FAE5")]
        for seg, bg in dist_tags:
            self.adist.tag_configure(seg, background=bg)

        # 右侧：成绩明细
        right_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        right_frame.pack(side="right", fill="both", expand=True, padx=3, pady=3)
        tk.Label(right_frame, text="📋 成绩明细", font=("微软雅黑", 11, "bold"), bg="white").pack(pady=4)
        detail_cols = ["名次", "学号", "姓名", "班级", "成绩", "等级"]
        detail_widths = [50, 110, 90, 90, 80, 80]
        self.adt = ttk.Treeview(right_frame, columns=detail_cols, show="headings", height=20)
        for col, width in zip(detail_cols, detail_widths):
            self.adt.heading(col, text=col)
            self.adt.column(col, width=width, anchor="center")
        self.adt.pack(fill="both", expand=True, padx=10, pady=10)
        level_tags = [("excellent", "#D1FAE5"), ("good", "#DBEAFE"), ("pass_", "#FEF9C3"), ("fail", "#FEE2E2")]
        for tag, bg in level_tags:
            self.adt.tag_configure(tag, background=bg)

        # 默认分析第一个科目
        if self.dm.subjects:
            self.win.after(100, self._analyze_subject)

    # ========== 图表页面 ==========

    def _build_chart_page(self, parent: tk.Frame) -> None:
        """构建图表页面。"""
        if not MAT_OK:
            tk.Label(parent, text="⚠️ 未安装 matplotlib，无法使用图表功能", fg="red", font=("微软雅黑", 12)).pack(expand=True)
            return

        tk.Label(parent, text="📈 数据图表", font=("微软雅黑", 14, "bold"), bg="white").pack(pady=4)
        control_frame = tk.Frame(parent, bg="white")
        control_frame.pack()
        chart_buttons = [
            ("总分排名", self._chart_total_ranking),
            ("平均分对比", self._chart_avg_comparison),
            ("成绩分布", self._chart_histogram),
            ("雷达图", self._chart_radar),
            ("箱线图", self._chart_boxplot),
        ]
        for text, cmd in chart_buttons:
            ttk.Button(control_frame, text=text, style="primary.TButton", command=cmd).pack(side="left", padx=3)

        tk.Label(control_frame, text="科目（仅成绩分布使用）：", bg="white", fg="#64748B", font=("微软雅黑", 9)).pack(side="left", padx=(10, 2))
        first_subject = self.dm.subjects[0] if self.dm.subjects else ""
        self.ch_subj = tk.StringVar(value=first_subject)
        self.ch_cb = ttk.Combobox(control_frame, textvariable=self.ch_subj, values=self.dm.subjects, width=10, state="readonly")
        self.ch_cb.pack(side="left")
        self.ch_subj.trace("w", lambda *args: self._chart_histogram())

        self.ct = tk.Frame(parent, bg="white")
        self.ct.pack(fill="both", expand=True)

        if self.dm.students:  # 有数据才显示，避免报错
            self._chart_total_ranking()

    # ========== 公共工具方法 ==========

    @staticmethod

    def _get_level(score: float) -> str:
        if score >= 90:
            return "优秀"
        if score >= 75:
            return "良好"
        if score >= 60:
            return "及格"
        return "不及格"

    @staticmethod

    def _get_level_tag(score: float) -> tuple[str, str]:
        if score >= 90:
            return "excellent", "优秀"
        if score >= 75:
            return "good", "良好"
        if score >= 60:
            return "pass_", "及格"
        return "fail", "不及格"

    def _check_excel_available(self) -> bool:
        if not EX_OK:
            logger.error("Excel 操作失败: 库未安装")
            messagebox.showerror("缺少库", "请执行：pip install openpyxl")
            return False
        return True

    def _show_status(self, text: str, level: str = "info") -> None:
        icons = {"info": "ℹ️", "ok": "✅", "warn": "⚠️", "err": "❌"}
        self.status.set(f"  {icons.get(level, 'ℹ️')}  {text}")

    def _update_status(self) -> None:
        self._show_status(f"学生 {len(self.dm.students)} 人 | 科目 {len(self.dm.subjects)} 门")

    def _update_clock(self) -> None:
        self.clock.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.win.after(1000, self._update_clock)

    def _refresh_all_pages(self) -> None:
        if hasattr(self, "mg_tree"):
            self._refresh_manage_tree()
        if hasattr(self, "ex_tree"):
            self._refresh_excel_tree()
        if hasattr(self, "se_list"):
            self._refresh_search_list()
        if hasattr(self, "da_cards"):
            self._refresh_dashboard()
        if hasattr(self, "cl_tree"):
            self._refresh_class_tree()

    def _calc_subject_widths(self, subjects: list[str], min_width: int = 72) -> list[int]:
        return [max(min_width, len(s) * 14) for s in subjects]

    def _create_treeview(self, parent: tk.Frame, columns: list[str], widths: list[int], height: int = 14, pack_frame: bool = True) -> ttk.Treeview:
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

        # 斑马纹
        tree.tag_configure("odd", background="#F8FAFC")
        tree.tag_configure("even", background="#FFFFFF")
        return tree

    # ========== 录入页面方法 ==========

    def _input_add_row(self) -> None:
        n = len(self.in_tree.get_children()) + 1
        values = [n, "", "", ""] + [""] * len(self.dm.subjects) + ["删除"]
        tag = "odd" if n % 2 == 1 else "even"
        self.in_tree.insert("", "end", values=values, tags=(tag,))

    def _input_delete_row(self) -> None:
        selected = self.in_tree.selection()
        if not selected:
            return
        for item in selected:
            self.in_tree.delete(item)
        for i, item in enumerate(self.in_tree.get_children(), 1):
            vals = list(self.in_tree.item(item, "values"))
            vals[0] = i
            tag = "odd" if i % 2 == 1 else "even"
            self.in_tree.item(item, values=vals, tags=(tag,))

    def _input_clear_rows(self) -> None:
        if messagebox.askyesno("确认", "确定清空所有录入内容？"):
            self.in_tree.delete(*self.in_tree.get_children())
            for _ in range(5):
                self._input_add_row()

    def _input_cell_double_click(self, event: tk.Event) -> None:
        row_id = self.in_tree.identify_row(event.y)
        col_id = self.in_tree.identify_column(event.x)
        if not row_id:
            return
        col_index = int(col_id.replace("#", "")) - 1
        columns = self.in_tree["columns"]
        if col_index >= len(columns) or columns[col_index] == "操作":
            return

        x, y, w, h = self.in_tree.bbox(row_id, col_id)
        entry = tk.Entry(self.in_tree, font=("微软雅黑", 10), relief="solid")
        entry.insert(0, self.in_tree.item(row_id, "values")[col_index])
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()

        def _commit_edit() -> None:
            vals = list(self.in_tree.item(row_id, "values"))
            val = entry.get().strip()
            columns = self.in_tree["columns"]
            if 4 <= col_index < len(columns) - 1 and val:
                try:
                    score = float(val)
                    if score < 0 or score > 100:
                        messagebox.showwarning("输入错误", "成绩必须在 0-100 之间！")
                        val = ""
                except ValueError:
                    messagebox.showwarning("输入错误", "成绩必须是数字！")
                    val = ""
            vals[col_index] = val
            entry.destroy()
            self.in_tree.item(row_id, values=vals)

        entry.bind("<Return>", lambda _: _commit_edit())
        entry.bind("<Escape>", lambda _: entry.destroy())
        entry.bind("<FocusOut>", lambda _: _commit_edit())

    def _input_save_rows(self) -> None:
        subjects = self.dm.subjects
        saved = 0
        errors = []

        for item in self.in_tree.get_children():
            vals = self.in_tree.item(item, "values")
            sid = str(vals[1]).strip()
            name = str(vals[2]).strip()
            cls = str(vals[3]).strip()
            scores_raw = vals[4:4 + len(subjects)]

            if not sid and not name and not cls and all(str(x).strip() == "" for x in scores_raw):
                continue
            if not sid:
                errors.append(f"行 {vals[0]}: 学号不能为空")
                continue

            scores_dict = {}
            for subj, sc in zip(subjects, scores_raw):
                sc = str(sc).strip()
                if sc:
                    try:
                        score = float(sc)
                        if score < 0 or score > 100:
                            errors.append(f"行 {vals[0]}: {subj} 成绩超出范围 (0-100)")
                            continue
                        scores_dict[subj] = score
                    except ValueError:
                        errors.append(f"行 {vals[0]}: {subj} 成绩无效")
                        continue

            try:
                if self.dm.exists(sid):
                    self.dm.upd_stu(sid, name, cls)
                else:
                    self.dm.add_stu(sid, name, cls)
                self.dm.batch_set(sid, scores_dict)
                saved += 1
            except Exception as e:
                errors.append(f"行 {vals[0]}: {e}")

        if errors:
            messagebox.showwarning("部分失败", "\n".join(errors[:10]))
        if saved:
            messagebox.showinfo("成功", f"保存 {saved} 名学生信息")
            self._show_status(f"保存 {saved} 人", "ok")
            self._refresh_all_pages()
            logger.info("录入保存: %d 名学生", saved)
        elif not errors:
            messagebox.showinfo("提示", "无有效数据可保存")

    # ========== Excel 页面方法 ==========

    def _refresh_excel_tree(self) -> None:
        self.ex_tree.delete(*self.ex_tree.get_children())
        for idx, (sid, stu) in enumerate(sorted(self.dm.students.items(), key=lambda x: x[0])):
            st = self.dm.stats(sid)
            if st is None:
                continue
            vals = [sid, stu["name"], stu.get("class", "")] + [stu["scores"].get(s, "-") for s in self.dm.subjects] + [st["total"], st["avg"]]
            base_tag = "odd" if idx % 2 == 0 else "even"
            self.ex_tree.insert("", "end", values=vals, tags=(base_tag,))

    def _export_template(self) -> None:
        if not self._check_excel_available():
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], initialfile="成绩模板.xlsx")
        if not filepath:
            return
        if create_template(filepath, self.dm.subjects):
            self._show_status("模板已保存", "ok")
            logger.info("模板已导出: %s", filepath)
        else:
            logger.error("模板创建失败: %s", filepath)
            messagebox.showerror("错误", "模板创建失败")

    def _import_excel(self) -> None:
        if not self._check_excel_available():
            return
        filepath = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if not filepath:
            return
        count, error = import_from_excel(filepath, self.dm)
        if error:
            logger.error("Excel 导入失败: %s - %s", filepath, error)
            messagebox.showerror("导入失败", error)
        else:
            self._refresh_excel_tree()
            self._update_status()
            self._refresh_subject_ui()
            messagebox.showinfo("完成", f"成功导入 {count} 名学生")
            logger.info("Excel 导入成功: %s (%d 条)", filepath, count)

    def _export_excel(self) -> None:
        if not self._check_excel_available():
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], initialfile=get_excel_filename())
        if not filepath:
            return
        if export_to_excel(filepath, self.dm):
            self._show_status("Excel 导出成功", "ok")
            logger.info("Excel 导出成功: %s", filepath)
        else:
            logger.error("Excel 导出失败: %s", filepath)
            messagebox.showerror("错误", "导出失败")

    def _export_csv(self) -> None:
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile=get_csv_filename())
        if not filepath:
            return
        if export_to_csv(filepath, self.dm):
            self._show_status("CSV 导出成功", "ok")
            logger.info("CSV 导出成功: %s", filepath)
        else:
            logger.error("CSV 导出失败: %s", filepath)
            messagebox.showerror("错误", "导出失败")

    # ========== 管理页面方法 ==========

    def _refresh_manage_tree(self) -> None:
        """刷新成绩管理表格，应用班级过滤、成绩范围过滤、排序和颜色预警。"""
        self.mg_tree.delete(*self.mg_tree.get_children())

        # 获取过滤条件
        filter_class = "全部班级"
        if hasattr(self, "mg_filter_class"):
            filter_class = self.mg_filter_class.get()
        filter_score = "全部"
        if hasattr(self, "mg_filter_score"):
            filter_score = self.mg_filter_score.get()

        # 收集数据
        columns = self.mg_tree["columns"]
        subject_count = len(self.dm.subjects)
        rows = []
        for sid, stu in self.dm.students.items():
            # 班级过滤
            if filter_class != "全部班级" and stu.get("class", "") != filter_class:
                continue

            st = self.dm.stats(sid)
            if st is None:
                continue

            vals = [sid, stu["name"], stu.get("class", "")] + \
                   [stu["scores"].get(s, "-") for s in self.dm.subjects] + \
                   [st["total"], st["avg"]]

            # 成绩范围过滤
            if filter_score != "全部":
                score_vals = vals[3:3+subject_count]
                pass_ok = True  # 全部 ≥ 60
                has_60_69 = False
                has_70_89 = False
                all_ge_90 = True
                all_empty = True

                for v in score_vals:
                    if v == "-":
                        continue
                    all_empty = False
                    try:
                        s = float(v)
                        if s < 60:
                            pass_ok = False
                        if 60 <= s < 70:
                            has_60_69 = True
                        if 70 <= s < 90:
                            has_70_89 = True
                        if s < 90:
                            all_ge_90 = False
                    except:
                        pass

                if all_empty:
                    continue
                if filter_score == "不及格 (<60)" and (not pass_ok):  # 任一 < 60
                    pass
                elif filter_score == "及格 (60-69)" and (pass_ok and has_60_69):
                    pass
                elif filter_score == "良好 (70-89)" and (pass_ok and not has_60_69 and has_70_89):
                    pass
                elif filter_score == "优秀 (≥90)" and all_ge_90:
                    pass
                else:
                    continue

            rows.append(vals)

        # 应用排序
        if not hasattr(self, "_mg_sort_col") or not self._mg_sort_col:
            rows.sort(key=lambda r: int(r[0]) if r[0].isdigit() else r[0])
        else:
            col_idx = columns.index(self._mg_sort_col)
            rows.sort(
                key=lambda r: self._mg_sort_key(r, col_idx),
                reverse=not self._mg_sort_asc,
            )

        # 填充数据并应用颜色预警
        for idx, vals in enumerate(rows):
            base_tag = "odd" if idx % 2 == 0 else "even"

            # ====== 计算颜色标签 ======
            score_vals = vals[3:3+subject_count]
            has_fail = False
            has_warn = False
            has_good = True
            all_empty = True

            for v in score_vals:
                if v == "-":
                    continue
                all_empty = False
                try:
                    score = float(v)
                    if score < 60:
                        has_fail = True
                        has_good = False
                    elif score < 70:
                        has_warn = True
                        has_good = False
                    elif score < 90:
                        has_good = False
                except:
                    pass

            row_tag = ""
            if all_empty:
                row_tag = "empty_all"
            elif has_fail:
                row_tag = "fail"
            elif has_warn:
                row_tag = "warn"
            elif has_good:
                row_tag = "good"

            tags = (base_tag,)
            if row_tag:
                tags = (base_tag, row_tag)

            self.mg_tree.insert("", "end", values=vals, tags=tags)

        # 更新状态栏
        total = len(self.dm.students)
        shown = len(rows)
        parts = []
        if filter_class != "全部班级":
            parts.append(filter_class)
        if filter_score != "全部":
            parts.append(filter_score)
        if parts:
            self._show_status(f"{' '.join(parts)}：共 {shown}/{total} 人", "info")
        else:
            self._show_status(f"全部学生共 {total} 人", "info")

    @staticmethod

    def _mg_sort_key(vals: list, col_idx: int) -> float | str:
        """生成排序键值（数字优先，文本兜底）。"""
        v = vals[col_idx]
        if v == "-" or v == "" or v is None:
            return -1
        try:
            return float(v)
        except (ValueError, TypeError):
            return str(v).lower()

    def _manage_sort_tree(self, col: str) -> None:
        """按指定列头排序（切换升降序）。"""
        if self._mg_sort_col == col:
            self._mg_sort_asc = not self._mg_sort_asc
        else:
            self._mg_sort_col = col
            self._mg_sort_asc = True  # 默认降序（高分在前）
        self._refresh_manage_tree()

    def _manage_cell_double_click(self, event: tk.Event) -> None:
        row_id = self.mg_tree.identify_row(event.y)
        col_id = self.mg_tree.identify_column(event.x)
        if not row_id:
            return
        col_index = int(col_id.replace("#", "")) - 1
        columns = self.mg_tree["columns"]
        if col_index == 0:
            return

        vals = self.mg_tree.item(row_id, "values")
        sid = vals[0]

        # 编辑姓名或班级
        if col_index in (1, 2):
            new_val = simpledialog.askstring("修改", f"学号 {sid}\n新值 (留空清除)：", initialvalue=vals[col_index])
            if new_val is None:
                return
            name, cls = vals[1], vals[2]
            if col_index == 1:
                name = new_val
            else:
                cls = new_val
            try:
                self.dm.upd_stu(sid, name, cls)
                self._refresh_manage_tree()
                self._show_status("信息已更新", "ok")
            except Exception as e:
                messagebox.showerror("错误", str(e))
            return

        # 编辑成绩
        if 3 <= col_index < len(columns) - 2:
            subject = columns[col_index]
            x, y, w, h = self.mg_tree.bbox(row_id, col_id)
            entry = tk.Entry(self.mg_tree, font=("微软雅黑", 10), relief="solid")
            entry.insert(0, vals[col_index])
            entry.place(x=x, y=y, width=w, height=h)
            entry.focus_set()

            def _commit_score() -> None:
                v = entry.get().strip()
                entry.destroy()
                try:
                    if v in ("", "-"):
                        self.dm.set_score(sid, subject, None)
                    else:
                        self.dm.set_score(sid, subject, v)
                    self._refresh_manage_tree()
                    self._show_status(f"{subject} 成绩已更新", "ok")
                except Exception as ex:
                    messagebox.showerror("错误", str(ex))

            entry.bind("<Return>", lambda _: _commit_score())
            entry.bind("<Escape>", lambda _: entry.destroy())
            entry.bind("<FocusOut>", lambda _: _commit_score())

    def _manage_edit_selected(self) -> None:
        selected = self.mg_tree.selection()
        if not selected:
            return
        sid = self.mg_tree.item(selected[0], "values")[0]
        stu = self.dm.get_stu(sid)
        if stu is None:
            return
        name = simpledialog.askstring("姓名", "新姓名：", initialvalue=stu["name"])
        if name is None:
            return
        cls = simpledialog.askstring("班级", "新班级：", initialvalue=stu.get("class", ""))
        if cls is None:
            return
        try:
            self.dm.upd_stu(sid, name, cls)
            self._refresh_manage_tree()
            self._show_status("信息已更新", "ok")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _manage_delete_selected(self) -> None:
        selected = self.mg_tree.selection()
        if not selected:
            return
        sid = self.mg_tree.item(selected[0], "values")[0]
        if messagebox.askyesno("确认", f"确定删除学生 {sid} 吗？"):
            self.dm.del_stu(sid)
            self._refresh_manage_tree()
            self._update_status()

    # ========== 查询页面方法 ==========

    def _search_execute(self) -> None:
        keyword = self.se_var.get().strip()
        results = self.dm.search(keyword) if keyword else list(self.dm.students.keys())
        results.sort()
        self.se_list.delete(0, "end")
        for sid in results:
            stu = self.dm.get_stu(sid)
            if stu:
                self.se_list.insert("end", f"{sid} | {stu['name']} | {stu.get('class', '')}")
        if len(results) == 1:
            self.se_list.selection_set(0)
            self._search_show_detail(None)

    def _refresh_search_list(self) -> None:
        self.se_var.set("")
        self._search_execute()

    def _search_show_detail(self, event: tk.Event) -> None:
        selected = self.se_list.curselection()
        if not selected:
            return
        sid = self.se_list.get(selected[0]).split("|")[0].strip()
        stu = self.dm.get_stu(sid)
        if not stu:
            return
        st = self.dm.stats(sid)
        if st is None:
            return

        self.dv["sid"].set(sid)
        self.dv["name"].set(stu["name"])
        self.dv["cls"].set(stu.get("class", ""))
        self.dv["total"].set(str(st["total"]) if st["total"] else "—")
        self.dv["avg"].set(str(st["avg"]) if st["avg"] else "—")

        self.stt.delete(*self.stt.get_children())
        for idx, subject in enumerate(self.dm.subjects):
            score = stu["scores"].get(subject)
            if score is not None:
                tag, level = self._get_level_tag(score)
                base_tag = "odd" if idx % 2 == 0 else "even"
                self.stt.insert("", "end", values=(subject, score, level), tags=(base_tag, tag))

    def _search_show_history(self, student_id: str) -> None:
        if not student_id or student_id == "—":
            messagebox.showinfo("提示", "请先在左侧列表选择一个学生")
            return

        try:
            history = self.dm.get_history(student_id=student_id)
        except Exception as e:
            logger.error("获取历史记录失败: %s", e)
            messagebox.showerror("错误", f"获取历史记录失败: {e}")
            return

        dialog = tk.Toplevel(self.win)
        dialog.title(f"成绩修改历史 - {student_id}")
        dialog.geometry("500x400")
        dialog.grab_set()
        
        tk.Label(dialog, text=f"学生 {student_id} 的成绩修改历史", font=("微软雅黑", 12, "bold")).pack(pady=8)

        if not history:
            tk.Label(dialog, text="暂无修改记录", font=("微软雅黑", 11), fg="#64748B").pack(expand=True)
            ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=8)
            return

        columns = ["时间", "科目", "旧成绩", "新成绩"]
        widths = [140, 100, 80, 80]
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=14)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        tree.tag_configure("even", background="#F8FAFC")
        tree.tag_configure("odd", background="#FFFFFF")

        for i, record in enumerate(history):
            base_tag = "odd" if i % 2 == 0 else "even"
            old_val = record.get("old")
            new_val = record.get("new")
            old_str = str(old_val) if old_val is not None else "—"
            new_str = str(new_val) if new_val is not None else "—"
            tree.insert("", "end", values=(record.get("time", "")[:16], record.get("subject", ""), old_str, new_str), tags=(base_tag,))

        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=8)

    def _search_delete_selected(self) -> None:
        selected = self.se_list.curselection()
        if not selected:
            return
        sid = self.se_list.get(selected[0]).split("|")[0].strip()
        if messagebox.askyesno("确认", f"确定删除 {sid} 吗？"):
            self.dm.del_stu(sid)
            self._refresh_search_list()
            self._show_status(f"已删除 {sid}", "warn")

    # ========== 科目分析页面方法 ==========

    def _analyze_subject(self) -> None:
        subject = self.an_subj.get()
        if not subject:
            messagebox.showwarning("提示", "请先添加科目！")
            return

        analysis = self.dm.analyze_subject(subject)
        if not analysis:
            messagebox.showinfo("提示", "该科目暂无成绩数据")
            return

        self.alab["cnt"].config(text=f"{analysis['count']} 人")
        self.alab["mx"].config(text=str(analysis["max"]), fg="#059669")
        self.alab["mn"].config(text=str(analysis["min"]), fg="#EF4444" if analysis["min"] < 60 else "#1E293B")
        self.alab["av"].config(text=str(analysis["avg"]))
        self.alab["ps"].config(text=f"{analysis['pass_rate']}%", fg="#059669" if analysis["pass_rate"] >= 60 else "#EF4444")
        self.alab["ex"].config(text=f"{analysis['excellent_rate']}%")

        self.adist.delete(*self.adist.get_children())
        for seg in ["0-59", "60-69", "70-79", "80-89", "90-100"]:
            count = analysis["distribution"].get(seg, 0)
            pct = f"{round(count / analysis['count'] * 100, 1)}%" if analysis["count"] else "0%"
            self.adist.insert("", "end", values=(seg, count, pct), tags=(seg,))

        self.adt.delete(*self.adt.get_children())
        rows = []
        for sid, stu in self.dm.students.items():
            score = stu["scores"].get(subject)
            if score is not None:
                rows.append((sid, stu["name"], stu.get("class", ""), score))
        rows.sort(key=lambda x: x[3], reverse=True)

        for rank, (sid, name, cls, score) in enumerate(rows, 1):
            tag, level = self._get_level_tag(score)
            self.adt.insert("", "end", values=(rank, sid, name, cls, score, level), tags=(tag,))

    def _manage_subjects(self) -> None:
        dialog = tk.Toplevel(self.win)
        dialog.title("科目管理")
        dialog.geometry("300x300")
        dialog.grab_set()

        listbox = tk.Listbox(dialog)
        listbox.pack(fill="both", expand=True)
        for s in self.dm.subjects:
            listbox.insert("end", s)

        def _add() -> None:
            name = simpledialog.askstring("添加", "请输入科目名称：", parent=dialog)
            if name:
                try:
                    self.dm.add_subject(name)
                    listbox.insert("end", name)
                    self._refresh_subject_ui()
                except Exception as e:
                    messagebox.showerror("错误", str(e))

        def _delete() -> None:
            selected = listbox.curselection()
            if not selected:
                return
            name = listbox.get(selected[0])
            try:
                self.dm.delete_subject(name)
                listbox.delete(selected[0])
                self._refresh_subject_ui()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        btn_frame = tk.Frame(dialog)
        btn_frame.pack()
        ttk.Button(btn_frame, text="➕ 添加", command=_add).pack(side="left")
        ttk.Button(btn_frame, text="🗑️ 删除", command=_delete).pack(side="left")
        ttk.Button(btn_frame, text="关闭", command=dialog.destroy).pack(side="left")

    def _refresh_subject_ui(self) -> None:
        subjects = self.dm.subjects
        if hasattr(self, "an_cb"):
            self.an_cb["values"] = subjects
        if hasattr(self, "ch_cb"):
            self.ch_cb["values"] = subjects
        if hasattr(self, "mg_tree"):
            self._refresh_manage_tree()
            widths = self._calc_subject_widths(subjects)
            cols = self.mg_tree["columns"]
            for i, w in enumerate(widths, start=3):
                if i < len(cols):
                    self.mg_tree.column(cols[i], width=w, minwidth=50)
            # 更新列头排序绑定
            for col in cols:
                self.mg_tree.heading(col, command=lambda c=col: self._manage_sort_tree(c))
        if hasattr(self, "mg_class_cb"):
            self.mg_class_cb["values"] = ["全部班级"] + self.dm.classes
        if hasattr(self, "ex_tree"):
            self._refresh_excel_tree()
            widths = self._calc_subject_widths(subjects)
            cols = self.ex_tree["columns"]
            for i, w in enumerate(widths, start=3):
                if i < len(cols) - 2:
                    self.ex_tree.column(cols[i], width=w, minwidth=50)

    # ========== 图表页面方法 ==========

    def _clear_chart_area(self) -> None:
        for w in self.ct.winfo_children():
            w.destroy()

    def _show_chart(self, figure: Figure) -> None:
        self._clear_chart_area()
        canvas = FigureCanvasTkAgg(figure, self.ct)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(figure)

    def _chart_total_ranking(self) -> None:
        ranking = self.dm.ranking()
        if not ranking:
            messagebox.showinfo("提示", "暂无学生数据")
            return
        fig = Figure(figsize=(max(7, len(ranking) * 0.6), 4))
        ax = fig.add_subplot(111)
        bar_colors = ["#FCD34D" if x["rank"] == 1 else "#F97316" if x["rank"] == 3 else "#3B82F6" for x in ranking]
        ax.bar([x["name"] for x in ranking], [x["total"] for x in ranking], color=bar_colors)
        ax.set_title("总分排名")
        fig.tight_layout()
        self._show_chart(fig)

    def _chart_avg_comparison(self) -> None:
        ranking = self.dm.ranking(by="avg")
        if not ranking:
            messagebox.showinfo("提示", "暂无学生数据")
            return
        fig = Figure(figsize=(max(7, len(ranking) * 0.6), 4))
        ax = fig.add_subplot(111)
        avgs = [x["avg"] for x in ranking]
        bar_colors = ["#10B981" if v >= 90 else "#3B82F6" if v >= 75 else "#F59E0B" if v >= 60 else "#EF4444" for v in avgs]
        ax.bar([x["name"] for x in ranking], avgs, color=bar_colors)
        ax.axhline(60, color="red", ls="--")
        ax.axhline(90, color="green", ls="--")
        ax.set_title("平均分对比")
        ax.set_ylim(0, 105)
        fig.tight_layout()
        self._show_chart(fig)

    def _chart_histogram(self) -> None:
        subject = self.ch_subj.get()
        if not subject:
            messagebox.showwarning("提示", "请先添加科目！")
            return
        analysis = self.dm.analyze_subject(subject)
        if not analysis:
            messagebox.showinfo("提示", "该科目暂无成绩数据")
            return
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.hist(analysis["scores"], bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], color="#3B82F6")
        ax.axvline(analysis["avg"], color="red", ls="--", label=f"均分 {analysis['avg']}")
        ax.axvline(60, color="orange", ls=":", label="及格线")
        ax.set_title(f"{subject} 成绩分布")
        ax.legend()
        self._show_chart(fig)

    def _chart_radar(self) -> None:
        if len(self.dm.subjects) < 3:
            messagebox.showinfo("提示", "至少需要 3 个科目才能生成雷达图")
            return
        avgs = [self.dm.analyze_subject(s)["avg"] if self.dm.analyze_subject(s) else 0 for s in self.dm.subjects]
        n = len(self.dm.subjects)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles + angles[:1], avgs + avgs[:1], "o-")
        ax.fill(angles + angles[:1], avgs + avgs[:1], alpha=0.25)
        ax.set_xticks(angles)
        ax.set_xticklabels(self.dm.subjects, fontsize=8)
        ax.set_ylim(0, 100)
        self._show_chart(fig)

    def _chart_boxplot(self) -> None:
        if not self.dm.subjects:
            messagebox.showinfo("提示", "暂无科目数据")
            return
        data = []
        labels = []
        for s in self.dm.subjects:
            analysis = self.dm.analyze_subject(s)
            if analysis and analysis["scores"]:
                data.append(analysis["scores"])
                labels.append(s)
        if not data:
            messagebox.showinfo("提示", "无有效数据")
            return
        fig = Figure(figsize=(max(6, len(self.dm.subjects) * 1.2), 4))
        ax = fig.add_subplot(111)
        bp = ax.boxplot(data, patch_artist=True)
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels)
        box_colors = ["#6366F1", "#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
        for patch, color in zip(bp["boxes"], box_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        ax.set_ylim(0, 105)
        ax.axhline(60, color="red", ls="--", alpha=0.5)
        ax.set_title("各科目成绩箱线图")
        fig.tight_layout()
        self._show_chart(fig)

    # ========== 班级管理页面方法 ==========

    def _class_add(self) -> None:
        name = simpledialog.askstring("添加班级", "请输入班级名称：")
        if not name:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("提示", "班级名称不能为空")
            return
        try:
            existing = [s for s in self.dm.data["students"].values() if s.get("class") == name]
            if existing:
                if not messagebox.askyesno("提示", f"班级「{name}」已存在，是否查看？"):
                    return
                self._class_show_detail(name)
                return
            for sid, s in self.dm.data["students"].items():
                if not s.get("class"):
                    s["class"] = name
            self.dm.save()
            messagebox.showinfo("成功", f"已创建班级「{name}」")
            self._refresh_class_tree()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _refresh_class_tree(self) -> None:
        """刷新班级列表表格数据。"""
        # 清空现有数据，不要重新创建表格
        if self.cl_tree:
            self.cl_tree.delete(*self.cl_tree.get_children())
        else:
            return  # 表格还没创建，直接返回

        classes = self.dm.classes
        if not classes:
            tk.Label(self.content_area, text="暂无班级，请先在录入页面为学生设置班级", font=("微软雅黑", 11), bg="white", fg="#64748B").pack(pady=40)
            return

        # 插入数据
        for idx, cls_name in enumerate(classes):
            stats = self.dm.get_class_stats(cls_name)
            if stats:
                base_tag = "odd" if idx % 2 == 0 else "even"
                self.cl_tree.insert("", "end", values=(
                    cls_name,
                    stats["count"],
                    stats["total_avg"],
                    stats["max_total"],
                    stats["min_total"],
                    "查看详情"
                ), tags=(base_tag,))

    def _class_double_click(self, event: tk.Event) -> None:
        row_id = self.cl_tree.identify_row(event.y)
        col_id = self.cl_tree.identify_column(event.x)
        if not row_id:
            return
        if int(col_id.replace("#", "")) == 6:
            vals = self.cl_tree.item(row_id, "values")
            self._class_show_detail(vals[0])

    def _class_show_detail(self, class_name: str) -> None:
        stats = self.dm.get_class_stats(class_name)
        if not stats:
            return
        dialog = tk.Toplevel(self.win)
        dialog.title(f"班级详情 - {class_name}")
        dialog.geometry("700x500")
        tk.Label(dialog, text=f"🏫 {class_name}", font=("微软雅黑", 14, "bold")).pack(pady=8)
        info_frame = tk.Frame(dialog, bg="#F0F9FF", bd=1, relief="solid")
        info_frame.pack(fill="x", padx=10, pady=5)
        info_items = [("班级人数", f"{stats['count']} 人"), ("班级平均分", f"{stats['total_avg']:.1f} 分"), ("最高总分", f"{stats['max_total']:.1f} 分"), ("最低总分", f"{stats['min_total']:.1f} 分")]
        for label, value in info_items:
            tk.Label(info_frame, text=f"{label}：{value}", font=("微软雅黑", 10), bg="#F0F9FF").pack(side="left", padx=15, pady=8)
        columns = ["排名", "学号", "姓名", "总分", "平均分"]
        widths = [60, 120, 100, 100, 100]
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=15)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        tree.tag_configure("even", background="#F8FAFC")
        tree.tag_configure("odd", background="#FFFFFF")
        tree.tag_configure("fail", foreground="#EF4444")
        for idx, student in enumerate(stats["students"]):
            base_tag = "odd" if idx % 2 == 0 else "even"
            fail_tag = "fail" if student["avg"] < 60 else ""
            tags = (base_tag,)
            if fail_tag:
                tags = (base_tag, fail_tag)
            tree.insert("", "end", values=(student["rank"], student["sid"], student["name"], student["total"], student["avg"]), tags=tags)

    # ========== 仪表盘刷新方法 ==========

    def _refresh_dashboard(self) -> None:
        # 更新卡片数值
        if hasattr(self, "da_cards"):
            self.da_cards["students"].config(text=str(len(self.dm.students)))
            self.da_cards["subjects"].config(text=str(len(self.dm.subjects)))
            classes = self.dm.classes
            self.da_cards["classes"].config(text=str(len(classes)))
            warnings = self.dm.get_warnings()
            self.da_cards["warnings"].config(text=str(len(warnings)))

        # 刷新图表
        if hasattr(self, "da_subj_frame"):
            for w in self.da_subj_frame.winfo_children():
                w.destroy()
            if MAT_OK and self.dm.subjects:
                try:
                    avgs = [self.dm.analyze_subject(s)["avg"] if self.dm.analyze_subject(s) else 0 for s in self.dm.subjects]
                    fig = Figure(figsize=(6, 3.5))
                    ax = fig.add_subplot(111)
                    bar_colors = ["#6366F1", "#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EF4444"][:len(avgs)]
                    bars = ax.bar(self.dm.subjects, avgs, color=bar_colors, width=0.6)
                    for bar, val in zip(bars, avgs):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.5, f"{val:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
                    ax.set_ylim(0, 105)
                    ax.axhline(60, color="#EF4444", ls="--", alpha=0.7, label="及格线")
                    ax.set_title("科目均分对比", fontsize=12, fontweight="bold", pad=10)
                    ax.legend(fontsize=8)
                    fig.tight_layout(pad=1.0)
                    canvas = FigureCanvasTkAgg(fig, self.da_subj_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
                except Exception as e:
                    logger.error("刷新仪表盘图表失败: %s", e)
                    tk.Label(self.da_subj_frame, text=f"图表加载失败: {e}", bg="white").pack()
            else:
                tk.Label(self.da_subj_frame, text="暂无数据", bg="white").pack()

        # 刷新预警列表
        if hasattr(self, "da_warn_frame"):
            for w in self.da_warn_frame.winfo_children():
                w.destroy()
            warnings = self.dm.get_warnings()
            if warnings:
                for w in warnings[:10]:
                    fails = ", ".join([f"{s}:{sc}" for s, sc in w.get("fails", [])])
                    tk.Label(self.da_warn_frame, text=f"⚠️ {w.get('name', '?')}({w.get('sid', '?')}) | {w.get('class', '')} | {fails}", bg="white", anchor="w").pack(fill="x", padx=5, pady=2)
            else:
                tk.Label(self.da_warn_frame, text="✓ 暂无成绩预警", bg="white").pack()

