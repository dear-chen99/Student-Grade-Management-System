"""
学生成绩管理系统 - Student Grade Management System.

主程序入口，提供成绩录入、统计排名、科目分析、图表展示、数据导出等功能。
使用 ttkbootstrap 美化界面，青绿色主题。
"""

import datetime
import logging
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

# --- 第三方库 ---
from ttkbootstrap import Window, Style

# 导入自定义模块
from modules.data_manager import (
    DataManager,
    DataSaveError,
    DataLoadError,
)
from src.config import (
    COLORS,
    WINDOW_CONFIG,
    CHART_CONFIG,
    UI_COLORS,
    FONTS,
    DIALOG_SIZES,
)
from src.utils.excel_handler import (
    is_excel_available,
    create_template,
    import_from_excel,
    export_to_excel,
    get_default_filename as get_excel_filename,
)
from src.utils.export import export_to_csv, get_default_filename as get_csv_filename
from src.utils.avatar_utils import load_avatar, change_avatar
from src.utils.base_app import (
    BaseApp,
    logger,
    TEAL_COLOR,
    TEAL_DARK,
    TEAL_LIGHT,
    EX_OK,
    MAT_OK,
    Figure,
    FigureCanvasTkAgg,
)
from src.utils.ui_utils import (
    create_dialog,
    show_info,
    show_warning,
    show_error,
    confirm,
    validate_password,
)

# 设置项目基础路径
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


class App(BaseApp):
    """学生成绩管理系统主应用程序类."""

    def __init__(
        self,
        data_manager: DataManager | None = None,
        user_info: dict | None = None,
    ) -> None:
        """初始化应用程序，创建窗口、样式和 UI 布局.

        Args:
            data_manager: 外部传入的数据管理器实例，为 None 时自动创建。
            user_info: 当前登录用户信息字典。
        """
        dm = data_manager
        if dm is None:
            try:
                dm = DataManager()
                logger.info("数据管理器初始化成功")
            except DataLoadError as e:
                logger.error("数据管理器初始化失败: %s", e)
                show_error(
                    "数据错误",
                    f"无法加载数据文件，系统将使用空数据启动。\n\n错误详情: {e}",
                )
                dm = DataManager()
        super().__init__(data_manager=dm, user_info=user_info)

        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "img", "app_icon.ico"
        )
        if os.path.exists(icon_path):
            self.win.iconbitmap(icon_path)

        # App 特有的 Treeview 样式覆盖
        style = Style("cosmo")
        style.configure(
            "Treeview",
            font=FONTS["large"],
            rowheight=40,
            padding=(12, 6),
            background="white",
            fieldbackground="white",
        )
        style.configure(
            "Treeview.Heading",
            font=("微软雅黑", 13, "bold"),
            padding=(10, 8),
            background=UI_COLORS["heading_bg"],
            foreground=UI_COLORS["sidebar_bg"],
        )

        # 页面映射
        self.page_builders = {
            "📊 仪表盘": self._build_dashboard_page,
            "📝 录入": self._build_input_page,
            "📥 导入与导出": self._build_excel_page,
            "🏫 班级": self._build_class_page,
            "📁 管理": self._build_manage_page,
            "📊 分析": self._build_analysis_page,
            "👤 账号管理": self._build_account_page,
            "📚 课程管理": self._build_course_mgmt_page,
            "📢 通知管理": self._build_notice_mgmt_page,
            "📅 课表管理": self._build_schedule_mgmt_page,
            "个人中心": self._build_profile_page,
            "⚙️ 系统设置": self._build_settings_page,
        }

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
        logger.info("应用程序初始化完成")

    def _get_window_title(self) -> str:
        """返回主窗口标题."""
        return WINDOW_CONFIG["title"]

    def _get_header_title(self) -> str:
        """返回顶部横幅标题文本."""
        return "🎓 学生成绩管理系统"

    def _get_user_display_name(self) -> str:
        """返回右上角显示的用户名称."""
        return self.user_info.get("username", "管理员")

    def _get_avatar_data(self) -> dict:
        """返回管理员头像数据."""
        admin = self.dm.get_admin() or {}
        return {
            "name": admin.get("name", "管理员"),
            "avatar": admin.get("avatar", ""),
        }

    def _save_avatar(self, path: str) -> None:
        """保存管理员头像路径."""
        self.dm.update_admin_profile(avatar=path)

    # ----- 个人中心钩子实现 -----

    def _get_profile_page_title(self) -> str:
        return "个人中心"

    def _get_avatar_label_text(self) -> str:
        return "管理员头像"

    def _get_profile_id_label(self) -> str:
        return "管理员账号"

    def _get_profile_id_value(self) -> str:
        return self.dm.get_admin().get("username", "admin")

    def _get_profile_pwd_label(self) -> str:
        return "管理员密码"

    def _get_profile_name_label(self) -> str:
        return "管理员名称"

    def _get_profile_name_value(self) -> str:
        return self.dm.get_admin().get("name", "管理员")

    def _get_profile_data(self) -> dict:
        admin = self.dm.get_admin() or {}
        return {
            "password": admin.get("password", ""),
            "phone": admin.get("phone", ""),
            "email": admin.get("email", ""),
        }

    def _save_profile_entity(
        self, name: str, phone: str, email: str, password: str
    ) -> None:
        admin = self.dm.get_admin()
        self.dm.update_admin_profile(
            name=name,
            phone=phone,
            email=email,
            password=password,
            avatar=admin.get("avatar", ""),
        )

    def _get_current_password(self) -> str:
        admin = self.dm.get_admin()
        return admin.get("password", "")

    def _update_password(self, new_password: str) -> None:
        self.dm.update_admin_password(new_password)

    # ========== 仪表盘页面（卡片风格） ==========

    def _build_dashboard_page(self, parent: tk.Frame) -> None:
        """构建仪表盘页面，包含统计卡片、科目均分图和成绩预警列表.

        Args:
            parent: 父容器 Frame，用于放置仪表盘内容。
        """
        # 顶部欢迎横幅
        banner = tk.Frame(parent, bg=TEAL_COLOR, height=80)
        banner.pack(fill="x")
        user_name = self.user_info.get("username", "admin")
        label = tk.Label(
            banner,
            text=f"👋 欢迎回来，{user_name}",
            font=("微软雅黑", 18, "bold"),
            fg="white",
            bg=TEAL_COLOR,
        )
        label.pack(pady=(12, 2))
        date_text = (
            f"当前角色：管理员 | {datetime.datetime.now().strftime('%Y年%m月%d日')}"
        )
        tk.Label(
            banner, text=date_text, font=FONTS["caption"], fg="#e0f2f1", bg=TEAL_COLOR
        ).pack()

        # 统计卡片行
        card_row = tk.Frame(parent, bg="white")
        card_row.pack(fill="x", pady=10)

        self.da_cards = {}  # 存储卡片数值标签，便于刷新

        self.da_cards["students"] = self._create_dashboard_card(
            card_row, "👥", "学生总数", len(self.dm.students), TEAL_COLOR
        )
        self.da_cards["subjects"] = self._create_dashboard_card(
            card_row, "📚", "科目数量", len(self.dm.subjects), "#8B5CF6"
        )
        self.da_cards["classes"] = self._create_dashboard_card(
            card_row, "🏫", "班级数量", len(self.dm.classes), UI_COLORS["success"]
        )
        self.da_cards["warnings"] = self._create_dashboard_card(
            card_row, "⚠️", "预警人数", len(self.dm.get_warnings()), UI_COLORS["danger"]
        )

        # 第二行统计卡片
        card_row2 = tk.Frame(parent, bg="white")
        card_row2.pack(fill="x", pady=(0, 10))
        self.da_cards["teachers"] = self._create_dashboard_card(
            card_row2, "👨‍🏫", "教师总数", len(self.dm.teachers), "#3B82F6"
        )
        self.da_cards["courses"] = self._create_dashboard_card(
            card_row2, "📖", "课程总数", len(self.dm.courses), UI_COLORS["warning"]
        )

        # 下边区域：左侧图表 + 右侧预警列表
        chart_row = tk.Frame(parent, bg="white")
        chart_row.pack(fill="both", expand=True, pady=10)

        # 左：科目均分图
        left_chart = tk.Frame(chart_row, bg="white", bd=1, relief="solid")
        left_chart.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(
            left_chart,
            text="📈 各科目平均分",
            font=FONTS["body_bold"],
            bg="white",
        ).pack(pady=5)
        self.da_subj_frame = tk.Frame(left_chart, bg="white")
        self.da_subj_frame.pack(fill="both", expand=True, padx=8, pady=(0, 5))

        # 右：预警列表
        right_list = tk.Frame(chart_row, bg="white", bd=1, relief="solid")
        right_list.pack(side="right", fill="both", expand=True, padx=5)
        warning_label = tk.Label(
            right_list,
            text="⚠️ 成绩预警",
            font=FONTS["body_bold"],
            bg="white",
        )
        warning_label.pack(pady=5)
        self.da_warn_frame = tk.Frame(right_list, bg="white")
        self.da_warn_frame.pack(fill="both", expand=True, padx=8, pady=(0, 5))

        # 最近修改记录
        hist_frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
        hist_frame.pack(fill="x", pady=10, padx=5)
        tk.Label(
            hist_frame,
            text="🕒 最近修改记录",
            font=FONTS["body_bold"],
            bg="white",
        ).pack(pady=5, anchor="w", padx=10)
        self.da_hist_frame = tk.Frame(hist_frame, bg="white")
        self.da_hist_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        """刷新仪表盘页面数据，更新统计卡片、科目均分图和成绩预警列表."""
        if hasattr(self, "da_cards"):
            self.da_cards["students"].config(text=str(len(self.dm.students)))
            self.da_cards["subjects"].config(text=str(len(self.dm.subjects)))
            classes = self.dm.classes
            self.da_cards["classes"].config(text=str(len(classes)))
            warnings = self.dm.get_warnings()
            self.da_cards["warnings"].config(text=str(len(warnings)))
            self.da_cards["teachers"].config(text=str(len(self.dm.teachers)))
            self.da_cards["courses"].config(text=str(len(self.dm.courses)))

        # 刷新图表
        if hasattr(self, "da_subj_frame"):
            for w in self.da_subj_frame.winfo_children():
                w.destroy()
            if MAT_OK and self.dm.subjects:
                try:
                    # 计算每个科目的平均分，缺失分析结果时默认 0
                    avgs = [
                        (
                            self.dm.analyze_subject(s)["avg"]
                            if self.dm.analyze_subject(s)
                            else 0
                        )
                        for s in self.dm.subjects
                    ]
                    fig = Figure(figsize=(6, 3.5))
                    ax = fig.add_subplot(111)
                    # 为柱状条分配颜色，循环使用预设色板
                    bar_colors = [
                        "#6366F1",
                        "#8B5CF6",
                        "#3B82F6",
                        UI_COLORS["success"],
                        UI_COLORS["warning"],
                        UI_COLORS["danger"],
                    ][: len(avgs)]
                    bars = ax.bar(self.dm.subjects, avgs, color=bar_colors, width=0.6)
                    # 在柱顶标注具体均分值
                    for bar, val in zip(bars, avgs):
                        ax.text(
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.5,
                            f"{val:.1f}",
                            ha="center",
                            va="bottom",
                            fontsize=9,
                            fontweight="bold",
                        )
                    ax.set_ylim(0, 105)
                    # 绘制 60 分及格参考线
                    ax.axhline(60, color=UI_COLORS["danger"], ls="--", alpha=0.7, label="及格线")
                    ax.set_title(
                        "科目均分对比",
                        fontsize=12,
                        fontweight="bold",
                        pad=10,
                    )
                    ax.legend(fontsize=8)
                    fig.tight_layout(pad=1.0)
                    canvas = FigureCanvasTkAgg(fig, self.da_subj_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
                except Exception as e:
                    logger.error("刷新仪表盘图表失败: %s", e)
                    tk.Label(
                        self.da_subj_frame,
                        text=f"图表加载失败: {e}",
                        bg="white",
                    ).pack()
            else:
                tk.Label(self.da_subj_frame, text="暂无数据", bg="white").pack()

        # 刷新预警列表
        if hasattr(self, "da_warn_frame"):
            for w in self.da_warn_frame.winfo_children():
                w.destroy()
            warnings = self.dm.get_warnings()
            if warnings:
                # 仅展示前 10 条预警，避免界面过长
                for w in warnings[:10]:
                    fails = ", ".join([f"{s}:{sc}" for s, sc in w.get("fails", [])])
                    name = w.get("name", "?")
                    sid = w.get("sid", "?")
                    class_name = w.get("class", "")
                    text = f"⚠️ {name}({sid}) | {class_name} | {fails}"
                    tk.Label(
                        self.da_warn_frame, text=text, bg="white", anchor="w"
                    ).pack(fill="x", padx=5, pady=2)
            else:
                tk.Label(self.da_warn_frame, text="✓ 暂无成绩预警", bg="white").pack()

        # 刷新最近修改记录
        if hasattr(self, "da_hist_frame"):
            for w in self.da_hist_frame.winfo_children():
                w.destroy()
            # 取最近 5 条历史记录并按时间倒序展示
            history = self.dm.get_history()[-5:]
            if history:
                for record in reversed(history):
                    text = (
                        f"{record.get('time', '')} | "
                        f"学号 {record.get('sid', '')} | "
                        f"{record.get('subject', '')}: "
                        f"{record.get('old', '')} → {record.get('new', '')}"
                    )
                    tk.Label(
                        self.da_hist_frame,
                        text=text,
                        font=FONTS["caption"],
                        bg="white",
                        anchor="w",
                    ).pack(fill="x", pady=2)
            else:
                tk.Label(
                    self.da_hist_frame,
                    text="暂无修改记录",
                    font=FONTS["caption"],
                    bg="white",
                    fg=UI_COLORS["placeholder"],
                ).pack(pady=10)

    # ========== 账号管理页面 ==========
    def _build_account_page(self, parent: tk.Frame) -> None:
        """构建账号管理页面."""
        # 标题
        tk.Label(
            parent,
            text="👤 账号管理",
            font=FONTS["title"],
            fg=UI_COLORS["sidebar_bg"],
            bg="white",
        ).pack(pady=4)

        # 角色切换按钮
        tab_frame = tk.Frame(parent, bg="white")
        tab_frame.pack(pady=5)
        self.acc_tab = "teacher"
        self.btn_tab_teacher = tk.Label(
            tab_frame,
            text="教师账号",
            font=FONTS["body_bold"],
            bg=UI_COLORS["heading_bg"],
            fg=UI_COLORS["sidebar_bg"],
            cursor="hand2",
            padx=15,
            pady=5,
        )
        self.btn_tab_teacher.pack(side="left", padx=5)
        self.btn_tab_teacher.bind(
            "<Button-1>", lambda e: self._switch_account_tab("teacher")
        )
        self.btn_tab_student = tk.Label(
            tab_frame,
            text="学生账号",
            font=FONTS["body"],
            bg="white",
            fg=UI_COLORS["sidebar_inactive_fg"],
            cursor="hand2",
            padx=15,
            pady=5,
        )
        self.btn_tab_student.pack(side="left", padx=5)
        self.btn_tab_student.bind(
            "<Button-1>", lambda e: self._switch_account_tab("student")
        )

        # 操作按钮
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=5)
        ttk.Button(
            btn_frame,
            text="➕ 添加账号",
            style="success.TButton",
            command=self._account_add,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="🔄 刷新",
            style="primary.TButton",
            command=self._refresh_account_tree,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="🗑️ 删除选中",
            style="danger.TButton",
            command=self._account_delete_selected,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="🔑 重置密码",
            style="warning.TButton",
            command=self._account_reset_password,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="✏️ 编辑选中",
            style="info.TButton",
            command=self._account_edit,
        ).pack(side="left", padx=4)

        # 表格容器
        self.acc_tree_frame = tk.Frame(parent, bg="white")
        self.acc_tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._switch_account_tab("teacher")

    def _switch_account_tab(self, tab: str) -> None:
        """切换账号管理标签页."""
        self.acc_tab = tab
        if tab == "teacher":
            self.btn_tab_teacher.configure(
                font=FONTS["body_bold"], bg=UI_COLORS["heading_bg"], fg=UI_COLORS["sidebar_bg"]
            )
            self.btn_tab_student.configure(
                font=FONTS["body"], bg="white", fg=UI_COLORS["sidebar_inactive_fg"]
            )
        else:
            self.btn_tab_student.configure(
                font=FONTS["body_bold"], bg=UI_COLORS["heading_bg"], fg=UI_COLORS["sidebar_bg"]
            )
            self.btn_tab_teacher.configure(
                font=FONTS["body"], bg="white", fg=UI_COLORS["sidebar_inactive_fg"]
            )
        self._refresh_account_tree()

    def _refresh_account_tree(self) -> None:
        """刷新账号管理表格."""
        # 清空旧表格，避免重复渲染
        for w in self.acc_tree_frame.winfo_children():
            w.destroy()

        if self.acc_tab == "teacher":
            # 教师账号列：工号、姓名、授课数量、操作
            columns = ["工号", "姓名", "授课数量", "操作"]
            widths = [120, 120, 100, 150]
            tree = ttk.Treeview(
                self.acc_tree_frame,
                columns=columns,
                show="headings",
                height=20,
            )
            for col, width in zip(columns, widths):
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")
            tree.pack(fill="both", expand=True)
            self._apply_zebra_stripes(tree)
            # 遍历教师数据并插入表格，应用斑马纹
            for idx, (tid, tinfo) in enumerate(self.dm.teachers.items()):
                tag = "odd" if idx % 2 == 0 else "even"
                course_count = len(tinfo.get("course_ids", []))
                tree.insert(
                    "",
                    "end",
                    values=(tid, tinfo["name"], course_count, ""),
                    tags=(tag,),
                )
            self.acc_tree = tree
        else:
            # 学生账号列：学号、姓名、班级、操作
            columns = ["学号", "姓名", "班级", "操作"]
            widths = [120, 120, 120, 150]
            tree = ttk.Treeview(
                self.acc_tree_frame,
                columns=columns,
                show="headings",
                height=20,
            )
            for col, width in zip(columns, widths):
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")
            tree.pack(fill="both", expand=True)
            self._apply_zebra_stripes(tree)
            # 遍历学生数据并插入表格
            for idx, (sid, sinfo) in enumerate(self.dm.students.items()):
                tag = "odd" if idx % 2 == 0 else "even"
                tree.insert(
                    "",
                    "end",
                    values=(
                        sid,
                        sinfo["name"],
                        sinfo.get("class", ""),
                        "",
                    ),
                    tags=(tag,),
                )
            self.acc_tree = tree

    def _account_add(self) -> None:
        """打开添加账号对话框."""
        dialog = tk.Toplevel(self.win)
        dialog.title("添加账号")
        dialog.transient(self.win)
        dialog.grab_set()
        dialog.resizable(False, False)

        dialog.geometry("350x200")
        self._position_dialog(dialog)

        tk.Label(dialog, text="账号：", font=FONTS["body"]).pack(pady=(15, 2))
        id_var = tk.StringVar()
        tk.Entry(dialog, textvariable=id_var, font=FONTS["body"]).pack()

        tk.Label(dialog, text="姓名：", font=FONTS["body"]).pack(pady=(10, 2))
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, font=FONTS["body"]).pack()

        def do_add():
            account_id = id_var.get().strip()
            name = name_var.get().strip()
            if not account_id or not name:
                show_warning("提示", "账号和姓名不能为空")
                return
            try:
                if self.acc_tab == "teacher":
                    self.dm.add_teacher(account_id, name)
                else:
                    class_name = ""
                    self.dm.add_student(account_id, name, class_name)
                show_info("成功", "账号添加成功")
                dialog.destroy()
                self._refresh_account_tree()
            except Exception as e:
                show_error("错误", str(e))

        ttk.Button(
            dialog, text="确认添加", style="primary.TButton", command=do_add
        ).pack(pady=15)

    def _account_delete_selected(self) -> None:
        """删除选中的账号."""
        selected = self.acc_tree.selection()
        if not selected:
            show_warning("提示", "请先选中一个账号")
            return
        vals = self.acc_tree.item(selected[0], "values")
        if not vals or not vals[0]:
            return
        account_id = vals[0]
        role_text = "教师" if self.acc_tab == "teacher" else "学生"
        if not confirm(
            "确认删除", f"确定要删除{role_text}「{account_id}」吗？"
        ):
            return
        try:
            if self.acc_tab == "teacher":
                self.dm.delete_teacher(account_id)
            else:
                self.dm.delete_student(account_id)
            show_info("成功", f"{role_text}账号已删除")
            self._refresh_account_tree()
        except Exception as e:
            show_error("错误", str(e))

    def _account_reset_password(self) -> None:
        """重置选中账号的密码."""
        selected = self.acc_tree.selection()
        if not selected:
            show_warning("提示", "请先选中一个账号")
            return
        vals = self.acc_tree.item(selected[0], "values")
        if not vals or not vals[0]:
            return
        account_id = vals[0]
        role_text = "教师" if self.acc_tab == "teacher" else "学生"
        if not confirm(
            "确认重置",
            f"确定要重置{role_text}「{account_id}」的密码为默认值吗？",
        ):
            return
        try:
            if self.acc_tab == "teacher":
                default_pw = self.dm.reset_teacher_password(account_id)
            else:
                default_pw = self.dm.reset_student_password(account_id)
            show_info(
                "成功",
                f"{role_text}「{account_id}」密码已重置为：{default_pw}",
            )
        except Exception as e:
            show_error("错误", str(e))

    def _account_edit(self) -> None:
        """编辑选中账号信息."""
        selected = self.acc_tree.selection()
        if not selected:
            show_warning("提示", "请先选中一个账号")
            return
        vals = self.acc_tree.item(selected[0], "values")
        if not vals or not vals[0]:
            return
        account_id = vals[0]
        role_text = "教师" if self.acc_tab == "teacher" else "学生"

        dialog = tk.Toplevel(self.win)
        dialog.title(f"编辑{role_text}信息")
        dialog.transient(self.win)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.geometry("350x250")
        self._position_dialog(dialog)

        tk.Label(dialog, text="姓名：", font=FONTS["body"]).pack(pady=(15, 2))
        name_var = tk.StringVar(value=vals[1] if len(vals) > 1 else "")
        tk.Entry(dialog, textvariable=name_var, font=FONTS["body"]).pack()

        class_var = tk.StringVar()
        if self.acc_tab == "student":
            tk.Label(dialog, text="班级：", font=FONTS["body"]).pack(pady=(10, 2))
            class_var.set(vals[2] if len(vals) > 2 else "")
            tk.Entry(dialog, textvariable=class_var, font=FONTS["body"]).pack()

        def do_save():
            name = name_var.get().strip()
            if not name:
                show_warning("提示", "姓名不能为空")
                return
            try:
                if self.acc_tab == "teacher":
                    self.dm.update_teacher(account_id, name=name)
                else:
                    self.dm.update_student(
                        account_id, name=name, class_name=class_var.get().strip()
                    )
                show_info("成功", f"{role_text}信息已更新")
                dialog.destroy()
                self._refresh_account_tree()
            except Exception as e:
                show_error("错误", str(e))

        ttk.Button(dialog, text="保存", style="primary.TButton", command=do_save).pack(
            pady=15
        )

    def _build_course_mgmt_page(self, parent: tk.Frame) -> None:
        """构建课程管理页面."""
        tk.Label(
            parent,
            text="📚 课程管理",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=5)
        ttk.Button(
            btn_frame,
            text="➕ 添加课程",
            style="success.TButton",
            command=self._course_add,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="🔄 刷新",
            style="primary.TButton",
            command=self._refresh_course_tree,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="🗑️ 删除选中",
            style="danger.TButton",
            command=self._course_delete_selected,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="✏️ 编辑选中",
            style="info.TButton",
            command=self._course_edit,
        ).pack(side="left", padx=4)

        columns = ["课程编号", "课程名称", "授课教师", "开课班级"]
        widths = [120, 180, 120, 120]
        self.co_tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)
        for col, width in zip(columns, widths):
            self.co_tree.heading(col, text=col)
            self.co_tree.column(col, width=width, anchor="center")
        self.co_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self._apply_zebra_stripes(self.co_tree)
        self._refresh_course_tree()

    def _refresh_course_tree(self) -> None:
        """刷新课程列表."""
        for item in self.co_tree.get_children():
            self.co_tree.delete(item)
        for idx, (cid, cinfo) in enumerate(self.dm.courses.items()):
            tag = "odd" if idx % 2 == 0 else "even"
            teacher = self.dm.get_teacher(cinfo.get("teacher_id", ""))
            teacher_name = teacher["name"] if teacher else "未分配"
            self.co_tree.insert(
                "",
                "end",
                values=(
                    cid,
                    cinfo["name"],
                    teacher_name,
                    cinfo.get("class_name", ""),
                ),
                tags=(tag,),
            )

    def _course_add(self) -> None:
        """添加课程对话框。"""
        dialog = tk.Toplevel(self.win)
        dialog.title("添加课程")
        dialog.transient(self.win)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.geometry("400x320")
        self._position_dialog(dialog)

        main_frame = tk.Frame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(main_frame, text="课程编号：", font=FONTS["body"]).grid(
            row=0, column=0, sticky="w", pady=5
        )
        id_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=id_var, font=FONTS["body"], width=25).grid(
            row=0, column=1, pady=5
        )

        tk.Label(main_frame, text="课程名称：", font=FONTS["body"]).grid(
            row=1, column=0, sticky="w", pady=5
        )
        name_var = tk.StringVar()
        tk.Entry(
            main_frame, textvariable=name_var, font=FONTS["body"], width=25
        ).grid(row=1, column=1, pady=5)

        tk.Label(main_frame, text="授课教师：", font=FONTS["body"]).grid(
            row=2, column=0, sticky="w", pady=5
        )
        teacher_var = tk.StringVar()
        teachers = list(self.dm.teachers.keys())
        teacher_combo = ttk.Combobox(
            main_frame,
            textvariable=teacher_var,
            values=teachers,
            width=22,
            state="readonly",
        )
        teacher_combo.grid(row=2, column=1, pady=5)

        tk.Label(main_frame, text="开课班级：", font=FONTS["body"]).grid(
            row=3, column=0, sticky="w", pady=5
        )
        class_var = tk.StringVar()
        tk.Entry(
            main_frame, textvariable=class_var, font=FONTS["body"], width=25
        ).grid(row=3, column=1, pady=5)

        def do_add():
            cid = id_var.get().strip()
            name = name_var.get().strip()
            tid = teacher_var.get().strip()
            cls = class_var.get().strip()
            if not cid or not name:
                show_warning("提示", "课程编号和名称不能为空")
                return
            try:
                self.dm.add_course(cid, name, tid, cls)
                show_info("成功", "课程添加成功")
                dialog.destroy()
                self._refresh_course_tree()
            except Exception as e:
                show_error("错误", str(e))

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        ttk.Button(
            btn_frame, text="确认添加", style="primary.TButton", command=do_add
        ).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(
            side="left", padx=10
        )

    def _course_delete_selected(self) -> None:
        """删除选中的课程."""
        selected = self.co_tree.selection()
        if not selected:
            show_warning("提示", "请先选中一个课程")
            return
        vals = self.co_tree.item(selected[0], "values")
        if not vals or not vals[0]:
            return
        cid = vals[0]
        if not confirm("确认删除", f"确定要删除课程「{cid}」吗？"):
            return
        try:
            self.dm.delete_course(cid)
            show_info("成功", "课程已删除")
            self._refresh_course_tree()
        except Exception as e:
            show_error("错误", str(e))

    def _course_edit(self) -> None:
        """编辑选中的课程."""
        selected = self.co_tree.selection()
        if not selected:
            show_warning("提示", "请先选中一个课程")
            return
        vals = self.co_tree.item(selected[0], "values")
        if not vals or not vals[0]:
            return
        cid = vals[0]
        course = self.dm.get_course(cid)
        if not course:
            return

        dialog = tk.Toplevel(self.win)
        dialog.title("编辑课程")
        dialog.transient(self.win)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.geometry("400x320")
        self._position_dialog(dialog)

        main_frame = tk.Frame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(main_frame, text="课程名称：", font=FONTS["body"]).grid(
            row=0, column=0, sticky="w", pady=5
        )
        name_var = tk.StringVar(value=course.get("name", ""))
        tk.Entry(
            main_frame, textvariable=name_var, font=FONTS["body"], width=25
        ).grid(row=0, column=1, pady=5)

        tk.Label(main_frame, text="授课教师：", font=FONTS["body"]).grid(
            row=1, column=0, sticky="w", pady=5
        )
        teacher_var = tk.StringVar(value=course.get("teacher_id", ""))
        teachers = list(self.dm.teachers.keys())
        teacher_combo = ttk.Combobox(
            main_frame,
            textvariable=teacher_var,
            values=teachers,
            width=22,
            state="readonly",
        )
        teacher_combo.grid(row=1, column=1, pady=5)

        tk.Label(main_frame, text="开课班级：", font=FONTS["body"]).grid(
            row=2, column=0, sticky="w", pady=5
        )
        class_var = tk.StringVar(value=course.get("class_name", ""))
        tk.Entry(
            main_frame, textvariable=class_var, font=FONTS["body"], width=25
        ).grid(row=2, column=1, pady=5)

        def do_save():
            name = name_var.get().strip()
            tid = teacher_var.get().strip()
            cls = class_var.get().strip()
            try:
                self.dm.update_course(cid, name=name, teacher_id=tid, class_name=cls)
                show_info("成功", "课程信息已更新")
                dialog.destroy()
                self._refresh_course_tree()
            except Exception as e:
                show_error("错误", str(e))

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        ttk.Button(
            btn_frame, text="保存", style="primary.TButton", command=do_save
        ).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(
            side="left", padx=10
        )


    def _build_settings_page(self, parent: tk.Frame) -> None:
        """构建美观的系统设置页面."""
        # 清空原有内容
        for widget in parent.winfo_children():
            widget.destroy()

        # 页面标题
        title_frame = tk.Frame(parent, bg="white")
        title_frame.pack(fill="x", padx=20, pady=(15, 5))
        tk.Label(
            title_frame,
            text="⚙️ 系统设置",
            font=("微软雅黑", 18, "bold"),
            fg=TEAL_COLOR,
            bg="white",
        ).pack(side="left")

        # 主容器（滚动区域可选，这里使用普通Frame）
        main_frame = tk.Frame(parent, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ========== 第一组：数据管理 ==========
        group1 = tk.LabelFrame(
            main_frame,
            text="📦 数据管理",
            font=FONTS["normal_bold"],
            fg=TEAL_COLOR,
            bg="white",
            relief="solid",
            bd=1,
            padx=15,
            pady=10,
        )
        group1.pack(fill="x", pady=(0, 20))

        # 网格布局（2列，每列可放多个卡片，但这里一行放两个卡片）
        cards_frame = tk.Frame(group1, bg="white")
        cards_frame.pack(fill="x", pady=5)

        # 辅助函数：创建带图标的操作卡片
        def create_action_card(
            container,
            icon: str,
            title: str,
            desc: str,
            command,
            col: int,
            row: int,
            color: str = TEAL_COLOR,
        ):
            """创建操作按钮卡片."""
            card = tk.Frame(
                container,
                bg="white",
                relief="solid",
                bd=1,
                highlightbackground=UI_COLORS["border"],
                highlightthickness=1,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            container.columnconfigure(col, weight=1)
            # 图标
            tk.Label(card, text=icon, font=("Segoe UI Emoji", 24), bg="white").pack(
                anchor="w", padx=12, pady=(12, 0)
            )
            # 标题
            tk.Label(
                card,
                text=title,
                font=FONTS["normal_bold"],
                bg="white",
                fg=color,
            ).pack(anchor="w", padx=12, pady=(5, 0))
            # 描述
            tk.Label(
                card,
                text=desc,
                font=FONTS["small"],
                bg="white",
                fg=UI_COLORS["text_gray"],
                wraplength=180,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 8))
            # 按钮
            btn = ttk.Button(
                card,
                text="执行",
                style="primary.TButton",
                command=command,
                width=10,
            )
            btn.pack(anchor="e", padx=12, pady=(0, 12))

            # 鼠标悬停效果（改变卡片边框颜色）
            def on_enter(e):
                """鼠标进入事件回调."""
                card.config(highlightbackground=TEAL_COLOR)

            def on_leave(e):
                """鼠标离开事件回调."""
                card.config(highlightbackground=UI_COLORS["border"])

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

        # 备份卡片
        create_action_card(
            cards_frame,
            "💾",
            "数据备份",
            "将当前系统数据保存为备份文件，防止数据丢失。",
            self._settings_backup,
            col=0,
            row=0,
        )
        # 恢复卡片
        create_action_card(
            cards_frame,
            "🔄",
            "数据恢复",
            "从先前备份的文件中恢复数据，覆盖当前状态。",
            self._settings_restore,
            col=1,
            row=0,
        )
        # 重置卡片（危险操作，用红色强调）
        create_action_card(
            cards_frame,
            "⚠️",
            "数据重置",
            "清空所有学生、科目和成绩，恢复初始状态（不可逆）。",
            self._settings_reset,
            col=0,
            row=1,
            color=UI_COLORS["danger"],
        )

        # ========== 第二组：日志与审计 ==========
        group2 = tk.LabelFrame(
            main_frame,
            text="📜 日志审计",
            font=FONTS["normal_bold"],
            fg=TEAL_COLOR,
            bg="white",
            relief="solid",
            bd=1,
            padx=15,
            pady=10,
        )
        group2.pack(fill="x")

        cards_frame2 = tk.Frame(group2, bg="white")
        cards_frame2.pack(fill="x", pady=5)

        create_action_card(
            cards_frame2,
            "📋",
            "查看成绩日志",
            "查看所有成绩修改记录，包括时间、学生、科目、新旧成绩。",
            self._settings_view_logs,
            col=0,
            row=0,
        )
        # 可以预留更多卡片，比如“操作日志”（未来扩展）
        # 第二列留空或者放一个占位
        placeholder = tk.Frame(cards_frame2, bg="white")
        placeholder.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        cards_frame2.columnconfigure(1, weight=1)

    def _settings_backup(self) -> None:
        """手动备份数据文件."""
        import shutil
        from datetime import datetime

        try:
            src = self.dm.fp
            bak_name = f"grades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.bak"
            bak_path = os.path.join(os.path.dirname(src), bak_name)
            shutil.copy2(src, bak_path)
            show_info("成功", f"数据已备份到：{bak_name}")
        except Exception as e:
            show_error("错误", f"备份失败: {e}")

    def _settings_restore(self) -> None:
        """从备份文件恢复数据."""
        from tkinter import filedialog

        fp = filedialog.askopenfilename(
            title="选择备份文件",
            filetypes=[("备份文件", "*.bak"), ("JSON", "*.json")],
        )
        if not fp:
            return
        if not confirm("确认恢复", "恢复将覆盖当前数据，确定继续吗？"):
            return
        try:
            import shutil

            shutil.copy2(fp, self.dm.fp)
            self.dm.load()
            show_info("成功", "数据恢复完成")
        except Exception as e:
            show_error("错误", f"恢复失败: {e}")

    def _settings_reset(self) -> None:
        """清空所有数据并恢复初始状态."""
        if not confirm(
            "危险操作确认",
            "确定要清空所有数据吗？\n\n此操作不可恢复！",
        ):
            return
        try:
            self.dm.data = self.dm._create_empty_data()
            self.dm.save()
            show_info("成功", "数据已重置为初始状态")
        except Exception as e:
            show_error("错误", str(e))

    def _settings_view_logs(self) -> None:
        """查看成绩修改历史日志."""
        dialog = tk.Toplevel(self.win)
        dialog.title("成绩修改日志")
        dialog.geometry("700x500")
        dialog.transient(self.win)

        columns = ["时间", "学号", "科目", "旧成绩", "新成绩"]
        widths = [120, 100, 120, 80, 80]
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=20)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        self._apply_zebra_stripes(tree)

        history = self.dm.get_history()
        for idx, record in enumerate(history):
            tag = "odd" if idx % 2 == 0 else "even"
            tree.insert(
                "",
                "end",
                values=(
                    record.get("time", ""),
                    record.get("sid", ""),
                    record.get("subject", ""),
                    record.get("old", ""),
                    record.get("new", ""),
                ),
                tags=(tag,),
            )

    # ------------------------------------------------------------------
    # 科目分析页面（从教师端迁移）
    # ------------------------------------------------------------------

    def _build_analysis_page(self, parent: tk.Frame) -> None:
        """构建科目分析页面（支持全部/按班级分析）."""
        tk.Label(
            parent,
            text="📊 科目分析",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        control_frame = tk.Frame(parent, bg="white")
        control_frame.pack(pady=3)
        subject_label = tk.Label(control_frame, text="科目：", bg="white")
        subject_label.pack(side="left", padx=5)
        first_subject = self.dm.subjects[0] if self.dm.subjects else ""
        self.an_subj = tk.StringVar(value=first_subject)
        self.an_cb = ttk.Combobox(
            control_frame,
            textvariable=self.an_subj,
            values=self.dm.subjects,
            width=10,
            state="readonly",
        )
        self.an_cb.pack(side="left", padx=5)

        # 班级选择器：全部 + 各班级
        tk.Label(control_frame, text="班级：", bg="white").pack(side="left", padx=(15, 2))
        self.an_class = tk.StringVar(value="全部")
        self.an_class_cb = ttk.Combobox(
            control_frame,
            textvariable=self.an_class,
            values=["全部"] + self.dm.classes,
            width=12,
            state="readonly",
        )
        self.an_class_cb.pack(side="left", padx=5)

        ttk.Button(
            control_frame,
            text="📊 分析",
            style="primary.TButton",
            command=self._analyze_subject,
        ).pack(side="left", padx=5)
        ttk.Button(
            control_frame,
            text="⚙️ 科目管理",
            style="warning.TButton",
            command=self._manage_subjects,
        ).pack(side="left", padx=5)

        main_frame = tk.Frame(parent, bg="white")
        main_frame.pack(fill="both", expand=True, padx=5, pady=3)

        # 左侧：统计信息
        left_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        left_frame.pack(side="left", fill="y", padx=3, pady=3)
        stats_label = tk.Label(
            left_frame,
            text="📈 统计信息",
            font=FONTS["body_bold"],
            bg="white",
        )
        stats_label.pack(pady=4)
        self.alab = {}
        stat_items = [
            ("人数", "cnt"),
            ("最高", "mx"),
            ("最低", "mn"),
            ("均分", "av"),
            ("及格率", "ps"),
            ("优秀率", "ex"),
        ]
        for label, key in stat_items:
            row = tk.Frame(left_frame, bg="white")
            row.pack(fill="x", pady=2)
            row_label = tk.Label(row, text=label + "：", bg="white")
            row_label.pack(side="left", padx=10)
            self.alab[key] = tk.Label(
                row, text="—", font=("微软雅黑", 10, "bold"), bg="white"
            )
            self.alab[key].pack(side="left")

        self.adist = ttk.Treeview(
            left_frame, columns=["段", "人", "%"], show="headings", height=6
        )
        for col, width in [("段", 60), ("人", 40), ("%", 50)]:
            self.adist.heading(col, text=col)
            self.adist.column(col, width=width, anchor="center")
        self.adist.pack(pady=6)
        dist_tags = [
            ("0-59", UI_COLORS["danger_light"]),
            ("60-69", UI_COLORS["warning_light"]),
            ("70-79", UI_COLORS["warn_light"]),
            ("80-89", UI_COLORS["info_light"]),
            ("90-100", UI_COLORS["success_light"]),
        ]
        for seg, bg in dist_tags:
            self.adist.tag_configure(seg, background=bg)

        # 右侧：成绩明细
        right_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        right_frame.pack(side="right", fill="both", expand=True, padx=3, pady=3)
        detail_label = tk.Label(
            right_frame,
            text="📋 成绩明细",
            font=FONTS["body_bold"],
            bg="white",
        )
        detail_label.pack(pady=4)
        detail_cols = ["名次", "学号", "姓名", "班级", "成绩", "等级"]
        detail_widths = [50, 110, 90, 90, 80, 80]
        self.adt = ttk.Treeview(
            right_frame, columns=detail_cols, show="headings", height=20
        )
        for col, width in zip(detail_cols, detail_widths):
            self.adt.heading(col, text=col)
            self.adt.column(col, width=width, anchor="center")
        self.adt.pack(fill="both", expand=True, padx=10, pady=10)
        level_tags = [
            ("excellent", UI_COLORS["success_light"]),
            ("good", UI_COLORS["info_light"]),
            ("pass_", UI_COLORS["warn_light"]),
            ("fail", UI_COLORS["danger_light"]),
        ]
        for tag, bg in level_tags:
            self.adt.tag_configure(tag, background=bg)

        # 默认分析第一个科目
        if self.dm.subjects:
            self.win.after(100, self._analyze_subject)

    def _analyze_subject(self) -> None:
        """分析科目成绩分布（支持按班级过滤）."""
        subject = self.an_subj.get()
        if not subject:
            show_warning("提示", "请先添加科目！")
            return

        # 按班级过滤学生集合
        class_name = self.an_class.get() if hasattr(self, "an_class") else "全部"
        student_ids = None
        if class_name and class_name != "全部":
            student_ids = {
                sid for sid, stu in self.dm.students.items()
                if stu.get("class", "") == class_name
            }

        analysis = self.dm.analyze_subject(subject, student_ids=student_ids)
        if not analysis:
            show_info("提示", "该科目暂无成绩数据")
            return

        scope = f"（{class_name}）" if class_name != "全部" else "（全部班级）"
        self.alab["cnt"].config(text=f"{analysis['count']} 人")
        self.alab["mx"].config(text=str(analysis["max"]), fg=UI_COLORS["danger_dark"])
        self.alab["mn"].config(
            text=str(analysis["min"]),
            fg=UI_COLORS["danger"] if analysis["min"] < 60 else UI_COLORS["text_dark"],
        )
        self.alab["av"].config(text=str(analysis["avg"]))
        self.alab["ps"].config(
            text=f"{analysis['pass_rate']}%",
            fg=UI_COLORS["danger_dark"] if analysis["pass_rate"] >= 60 else UI_COLORS["danger"],
        )
        self.alab["ex"].config(text=f"{analysis['excellent_rate']}%")

        self.adist.delete(*self.adist.get_children())
        for seg in ["0-59", "60-69", "70-79", "80-89", "90-100"]:
            count = analysis["distribution"].get(seg, 0)
            pct = (
                f"{round(count / analysis['count'] * 100, 1)}%"
                if analysis["count"]
                else "0%"
            )
            self.adist.insert("", "end", values=(seg, count, pct), tags=(seg,))

        self.adt.delete(*self.adt.get_children())
        rows = []
        for sid, stu in self.dm.students.items():
            # 按班级过滤
            if class_name and class_name != "全部" and stu.get("class", "") != class_name:
                continue
            score = stu["scores"].get(subject)
            if score is not None:
                rows.append((sid, stu["name"], stu.get("class", ""), score))
        rows.sort(key=lambda x: x[3], reverse=True)

        for rank, (sid, name, cls, score) in enumerate(rows, 1):
            tag, level = self._get_level_tag(score)
            self.adt.insert(
                "",
                "end",
                values=(rank, sid, name, cls, score, level),
                tags=(tag,),
            )

    @staticmethod
    def _get_level_tag(score: float) -> tuple[str, str]:
        """根据分数返回等级标签文本."""
        if score >= 90:
            return "excellent", "优秀"
        if score >= 75:
            return "good", "良好"
        if score >= 60:
            return "pass_", "及格"
        return "fail", "不及格"

    def _manage_subjects(self) -> None:
        """管理科目增删改."""
        dialog = tk.Toplevel(self.win)
        dialog.title("科目管理")
        dialog.geometry("350x350")
        self._position_dialog(dialog)

        dialog.grab_set()

        listbox = tk.Listbox(dialog)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        for s in self.dm.subjects:
            """添加新记录."""
            listbox.insert("end", s)

        def _add() -> None:
            name = simpledialog.askstring("添加", "请输入科目名称：", parent=dialog)
            if name:
                try:
                    self.dm.add_subject(name)
                    listbox.insert("end", name)
                    self._refresh_subject_ui()
                except Exception as e:
                    """删除选中记录."""
                    show_error("错误", str(e))

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
                show_error("错误", str(e))

        # 按钮栏：拉开间距 + 不同颜色样式
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)

        ttk.Button(
            btn_frame, text="➕ 添加", style="success.TButton", command=_add
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame, text="🗑️ 删除", style="danger.TButton", command=_delete
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame, text="关闭", style="secondary.TButton", command=dialog.destroy
        ).pack(side="left", padx=10)

    def _refresh_subject_ui(self) -> None:
        """刷新科目相关界面."""
        subjects = self.dm.subjects
        if hasattr(self, "an_cb"):
            self.an_cb["values"] = subjects

    # ------------------------------------------------------------------
    # 通知管理页面
    # ------------------------------------------------------------------

    def _build_notice_mgmt_page(self, parent):
        """构建通知管理页面."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent,
            text="📢 通知管理",
            font=("微软雅黑", 18, "bold"),
            bg="white",
            fg=TEAL_COLOR,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # 工具栏
        tool_frame = tk.Frame(parent, bg="white")
        tool_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Button(
            tool_frame,
            text="➕ 发布通知",
            font=FONTS["body"],
            bg=TEAL_COLOR,
            fg="white",
            activebackground=TEAL_DARK,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self._notice_add,
            padx=16,
            pady=6,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            tool_frame,
            text="🗑️ 删除选中",
            font=FONTS["body"],
            bg=COLORS["danger"],
            fg="white",
            activebackground=UI_COLORS["danger_hover"],
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self._notice_delete_selected,
            padx=16,
            pady=6,
        ).pack(side="left")

        # 树状列表
        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("ID", "标题", "发布者", "发布角色", "接收对象", "发布日期")
        self._notice_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=15
        )
        col_widths = [50, 200, 100, 100, 100, 120]
        for col, width in zip(columns, col_widths):
            self._notice_tree.heading(col, text=col)
            self._notice_tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self._notice_tree.yview
        )
        hsb = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self._notice_tree.xview
        )
        self._notice_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._notice_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self._apply_zebra_stripes(self._notice_tree)
        self._notice_tree.bind("<Double-1>", self._notice_double_click)

        self._refresh_notice_tree()

    def _refresh_notice_tree(self):
        """刷新通知列表."""
        if not hasattr(self, "_notice_tree"):
            return
        for item in self._notice_tree.get_children():
            self._notice_tree.delete(item)

        notices = self.dm.get_notices()
        for idx, notice in enumerate(notices):
            tag = "odd" if idx % 2 == 0 else "even"
            self._notice_tree.insert(
                "",
                "end",
                values=(
                    notice.get("id", ""),
                    notice.get("title", ""),
                    notice.get("publisher", ""),
                    notice.get("publisher_role", ""),
                    notice.get("target", "all"),
                    notice.get("date", ""),
                ),
                tags=(tag,),
            )

    def _notice_add(self):
        """发布新通知."""
        dialog = tk.Toplevel(self.win)
        dialog.title("发布通知")
        dialog.geometry("500x480")
        dialog.transient(self.win)
        dialog.resizable(False, False)
        dialog.configure(bg="white")

        tk.Label(dialog, text="标题：", font=FONTS["body"], bg="white").pack(
            anchor="w", padx=20, pady=(20, 5)
        )
        title_entry = tk.Entry(dialog, font=FONTS["body"], width=50)
        title_entry.pack(padx=20, pady=(0, 10), fill="x")

        tk.Label(dialog, text="接收对象：", font=FONTS["body"], bg="white").pack(
            anchor="w", padx=20, pady=(0, 5)
        )
        target_var = tk.StringVar(value="all")
        target_frame = tk.Frame(dialog, bg="white")
        target_frame.pack(anchor="w", padx=20, pady=(0, 10))
        tk.Radiobutton(
            target_frame,
            text="全部",
            variable=target_var,
            value="all",
            font=FONTS["caption"],
            bg="white",
        ).pack(side="left", padx=(0, 15))
        tk.Radiobutton(
            target_frame,
            text="仅老师",
            variable=target_var,
            value="teacher",
            font=FONTS["caption"],
            bg="white",
        ).pack(side="left", padx=(0, 15))
        tk.Radiobutton(
            target_frame,
            text="仅学生",
            variable=target_var,
            value="student",
            font=FONTS["caption"],
            bg="white",
        ).pack(side="left")

        tk.Label(dialog, text="内容：", font=FONTS["body"], bg="white").pack(
            anchor="w", padx=20, pady=(0, 5)
        )
        content_text = tk.Text(dialog, font=FONTS["body"], width=50, height=10)
        content_text.pack(padx=20, pady=(0, 15), fill="both", expand=True)

        def _save():
            title = title_entry.get().strip()
            content = content_text.get("1.0", "end-1c").strip()
            target = target_var.get()
            if not title:
                show_warning("提示", "请输入通知标题")
                return
            if not content:
                show_warning("提示", "请输入通知内容")
                return
            notice_id = self.dm.add_notice(
                title=title,
                content=content,
                publisher=self.user_info.get("username", "admin"),
                publisher_role="admin",
                target=target,
            )
            show_info("成功", "通知发布成功！")
            dialog.destroy()
            self._refresh_notice_tree()

        tk.Button(
            dialog,
            text="发布",
            font=FONTS["normal"],
            bg=TEAL_COLOR,
            fg="white",
            activebackground=TEAL_DARK,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=_save,
            width=10,
            height=5,
        ).pack(fill="x", padx=20, pady=(0, 20))

    def _notice_delete_selected(self):
        """删除选中的通知."""
        if not hasattr(self, "_notice_tree"):
            return
        selection = self._notice_tree.selection()
        if not selection:
            show_warning("提示", "请先选择要删除的通知")
            return
        if not confirm("确认", "确定要删除选中的通知吗？"):
            return
        for item in selection:
            notice_id = self._notice_tree.item(item, "values")[0]
            self.dm.delete_notice(notice_id)
        show_info("成功", "通知已删除")
        self._refresh_notice_tree()

    def _notice_double_click(self, event):
        """双击查看通知详情."""
        if not hasattr(self, "_notice_tree"):
            return
        selection = self._notice_tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self._notice_tree.item(item, "values")
        notice_id = values[0]

        notices = self.dm.get_notices()
        notice = next((n for n in notices if str(n.get("id")) == str(notice_id)), None)
        if not notice:
            return

        dialog = tk.Toplevel(self.win)
        dialog.title(f"通知详情 - {notice.get('title', '')}")
        dialog.geometry("500x400")
        dialog.transient(self.win)

        tk.Label(
            dialog,
            text=notice.get("title", ""),
            font=FONTS["title"],
            bg="white",
            fg=TEAL_COLOR,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # 公告元信息：发布者、日期、接收对象
        publisher = notice.get("publisher", "")
        date = notice.get("date", "")
        target = notice.get("target", "all")
        info_text = f"发布者：{publisher}  |  日期：{date}  |  接收对象：{target}"
        tk.Label(
            dialog,
            text=info_text,
            font=FONTS["caption"],
            bg="white",
            fg="#666666",
        ).pack(anchor="w", padx=20, pady=(0, 15))

        content_text = tk.Text(dialog, font=FONTS["body"], wrap="word")
        content_text.insert("1.0", notice.get("content", ""))
        content_text.config(state="disabled")
        content_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ------------------------------------------------------------------
    # 课表管理
    # ------------------------------------------------------------------

    def _build_schedule_mgmt_page(self, parent):
        """构建课表管理页面（管理员可增删改，按班级分课表）."""
        # 标题和工具栏
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))

        tk.Label(
            header_frame,
            text="📅 课表管理",
            font=("微软雅黑", 18, "bold"),
            fg=TEAL_COLOR,
            bg="white",
        ).pack(side="left")

        # 班级选择器
        class_frame = tk.Frame(header_frame, bg="white")
        class_frame.pack(side="right", padx=(0, 5))
        tk.Label(
            class_frame, text="班级:", font=FONTS["body"], bg="white"
        ).pack(side="left", padx=(0, 5))
        self._schedule_class_var = tk.StringVar()
        self._schedule_class_combo = ttk.Combobox(
            class_frame,
            textvariable=self._schedule_class_var,
            values=self.dm.classes,
            state="readonly",
            width=15,
            font=FONTS["caption"],
        )
        self._schedule_class_combo.pack(side="left")
        # 默认选第一个班级
        if self.dm.classes:
            self._schedule_class_var.set(self.dm.classes[0])
        # 切换班级时刷新表格
        self._schedule_class_combo.bind(
            "<<ComboboxSelected>>", lambda e: self._refresh_schedule_tree()
        )

        toolbar = tk.Frame(parent, bg="white")
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        tk.Button(
            toolbar,
            text="➕ 添加课程",
            font=FONTS["body"],
            bg=TEAL_COLOR,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._schedule_add,
            padx=16,
            pady=6,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            toolbar,
            text="🗑 删除选中",
            font=FONTS["body"],
            bg="#E74C3C",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._schedule_delete_selected,
            padx=16,
            pady=6,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            toolbar,
            text="📜 查看历史",
            font=FONTS["body"],
            bg="#3498DB",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._schedule_show_history,
            padx=16,
            pady=6,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            toolbar,
            text="🔄 刷新",
            font=FONTS["body"],
            bg="#95A5A6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._refresh_schedule_tree,
            padx=16,
            pady=6,
        ).pack(side="left")

        # Treeview 表格
        columns = (
            "id",
            "weekday",
            "session",
            "period",
            "course",
            "teacher",
            "room",
            "updated",
        )
        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ysb = ttk.Scrollbar(tree_frame, orient="vertical")
        xsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        self._schedule_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=ysb.set,
            xscrollcommand=xsb.set,
        )
        ysb.config(command=self._schedule_tree.yview)
        xsb.config(command=self._schedule_tree.xview)

        headings = {
            "id": ("ID", 120),
            "weekday": ("星期", 60),
            "session": ("时段", 50),
            "period": ("节次", 50),
            "course": ("课程名", 140),
            "teacher": ("教师", 100),
            "room": ("教室", 80),
            "updated": ("最后更新", 130),
        }
        for col, (text, width) in headings.items():
            self._schedule_tree.heading(col, text=text)
            self._schedule_tree.column(col, width=width, anchor="center")

        self._schedule_tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y")

        # 斑马纹样式
        self._apply_zebra_stripes(self._schedule_tree, "oddrow", "evenrow")

        # 双击编辑
        self._schedule_tree.bind("<Double-1>", self._schedule_edit_double_click)

        # 加载数据
        self._refresh_schedule_tree()

    def _refresh_schedule_tree(self):
        """刷新课表Treeview，按选中班级过滤."""
        for item in self._schedule_tree.get_children():
            self._schedule_tree.delete(item)

        # 按选中班级过滤
        class_name = self._schedule_class_var.get() if hasattr(self, "_schedule_class_var") else ""
        schedules = self.dm.get_schedules(class_name=class_name)
        for i, s in enumerate(schedules):
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            self._schedule_tree.insert(
                "",
                "end",
                values=(
                    s.get("id", ""),
                    s.get("weekday", ""),
                    s.get("session", ""),
                    s.get("period", ""),
                    s.get("course", ""),
                    s.get("teacher", ""),
                    s.get("room", ""),
                    s.get("updated_at", ""),
                ),
                tags=(tag,),
            )

    def _schedule_add(self):
        """添加课程对话框."""
        dialog = tk.Toplevel(self.win)
        dialog.title("添加课程")
        dialog.geometry("400x430")
        dialog.resizable(False, False)
        dialog.transient(self.win)
        dialog.grab_set()

        tk.Label(
            dialog, text="添加课程", font=FONTS["title"], fg=TEAL_COLOR
        ).pack(pady=(15, 10))

        form = tk.Frame(dialog)
        form.pack(padx=20, pady=5)

        fields = [
            ("班级:", "class_entry"),
            ("星期:", "weekday_entry"),
            ("时段:", "session_entry"),
            ("节次:", "period_entry"),
            ("课程名:", "course_entry"),
            ("教师:", "teacher_entry"),
            ("教室:", "room_entry"),
        ]
        entries = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=FONTS["caption"]).grid(
                row=i, column=0, sticky="e", padx=(0, 8), pady=6
            )
            entry = tk.Entry(form, font=FONTS["caption"], width=25)
            entry.grid(row=i, column=1, pady=6)
            entries[key] = entry

        # 班级下拉（先销毁原来的 Entry）
        from tkinter import ttk as _ttk
        entries["class_entry"].destroy()
        class_combo = _ttk.Combobox(
            form, values=self.dm.classes, font=FONTS["caption"], width=22,
            state="readonly",
        )
        class_combo.grid(row=0, column=1, pady=6)
        # 默认选中当前课表页面选中的班级
        cur_class = self._schedule_class_var.get() if hasattr(self, "_schedule_class_var") else ""
        if cur_class:
            class_combo.set(cur_class)
        entries["class_entry"] = class_combo

        # 星期下拉（先销毁原来的 Entry）
        entries["weekday_entry"].destroy()
        weekday_vals = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        weekday_combo = _ttk.Combobox(
            form, values=weekday_vals, font=FONTS["caption"], width=22
        )
        weekday_combo.grid(row=1, column=1, pady=6)
        entries["weekday_entry"] = weekday_combo

        # 时段下拉（先销毁原来的 Entry）
        entries["session_entry"].destroy()
        session_vals = ["上午", "下午"]
        session_combo = _ttk.Combobox(
            form, values=session_vals, font=FONTS["caption"], width=22
        )
        session_combo.grid(row=2, column=1, pady=6)
        entries["session_entry"] = session_combo

        def confirm():
            class_name = entries["class_entry"].get().strip()
            weekday = entries["weekday_entry"].get().strip()
            session = entries["session_entry"].get().strip()
            period = entries["period_entry"].get().strip()
            course = entries["course_entry"].get().strip()
            teacher = entries["teacher_entry"].get().strip()
            room = entries["room_entry"].get().strip()

            if not all([class_name, weekday, session, period, course]):
                show_warning(
                    "提示",
                    "班级、星期、时段、节次和课程名为必填项！",
                    parent=dialog,
                )
                return
            try:
                period = int(period)
            except ValueError:
                show_warning("提示", "节次必须为数字！", parent=dialog)
                return

            username = (
                self.user_info.get("username", "admin")
                if hasattr(self, "user_info")
                else "admin"
            )
            self.dm.add_schedule(
                weekday,
                session,
                period,
                course,
                teacher,
                room,
                operator=username,
                class_name=class_name,
            )
            self._refresh_schedule_tree()
            dialog.destroy()
            show_info("成功", "课程添加成功！")

        tk.Button(
            dialog,
            text="确认添加",
            font=FONTS["body"],
            bg=TEAL_COLOR,
            fg="white",
            relief="flat",
            command=confirm,
            padx=20,
            pady=6,
        ).pack(pady=20)

    def _schedule_edit_double_click(self, event):
        """双击课表行编辑."""
        selection = self._schedule_tree.selection()
        if not selection:
            return

        item = self._schedule_tree.item(selection[0])
        values = item["values"]
        schedule_id = values[0]

        dialog = tk.Toplevel(self.win)
        dialog.title("编辑课程")
        dialog.geometry("400x430")
        dialog.resizable(False, False)
        dialog.transient(self.win)
        dialog.grab_set()

        tk.Label(
            dialog, text="编辑课程", font=FONTS["title"], fg=TEAL_COLOR
        ).pack(pady=(15, 10))

        form = tk.Frame(dialog)
        form.pack(padx=20, pady=5)

        fields = [
            ("班级:", "class_entry"),
            ("星期:", "weekday_entry"),
            ("时段:", "session_entry"),
            ("节次:", "period_entry"),
            ("课程名:", "course_entry"),
            ("教师:", "teacher_entry"),
            ("教室:", "room_entry"),
        ]
        entries = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=FONTS["caption"]).grid(
                row=i, column=0, sticky="e", padx=(0, 8), pady=6
            )
            entry = tk.Entry(form, font=FONTS["caption"], width=25)
            entry.grid(row=i, column=1, pady=6)
            entries[key] = entry

        # 班级下拉
        from tkinter import ttk as _ttk
        entries["class_entry"].destroy()
        class_combo = _ttk.Combobox(
            form, values=self.dm.classes, font=FONTS["caption"], width=22,
            state="readonly",
        )
        class_combo.grid(row=0, column=1, pady=6)
        entries["class_entry"] = class_combo

        # 星期下拉（先销毁原来的 Entry）
        entries["weekday_entry"].destroy()
        weekday_vals = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        weekday_combo = _ttk.Combobox(
            form, values=weekday_vals, font=FONTS["caption"], width=22
        )
        weekday_combo.grid(row=1, column=1, pady=6)
        entries["weekday_entry"] = weekday_combo

        # 时段下拉（先销毁原来的 Entry）
        entries["session_entry"].destroy()
        session_vals = ["上午", "下午"]
        session_combo = _ttk.Combobox(
            form, values=session_vals, font=FONTS["caption"], width=22
        )
        session_combo.grid(row=2, column=1, pady=6)
        entries["session_entry"] = session_combo

        # 填充现有数据（columns: id, weekday, session, period, course, teacher, room, updated）
        # 通过 schedule_id 查完整数据以获取 class_name（班级列已从Treeview移除）
        _all_sched = self.dm.get_schedules()
        _sched_data = next((s for s in _all_sched if s.get("id") == schedule_id), None)
        entries["class_entry"].set(_sched_data.get("class_name", "") if _sched_data else "")
        entries["weekday_entry"].set(str(values[1]))
        entries["session_entry"].set(str(values[2]))
        entries["period_entry"].insert(0, str(values[3]))
        entries["course_entry"].insert(0, str(values[4]))
        entries["teacher_entry"].insert(0, str(values[5]))
        entries["room_entry"].insert(0, str(values[6]))

        def confirm():
            class_name = entries["class_entry"].get().strip()
            weekday = entries["weekday_entry"].get().strip()
            session = entries["session_entry"].get().strip()
            period = entries["period_entry"].get().strip()
            course = entries["course_entry"].get().strip()
            teacher = entries["teacher_entry"].get().strip()
            room = entries["room_entry"].get().strip()

            if not all([class_name, weekday, session, period, course]):
                show_warning(
                    "提示",
                    "班级、星期、时段、节次和课程名为必填项！",
                    parent=dialog,
                )
                return
            try:
                period = int(period)
            except ValueError:
                show_warning("提示", "节次必须为数字！", parent=dialog)
                return

            username = (
                self.user_info.get("username", "admin")
                if hasattr(self, "user_info")
                else "admin"
            )
            self.dm.update_schedule(
                schedule_id,
                weekday,
                session,
                period,
                course,
                teacher,
                room,
                operator=username,
                class_name=class_name,
            )
            self._refresh_schedule_tree()
            dialog.destroy()
            show_info("成功", "课程修改成功！")

        tk.Button(
            dialog,
            text="确认修改",
            font=FONTS["body"],
            bg=TEAL_COLOR,
            fg="white",
            relief="flat",
            command=confirm,
            padx=20,
            pady=6,
        ).pack(pady=20)

    def _schedule_delete_selected(self):
        """删除选中的课表条目."""
        selection = self._schedule_tree.selection()
        if not selection:
            show_warning("提示", "请先选中要删除的课程！")
            return

        item = self._schedule_tree.item(selection[0])
        values = item["values"]
        schedule_id = values[0]
        course_info = f"{values[1]} {values[2]}第{values[3]}节 {values[4]}"

        if confirm("确认删除", f"确定要删除课程：{course_info}？"):
            username = (
                self.user_info.get("username", "admin")
                if hasattr(self, "user_info")
                else "admin"
            )
            self.dm.delete_schedule(schedule_id, operator=username)
            self._refresh_schedule_tree()
            show_info("成功", "课程已删除！")

    def _schedule_show_history(self):
        """查看课表变更历史."""
        history_win = tk.Toplevel(self.win)
        history_win.title("课表变更历史")
        history_win.geometry("750x450")
        history_win.transient(self.win)

        tk.Label(
            history_win,
            text="📜 课表变更历史",
            font=FONTS["title"],
            fg=TEAL_COLOR,
        ).pack(pady=(15, 10))

        columns = ("time", "action", "old_summary", "new_summary", "operator")
        tree_frame = tk.Frame(history_win)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)

        ysb = ttk.Scrollbar(tree_frame, orient="vertical")
        xsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=ysb.set,
            xscrollcommand=xsb.set,
        )
        ysb.config(command=tree.yview)
        xsb.config(command=tree.xview)

        headings = {
            "time": ("时间", 140),
            "action": ("操作", 60),
            "old_summary": ("原内容摘要", 220),
            "new_summary": ("新内容摘要", 220),
            "operator": ("操作者", 80),
        }
        for col, (text, width) in headings.items():
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor="center")

        tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y")

        # 斑马纹
        self._apply_zebra_stripes(tree, "oddrow", "evenrow")

        history = self.dm.get_schedule_history()
        for i, h in enumerate(history):
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            tree.insert(
                "",
                "end",
                values=(
                    h.get("time", ""),
                    h.get("action", ""),
                    h.get("old_summary", ""),
                    h.get("new_summary", ""),
                    h.get("operator", ""),
                ),
                tags=(tag,),
            )

        def _clear_history():
            if not confirm(
                "确认清空",
                "确定要清空所有课表变更历史记录吗？\n此操作不可恢复！",
                parent=history_win,
            ):
                return
            self.dm.clear_schedule_history()
            for item in tree.get_children():
                tree.delete(item)
            show_info("成功", "历史记录已清空", parent=history_win)

        tk.Button(
            history_win,
            text="🗑 清空历史",
            font=FONTS["caption"],
            bg="#E74C3C",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=_clear_history,
            padx=16,
            pady=6,
        ).pack(pady=(0, 15))

    # ========== 导入导出与管理页面（从教师端迁移） ==========

    def _refresh_all_pages(self) -> None:
        """计算科目列宽度."""
        if hasattr(self, "mg_tree"):
            self._refresh_manage_tree()
        if hasattr(self, "ex_tree"):
            if hasattr(self, "_excel_parent"):
                """创建并配置 Treeview 表格控件."""
                self._refresh_excel_tree(self._excel_parent)
        if hasattr(self, "in_tree"):
            self.in_tree.delete(*self.in_tree.get_children())
            for _ in range(5):
                self._input_add_row()
        if hasattr(self, "cl_tree"):
            self._refresh_class_tree()

    def _build_input_page(self, parent: tk.Frame) -> None:
        """构建成绩录入页面，提供期号、日期、科目成绩输入和批量提交功能.

        Args:
            parent: 父容器 Frame，用于放置录入页面内容。
        """
        tk.Label(
            parent,
            text="📝 批量录入",
            font=FONTS["title"],
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
            btn = ttk.Button(btn_frame, text=text, style="primary.TButton", command=cmd)
            btn.pack(side="left", padx=4)

        subjects = self.dm.subjects
        columns = ["行号", "学号*", "姓名*", "班级"] + subjects + ["操作"]
        widths = [45, 100, 90, 90] + self._calc_subject_widths(subjects) + [70]
        self.in_tree = self._create_treeview(parent, columns, widths, 12)
        self.in_tree.bind("<Double-1>", self._input_cell_double_click)

        for _ in range(5):
            self._input_add_row()

    def _input_add_row(self) -> None:
        """在录入表格末尾添加一行空白录入行."""
        n = len(self.in_tree.get_children()) + 1
        values = [n, "", "", ""] + [""] * len(self.dm.subjects) + ["删除"]
        tag = "odd" if n % 2 == 1 else "even"
        self.in_tree.insert("", "end", values=values, tags=(tag,))

    def _input_delete_row(self) -> None:
        """删除录入表格中选中的行，并重新编号."""
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
        """清空录入表格所有内容，并重新初始化 5 行空白行."""
        if confirm("确认", "确定清空所有录入内容？"):
            self.in_tree.delete(*self.in_tree.get_children())
            for _ in range(5):
                self._input_add_row()

    def _input_cell_double_click(self, event: tk.Event) -> None:
        """双击单元格时创建 Entry 控件进行行内编辑.

        Args:
            event: 鼠标双击事件对象，包含点击坐标信息。

        双击非操作列时，会在单元格位置显示输入框，
        支持回车确认、ESC 取消和失焦自动保存。
        成绩列会自动校验数值范围（0-100）。
        """
        row_id = self.in_tree.identify_row(event.y)
        col_id = self.in_tree.identify_column(event.x)
        if not row_id:
            return
        col_index = int(col_id.replace("#", "")) - 1
        columns = self.in_tree["columns"]
        if col_index >= len(columns) or columns[col_index] == "操作":
            return

        x, y, w, h = self.in_tree.bbox(row_id, col_id)
        entry = tk.Entry(self.in_tree, font=FONTS["caption"], relief="solid")
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
                        show_warning("输入错误", "成绩必须在 0-100 之间！")
                        val = ""
                except ValueError:
                    show_warning("输入错误", "成绩必须是数字！")
                    val = ""
            vals[col_index] = val
            entry.destroy()
            self.in_tree.item(row_id, values=vals)

        entry.bind("<Return>", lambda _: _commit_edit())
        entry.bind("<Escape>", lambda _: entry.destroy())
        entry.bind("<FocusOut>", lambda _: _commit_edit())

    def _input_save_rows(self) -> None:
        """保存录入表格中的所有有效数据到系统.

        逐行读取录入表格内容，校验学号、姓名、班级和成绩，
        将有效数据写入 DataManager。已存在的学生会更新信息，
        不存在的学生会新增。保存成功后刷新所有页面并提示结果。
        """
        subjects = self.dm.subjects
        saved = 0
        errors = []

        for item in self.in_tree.get_children():
            vals = self.in_tree.item(item, "values")
            sid = str(vals[1]).strip()
            name = str(vals[2]).strip()
            cls = str(vals[3]).strip()
            scores_raw = vals[4 : 4 + len(subjects)]

            if (
                not sid
                and not name
                and not cls
                and all(str(x).strip() == "" for x in scores_raw)
            ):
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
                            error_msg = f"行 {vals[0]}: {subj} 成绩超出范围 (0-100)"
                            errors.append(error_msg)
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
            show_warning("部分失败", "\n".join(errors[:10]))
        if saved:
            show_info("成功", f"保存 {saved} 名学生信息")
            self._show_status(f"保存 {saved} 人", "ok")
            self._refresh_all_pages()
            logger.info("录入保存: %d 名学生", saved)
        elif not errors:
            show_info("提示", "无有效数据可保存")

    def _build_excel_page(self, parent: tk.Frame) -> None:
        """构建 Excel 导入导出页面."""
        self._excel_parent = tk.Frame(parent, bg="white")
        self._excel_parent.pack(fill="both", expand=True)

        tk.Label(
            self._excel_parent,
            text="📥 Excel 导入导出",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        btn_frame = tk.Frame(self._excel_parent, bg="white")
        btn_frame.pack(pady=(0, 15))
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

        self._refresh_excel_tree(self._excel_parent)

    def _refresh_excel_tree(self, parent) -> None:
        """刷新 Excel 导入导出页面的表格，包含列头和行数据.

        Args:
            parent: 父容器 Frame，用于放置表格组件。

        Note:
            每次刷新会先销毁旧表格容器，再重新创建表头和数据行。
        """
        if hasattr(self, "excel_frame"):
            self.excel_frame.destroy()
            delattr(self, "excel_frame")

        self.excel_frame = tk.Frame(parent, bg="white")
        self.excel_frame.pack(fill="both", expand=True)

        subjects = self.dm.subjects
        columns = ["学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        widths = [100, 90, 90] + self._calc_subject_widths(subjects) + [80, 80]

        self.ex_tree = ttk.Treeview(
            self.excel_frame, columns=columns, show="headings", height=16
        )
        v_scroll = ttk.Scrollbar(
            self.excel_frame, orient="vertical", command=self.ex_tree.yview
        )
        h_scroll = ttk.Scrollbar(
            self.excel_frame,
            orient="horizontal",
            command=self.ex_tree.xview,
        )
        self.ex_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        for col, width in zip(columns, widths):
            self.ex_tree.heading(col, text=col)
            self.ex_tree.column(col, width=width, anchor="center")

        self._apply_zebra_stripes(self.ex_tree)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.ex_tree.pack(fill="both", expand=True)

        student_items = list(self.dm.students.items())

        if not student_items:
            for i in range(30):
                empty_vals = ["" for _ in range(len(columns))]
                tag = "odd" if i % 2 == 0 else "even"
                self.ex_tree.insert("", "end", values=empty_vals, tags=(tag,))
            self.win.update_idletasks()
            return

        try:
            sorted_items = sorted(student_items, key=lambda x: x[0])
            for idx, (sid, stu) in enumerate(sorted_items):
                st = self.dm.stats(sid)
                if st is None:
                    continue
                vals = (
                    [sid, stu["name"], stu.get("class", "")]
                    + [stu["scores"].get(s, "-") for s in subjects]
                    + [st["total"], st["avg"]]
                )
                base_tag = "odd" if idx % 2 == 0 else "even"
                self.ex_tree.insert("", "end", values=vals, tags=(base_tag,))
        except Exception as e:
            print(f"数据插入时发生错误: {e}")
            import traceback

            traceback.print_exc()

        self.win.update_idletasks()

    def _import_excel(self) -> None:
        """从 Excel 文件导入学生成绩数据.

        弹出文件选择对话框，读取用户指定的 Excel 文件，
        并将数据批量导入到系统。导入成功后自动刷新所有页面，
        更新状态栏和科目相关界面。如果刷新过程中出现非致命错误，
        会记录日志但不会影响导入结果。
        """
        if not self._check_excel_available():
            return
        excel_types = [("Excel", "*.xlsx *.xls")]
        filepath = filedialog.askopenfilename(filetypes=excel_types)
        if not filepath:
            return
        count, error = import_from_excel(filepath, self.dm)
        if error:
            logger.error("Excel 导入失败: %s - %s", filepath, error)
            show_error("导入失败", error)
        else:
            try:
                self._refresh_all_pages()
                self._update_status()
            except Exception as e:
                import traceback

                traceback.print_exc()
                logger.warning(f"导入数据后刷新界面时出现可忽略的错误: {e}")

            show_info("完成", f"成功导入 {count} 名学生")
            logger.info("Excel 导入成功: %s (%d 条)", filepath, count)

    # ========== 班级管理页面 ==========

    def _build_class_page(self, parent: tk.Frame) -> None:
        """构建班级管理页面，支持添加、删除、查看班级详情和右键菜单操作.

        Args:
            parent: 父容器 Frame，用于放置班级管理页面内容。
        """
        tk.Label(
            parent,
            text="🏫 班级管理",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=(10, 15))
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
        ttk.Button(
            btn_frame,
            text="🗑️ 删除班级",
            style="danger.TButton",
            command=self._class_delete_selected,
        ).pack(side="left", padx=4)
        columns = ["班级名称", "学生人数", "平均分", "最高分", "最低分", "操作"]
        widths = [150, 80, 80, 80, 80, 120]

        frame = tk.Frame(parent, bg="white")
        frame.pack(pady=(0, 10), fill="both", expand=True)

        self.cl_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.cl_tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.cl_tree.xview)
        self.cl_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        for col, width in zip(columns, widths):
            self.cl_tree.heading(col, text=col)
            self.cl_tree.column(col, width=width, anchor="center")

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.cl_tree.pack(fill="both", expand=True)

        self._apply_zebra_stripes(self.cl_tree)

        self.cl_tree.bind("<Double-1>", self._class_double_click)
        self.cl_tree.bind("<Button-3>", self._class_show_context_menu)

        self.cl_context_menu = tk.Menu(self.win, tearoff=0)
        self.cl_context_menu.add_command(
            label="查看详情", command=self._class_menu_show_detail
        )
        self.cl_context_menu.add_separator()
        self.cl_context_menu.add_command(
            label="删除班级", command=self._class_menu_delete, foreground="red"
        )

        self._refresh_class_tree()

    def _refresh_class_tree(self) -> None:
        """刷新班级列表表格数据，展示班级统计信息."""
        if not hasattr(self, "cl_tree") or not self.cl_tree:
            return
        self.cl_tree.delete(*self.cl_tree.get_children())

        classes = self.dm.classes

        if not classes:
            for i in range(30):
                tag = "odd" if i % 2 == 0 else "even"
                empty_vals = ["", "", "", "", "", ""]
                self.cl_tree.insert("", "end", values=empty_vals, tags=(tag,))
            return

        for idx, cls_name in enumerate(classes):
            stats = self.dm.get_class_stats(cls_name)
            base_tag = "odd" if idx % 2 == 0 else "even"
            if stats:
                self.cl_tree.insert(
                    "",
                    "end",
                    values=(
                        cls_name,
                        stats["count"],
                        stats["total_avg"],
                        stats["max_total"],
                        stats["min_total"],
                        "查看详情",
                    ),
                    tags=(base_tag,),
                )
            else:
                self.cl_tree.insert(
                    "",
                    "end",
                    values=(cls_name, 0, "-", "-", "-", "查看详情"),
                    tags=(base_tag,),
                )

    def _class_add(self) -> None:
        """添加班级."""
        name = simpledialog.askstring("添加班级", "请输入班级名称：")
        if not name:
            return
        name = name.strip()
        if not name:
            show_warning("提示", "班级名称不能为空")
            return
        try:
            self.dm.add_class(name)
            self.dm.save()
            show_info("成功", f"已创建班级「{name}」")
            self._refresh_class_tree()
        except Exception as e:
            show_error("错误", str(e))

    def _class_double_click(self, event: tk.Event) -> None:
        """班级列表双击回调."""
        row_id = self.cl_tree.identify_row(event.y)
        col_id = self.cl_tree.identify_column(event.x)
        if not row_id:
            return
        if int(col_id.replace("#", "")) == 6:
            vals = self.cl_tree.item(row_id, "values")
            self._class_show_detail(vals[0])

    def _class_show_detail(self, class_name: str) -> None:
        """显示班级详情."""
        stats = self.dm.get_class_stats(class_name)
        if not stats:
            return
        dialog = tk.Toplevel(self.win)
        dialog.title(f"班级详情 - {class_name}")
        dialog.geometry("700x500")
        self._position_dialog(dialog)
        tk.Label(dialog, text=f"🏫 {class_name}", font=FONTS["title"]).pack(
            pady=8
        )
        info_frame = tk.Frame(dialog, bg="#F0F9FF", bd=1, relief="solid")
        info_frame.pack(fill="x", padx=10, pady=5)
        info_items = [
            ("班级人数", f"{stats['count']} 人"),
            ("班级平均分", f"{stats['total_avg']:.1f} 分"),
            ("最高总分", f"{stats['max_total']:.1f} 分"),
            ("最低总分", f"{stats['min_total']:.1f} 分"),
        ]
        for label, value in info_items:
            label_widget = tk.Label(
                info_frame,
                text=f"{label}：{value}",
                font=FONTS["caption"],
                bg="#F0F9FF",
            )
            label_widget.pack(side="left", padx=15, pady=8)
        columns = ["排名", "学号", "姓名", "总分", "平均分"]
        widths = [60, 120, 100, 100, 100]
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=15)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        self._apply_zebra_stripes(tree)
        tree.tag_configure("fail", foreground=UI_COLORS["danger"])
        for idx, student in enumerate(stats["students"]):
            base_tag = "odd" if idx % 2 == 0 else "even"
            fail_tag = "fail" if student["avg"] < 60 else ""
            tags = (base_tag,)
            if fail_tag:
                tags = (base_tag, fail_tag)
            tree.insert(
                "",
                "end",
                values=(
                    student["rank"],
                    student["sid"],
                    student["name"],
                    student["total"],
                    student["avg"],
                ),
                tags=tags,
            )

    def _class_show_context_menu(self, event: tk.Event) -> None:
        """显示班级表格的右键菜单."""
        if not hasattr(self, "cl_context_menu"):
            return
        row_id = self.cl_tree.identify_row(event.y)
        if not row_id:
            return
        self.cl_tree.selection_set(row_id)
        self._selected_class_row = row_id
        self.cl_context_menu.post(event.x_root, event.y_root)

    def _class_menu_show_detail(self) -> None:
        """右键菜单：查看班级详情."""
        if hasattr(self, "_selected_class_row"):
            vals = self.cl_tree.item(self._selected_class_row, "values")
            if vals:
                self._class_show_detail(vals[0])

    def _class_menu_delete(self) -> None:
        """右键菜单：删除班级."""
        if hasattr(self, "_selected_class_row"):
            vals = self.cl_tree.item(self._selected_class_row, "values")
            if vals:
                self._class_do_delete(vals[0])

    def _class_delete_selected(self) -> None:
        """删除按钮：删除选中的班级."""
        selected = self.cl_tree.selection()
        if not selected:
            show_warning("提示", "请先选中一个班级")
            return
        vals = self.cl_tree.item(selected[0], "values")
        if not vals or not vals[0]:
            show_warning("提示", "请先选中一个班级")
            return
        self._class_do_delete(vals[0])

    def _class_do_delete(self, class_name: str) -> None:
        """执行删除班级操作（将该班级所有学生的班级字段清空）."""
        if not class_name:
            return
        if not confirm(
            "确认删除",
            f"确定要删除班级「{class_name}」吗？\n\n"
            f"该班级所有学生的班级信息将被清空，学生数据不会被删除。",
        ):
            return
        try:
            count = 0
            for student in self.dm.data["students"].values():
                if student.get("class") == class_name:
                    student["class"] = ""
                    count += 1
            # 从独立班级列表中移除
            class_list = self.dm.data.get("classes", [])
            if class_name in class_list:
                class_list.remove(class_name)
            self.dm.save()
            show_info(
                "删除成功",
                f"班级「{class_name}」已删除，共清空 {count} 名学生的班级信息",
            )
            self._refresh_class_tree()
        except Exception as e:
            show_error("错误", f"删除班级失败: {e}")

    def _build_manage_page(self, parent: tk.Frame) -> None:
        """构建成绩管理页面，支持成绩过滤、排序、删除和科目管理功能.

        Args:
            parent: 父容器 Frame，用于放置成绩管理页面内容。
        """
        tk.Label(
            parent,
            text="📁 成绩管理",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=2)

        filter_label = tk.Label(
            btn_frame,
            text="班级过滤：",
            font=FONTS["large"],
            bg="white",
        )
        filter_label.pack(side="left", padx=(10, 2))
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
        self.mg_class_cb.bind(
            "<<ComboboxSelected>>",
            lambda e: self._refresh_manage_tree(),
        )

        score_label = tk.Label(
            btn_frame,
            text="成绩范围：",
            font=FONTS["large"],
            bg="white",
        )
        score_label.pack(side="left", padx=(5, 2))
        self.mg_filter_score = tk.StringVar(value="全部")
        self.mg_score_cb = ttk.Combobox(
            btn_frame,
            textvariable=self.mg_filter_score,
            values=[
                "全部",
                "不及格 (<60)",
                "及格 (60-69)",
                "良好 (70-89)",
                "优秀 (≥90)",
            ],
            width=12,
            state="readonly",
        )
        self.mg_score_cb.pack(side="left", padx=(0, 15))
        self.mg_score_cb.bind(
            "<<ComboboxSelected>>",
            lambda e: self._refresh_manage_tree(),
        )

        ttk.Button(
            btn_frame,
            text="🗑️ 删除",
            style="danger.TButton",
            command=self._manage_delete_selected,
        ).pack(side="left", padx=4)

        ttk.Button(
            btn_frame,
            text="♻️ 重置",
            style="danger.TButton",
            command=self._reset_all_data,
        ).pack(side="left", padx=4)

        subjects = self.dm.subjects
        columns = ["学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        widths = [110, 90, 90] + self._calc_subject_widths(subjects) + [80, 80]
        self.mg_tree = self._create_treeview(parent, columns, widths, 18)
        self.mg_tree.tag_configure("fail", foreground=UI_COLORS["danger"])
        self.mg_tree.tag_configure("warn", foreground=UI_COLORS["warning"])
        self.mg_tree.tag_configure("good", foreground=UI_COLORS["success"])
        self.mg_tree.tag_configure("empty_all", foreground=UI_COLORS["placeholder"])
        self.mg_tree.bind("<Double-1>", self._manage_cell_double_click)

        self._mg_sort_asc = True
        self._mg_sort_col = ""
        for col in columns:

            def _make_sort_cmd(c):
                """创建列排序回调，避免 lambda 闭包陷阱."""
                return lambda: self._manage_sort_tree(c)

            self.mg_tree.heading(col, command=_make_sort_cmd(col))

        self._refresh_manage_tree()

    def _refresh_manage_tree(self) -> None:
        """刷新成绩管理表格，应用班级过滤、成绩范围过滤、排序和颜色预警.

        Raises:
            tk.TclError: 当表格控件已被销毁时捕获并静默返回。
        """
        try:
            if not self.mg_tree.winfo_exists():
                return
        except (tk.TclError, AttributeError):
            return

        self.mg_tree.delete(*self.mg_tree.get_children())

        filter_class = "全部班级"
        if hasattr(self, "mg_filter_class"):
            filter_class = self.mg_filter_class.get()
        filter_score = "全部"
        if hasattr(self, "mg_filter_score"):
            filter_score = self.mg_filter_score.get()

        columns = self.mg_tree["columns"]
        subject_count = len(self.dm.subjects)
        rows = []
        for sid, stu in self.dm.students.items():
            if filter_class != "全部班级" and stu.get("class", "") != filter_class:
                continue

            st = self.dm.stats(sid)
            if st is None:
                continue

            vals = (
                [sid, stu["name"], stu.get("class", "")]
                + [stu["scores"].get(s, "-") for s in self.dm.subjects]
                + [st["total"], st["avg"]]
            )

            if filter_score != "全部":
                score_vals = vals[3 : 3 + subject_count]
                pass_ok = True
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
                    except Exception as e:
                        logger.debug("成绩筛选时解析异常: %s", e)
                        pass

                if all_empty:
                    continue
                if filter_score == "不及格 (<60)" and (not pass_ok):
                    pass
                elif filter_score == "及格 (60-69)" and (pass_ok and has_60_69):
                    pass
                elif filter_score == "良好 (70-89)" and (
                    pass_ok and not has_60_69 and has_70_89
                ):
                    pass
                elif filter_score == "优秀 (≥90)" and all_ge_90:
                    pass
                else:
                    continue

            rows.append(vals)

        if not rows:
            for i in range(30):
                empty_vals = ["" for _ in range(len(columns))]
                tag = "odd" if i % 2 == 0 else "even"
                self.mg_tree.insert("", "end", values=empty_vals, tags=(tag,))
            return

        if not hasattr(self, "_mg_sort_col") or not self._mg_sort_col:
            rows.sort(key=lambda r: int(r[0]) if r[0].isdigit() else r[0])
        else:
            col_idx = columns.index(self._mg_sort_col)
            rows.sort(
                key=lambda r: self._manage_sort_key(r, col_idx),
                reverse=not self._mg_sort_asc,
            )

        for idx, vals in enumerate(rows):
            base_tag = "odd" if idx % 2 == 0 else "even"

            score_vals = vals[3 : 3 + subject_count]
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
                except Exception:
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

        total = len(self.dm.students)
        shown = len(rows)
        parts = []
        if filter_class != "全部班级":
            parts.append(filter_class)
        if filter_score != "全部":
            parts.append(filter_score)
        if parts:
            status_text = f"{' '.join(parts)}：共 {shown}/{total} 人"
            self._show_status(status_text, "info")
        else:
            self._show_status(f"全部学生共 {total} 人", "info")

    def _manage_sort_key(self, row, col_idx):
        """返回排序键值，处理数字和字符串混合情况."""
        val = row[col_idx]
        if val == "-" or val == "":
            return -1
        try:
            return float(val)
        except ValueError:
            return val

    def _manage_sort_tree(self, col: str) -> None:
        """按指定列头排序（切换升降序）."""
        if self._mg_sort_col == col:
            self._mg_sort_asc = not self._mg_sort_asc
        else:
            self._mg_sort_col = col
            self._mg_sort_asc = True
        self._refresh_manage_tree()

    def _manage_cell_double_click(self, event: tk.Event) -> None:
        """双击成绩管理表格单元格时进行行内编辑.

        Args:
            event: 鼠标双击事件对象，包含点击坐标信息。

        双击姓名或班级列会弹出输入框修改信息，
        双击成绩列会在单元格位置显示输入框直接修改成绩，
        支持回车确认、ESC 取消和失焦自动保存。
        """
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

        if col_index in (1, 2):
            prompt = f"学号 {sid}\n新值 (留空清除)："
            new_val = simpledialog.askstring(
                "修改", prompt, initialvalue=vals[col_index]
            )
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
                show_error("错误", str(e))
            return

        if 3 <= col_index < len(columns) - 2:
            subject = columns[col_index]
            x, y, w, h = self.mg_tree.bbox(row_id, col_id)
            entry = tk.Entry(self.mg_tree, font=FONTS["caption"], relief="solid")
            entry.insert(0, vals[col_index])
            entry.place(x=x, y=y, width=w, height=h)
            entry.focus_set()

            def _commit_score() -> None:
                """提交成绩编辑."""
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
                    show_error("错误", str(ex))

            entry.bind("<Return>", lambda _: _commit_score())
            entry.bind("<Escape>", lambda _: entry.destroy())
            entry.bind("<FocusOut>", lambda _: _commit_score())

    def _manage_delete_selected(self) -> None:
        """删除成绩管理表格中选中的学生记录."""
        selected = self.mg_tree.selection()
        if not selected:
            return

        selected_sids = [self.mg_tree.item(item, "values")[0] for item in selected]

        if confirm(
            "确认删除",
            f"确定要删除选中的 {len(selected_sids)} 名学生吗？",
        ):
            for sid in selected_sids:
                self.dm.del_stu(sid)
            self._refresh_manage_tree()
            self._update_status()
            self._show_status(f"已删除 {len(selected_sids)} 名学生", "ok")

    def _reset_all_data(self) -> None:
        """重置所有数据到初始状态（删除所有学生、科目、成绩)."""
        if confirm(
            "确认重置",
            "确定要删除所有数据并重置系统吗？\n"
            "此操作将删除所有学生、科目和成绩，且不可撤销！",
        ):
            # 只清空学生、科目和成绩历史，保留课程、教师、
            # 通知等基础数据
            self.dm.data["students"] = {}
            self.dm.data["subjects"] = []
            self.dm.data["history"] = []
            self.dm.save()

            self._rebuild_mg_tree()

            self._refresh_all_pages()
            self._update_status()
            self._show_status("系统已重置为初始状态", "ok")
            logger.info("所有数据已重置")


# ------------------------------------------------------------------
# 模块测试
# ------------------------------------------------------------------
