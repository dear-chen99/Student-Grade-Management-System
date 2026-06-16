"""学生界面模块 - Student App for Student Grade Management System."""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from ttkbootstrap import Window, Style

from modules.data_manager import DataManager
from src.utils.avatar_utils import load_avatar, change_avatar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(_handler)

TEAL_COLOR = "#00BFA5"
TEAL_DARK = "#00897B"


class StudentApp:
    """学生专属界面类，带左侧菜单栏和右侧动态页面."""

    def __init__(
        self,
        data_manager: DataManager | None = None,
        user_info: dict | None = None,
    ) -> None:
        """初始化学生界面.

        Args:
            data_manager: 数据管理器实例。
            user_info: 当前登录学生信息字典。
        """
        self.dm = data_manager if data_manager else DataManager()
        self.user_info = user_info or {}
        self.student_id = self.user_info.get("student_id", "")
        self.student_name = self.user_info.get("name", "学生")
        self.class_name = self.user_info.get("class", "")

        self.win = Window(themename="cosmo")
        self.win.title("学生中心 - 学生成绩管理系统")
        self.win.state("zoomed")
        self.win.minsize(1024, 768)
        self.win.configure(bg="#F3F4F6")

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

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> dict:
        """启动应用程序主循环.

        Returns:
            包含 logout 标志的字典。
        """
        self.win.mainloop()
        return {"logout": getattr(self, "_logout", False)}

    def _on_close(self) -> None:
        """窗口关闭时保存数据."""
        try:
            self.dm.save()
        except Exception as e:
            logger.warning("窗口关闭时保存数据失败: %s", e)
        self.win.destroy()

    # ========== UI 构建 ==========
    def _build_ui(self) -> None:
        """构建学生界面布局."""
        header = tk.Frame(self.win, bg=TEAL_COLOR, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text=f"学生中心 - {self.student_name}",
            font=("微软雅黑", 16, "bold"),
            fg="white",
            bg=TEAL_COLOR,
        ).pack(side="left", padx=20, pady=12)

        user_frame = tk.Frame(header, bg=TEAL_COLOR)
        user_frame.pack(side="right", padx=20, pady=12)

        tk.Label(
            user_frame,
            text=f"👤 {self.student_name}",
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

        main_container = tk.Frame(self.win, bg="#F3F4F6")
        main_container.pack(fill="both", expand=True)

        sidebar = tk.Frame(main_container, width=200, bg="#0F766E")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content_area = tk.Frame(main_container, bg="white")
        self.content_area.pack(side="right", fill="both", expand=True)

        # 侧边栏顶部头像
        avatar_frame = tk.Frame(sidebar, bg="#0F766E", height=80)
        avatar_frame.pack(fill="x", pady=(15, 5))
        avatar_frame.pack_propagate(False)
        try:
            student_data = self.dm.students.get(self.student_id, {})
            avatar_path = student_data.get("avatar", "")
            self.sidebar_avatar_label = tk.Label(avatar_frame, bg="#0F766E")
            self.sidebar_avatar_label.pack(pady=5)
            load_avatar(self.sidebar_avatar_label, avatar_path, size=(50, 50))
        except Exception:
            tk.Label(
                avatar_frame, text="👤", font=("微软雅黑", 28), bg="#0F766E", fg="white"
            ).pack(pady=5)
        tk.Label(
            avatar_frame,
            text=self.student_name,
            font=("微软雅黑", 11, "bold"),
            fg="white",
            bg="#0F766E",
        ).pack()

        # 定义页面映射
        self.page_builders = {
            "📊 仪表盘": self._build_dashboard_page,
            "个人信息": self._build_profile_page,
            "成绩查询": self._build_scores_page,
            "排名查询": self._build_ranking_page,
            "分析报告": self._build_analysis_page,
            "📢 通知公告": self._build_notices_page,
            "📅 课表查看": self._build_schedule_view_page,
        }

        self.nav_buttons = []

        # -------------- 1. 先单独放【仪表盘】（ttk.Button）--------------
        idx = 0
        text, builder = list(self.page_builders.items())[idx]

        def cmd(b=builder, btn_idx=idx):
            self._switch_page(b)
            self._set_active_button(btn_idx)

        btn = ttk.Button(sidebar, text=text, style="Sidebar.TButton", command=cmd)
        btn.pack(fill="x", padx=15, ipady=5)
        self.nav_buttons.append(btn)

        # -------------- 2. 其他菜单（tk.Label）--------------
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

        # 默认选中【仪表盘】
        self._set_active_button(0)
        self._switch_page(self._build_dashboard_page)

    def _switch_page(self, builder_func) -> None:
        """切换页面.

        Args:
            builder_func: 页面构建函数。
        """
        for widget in self.content_area.winfo_children():
            widget.destroy()
        page_frame = tk.Frame(self.content_area, bg="white")
        page_frame.pack(fill="both", expand=True, padx=10, pady=10)
        builder_func(page_frame)

    def _set_active_button(self, active_idx: int) -> None:
        """设置导航按钮选中状态.

        Args:
            active_idx: 选中按钮的索引。
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

    def _confirm_logout(self) -> None:
        """确认退出登录."""
        if messagebox.askyesno("确认退出", "确定要退出登录吗？"):
            self._logout = True
            try:
                self.dm.save()
            except Exception as e:
                logger.warning("退出登录时保存数据失败: %s", e)
            self.win.destroy()

    def _get_level(self, score: float | None) -> str:
        """根据成绩返回等级.

        Args:
            score: 成绩分数。

        Returns:
            等级字符串。
        """
        if score is None:
            return "未录入"
        if score >= 90:
            return "优秀"
        if score >= 80:
            return "良好"
        if score >= 70:
            return "中等"
        if score >= 60:
            return "及格"
        return "不及格"

    # ========== 仪表盘页面 ==========
    def _build_dashboard_page(self, parent: tk.Frame) -> None:
        """构建学生仪表盘页面."""
        self._dashboard_parent = parent
        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        """刷新仪表盘数据."""
        parent = self._dashboard_parent
        for w in parent.winfo_children():
            w.destroy()

        student = self.dm.students.get(self.student_id, {})
        scores = student.get("scores", {})
        subjects = list(scores.keys())
        st = self.dm.stats(self.student_id)

        # 获取班级排名（根据总分）
        rank = "-"
        if self.class_name:
            class_stats = self.dm.get_class_stats(self.class_name)
            if class_stats:
                for student_info in class_stats.get("students", []):
                    if student_info["sid"] == self.student_id:
                        rank = student_info["rank"]
                        break

        banner = tk.Frame(parent, bg=TEAL_COLOR, height=80)
        banner.pack(fill="x")
        tk.Label(
            banner,
            text=f"👋 欢迎回来，{self.student_name}",
            font=("微软雅黑", 18, "bold"),
            fg="white",
            bg=TEAL_COLOR,
        ).pack(pady=(12, 2))
        tk.Label(
            banner,
            text=(f"学号：{self.student_id} | " f"班级：{self.class_name or '未分配'}"),
            font=("微软雅黑", 10),
            fg="#e0f2f1",
            bg=TEAL_COLOR,
        ).pack()

        card_row = tk.Frame(parent, bg="white")
        card_row.pack(fill="x", pady=10)

        def create_card(container, icon, title, value, color):
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
                font=("微软雅黑", 10),
                fg="#6b7280",
                bg="white",
            ).pack(anchor="w", padx=10)
            tk.Label(
                card,
                text=str(value),
                font=("微软雅黑", 24, "bold"),
                fg=color,
                bg="white",
            ).pack(anchor="w", padx=10, pady=5)

        avg = round(st["avg"], 1) if st else "-"
        total = st.get("total", "-") if st else "-"
        # 格式化排名显示
        rank_display = f"第 {rank} 名" if rank != "-" else "-"

        create_card(card_row, "📚", "已修科目数", len(subjects), TEAL_COLOR)
        create_card(card_row, "📊", "平均分", avg, "#8B5CF6")
        create_card(card_row, "🏆", "班级排名", rank_display, "#10B981")
        create_card(card_row, "📝", "总分", total, "#F59E0B")

        info_frame = tk.Frame(parent, bg="#F0F9FF", bd=1, relief="solid")
        info_frame.pack(fill="x", pady=10)
        tips = (
            "💡 提示：点击左侧「成绩查询」查看各科详细成绩，"
            "「排名查询」查看班级排名情况。"
        )
        tk.Label(
            info_frame,
            text=tips,
            font=("微软雅黑", 11),
            bg="#F0F9FF",
        ).pack(pady=10)

    # ========== 个人信息页面 ==========
    def _build_profile_page(self, parent: tk.Frame) -> None:
        """构建个人信息页面，包含头像、账号、姓名、手机、邮箱."""
        tk.Label(
            parent,
            text="个人信息",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        student = self.dm.get_student(self.student_id) or {}

        # 头像区域（水平排列）
        avatar_frame = tk.Frame(parent, bg="white")
        avatar_frame.pack(pady=15)
        tk.Label(
            avatar_frame,
            text="学生头像",
            font=("微软雅黑", 11),
            bg="white",
        ).pack(side="left", padx=(0, 15))
        self.avatar_label = tk.Label(avatar_frame, bg="white")
        self.avatar_label.pack(side="left")
        self._load_avatar()
        ttk.Button(avatar_frame, text="更换头像", command=self._change_avatar).pack(
            side="left", padx=15
        )

        # 表单区域
        form_frame = tk.Frame(parent, bg="white")
        form_frame.pack(pady=10, padx=40)

        entry_opts = {"width": 35, "relief": "solid", "bd": 1, "font": ("微软雅黑", 11)}

        # 学号（只读）
        tk.Label(form_frame, text="学生账号", font=("微软雅黑", 11), bg="white").grid(
            row=0, column=0, sticky="e", pady=8, padx=10
        )
        id_entry = tk.Entry(
            form_frame, font=("微软雅黑", 11), width=35, relief="solid", bd=1
        )
        id_entry.insert(0, self.student_id)
        id_entry.config(state="readonly", readonlybackground="#F3F4F6")
        id_entry.grid(row=0, column=1, sticky="w")

        # 密码
        tk.Label(form_frame, text="学生密码", font=("微软雅黑", 11), bg="white").grid(
            row=1, column=0, sticky="e", pady=8, padx=10
        )
        pwd_frame = tk.Frame(form_frame, bg="white")
        pwd_frame.grid(row=1, column=1, sticky="w")
        pwd_var = tk.StringVar(value=student.get("password", ""))
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

        # 姓名
        tk.Label(form_frame, text="学生名称", font=("微软雅黑", 11), bg="white").grid(
            row=2, column=0, sticky="e", pady=8, padx=10
        )
        name_var = tk.StringVar(value=self.student_name)
        tk.Entry(form_frame, textvariable=name_var, **entry_opts).grid(
            row=2, column=1, sticky="w"
        )

        # 手机号
        tk.Label(form_frame, text="手机号", font=("微软雅黑", 11), bg="white").grid(
            row=3, column=0, sticky="e", pady=8, padx=10
        )
        phone_var = tk.StringVar(value=student.get("phone", ""))
        tk.Entry(form_frame, textvariable=phone_var, **entry_opts).grid(
            row=3, column=1, sticky="w"
        )

        # 邮箱
        tk.Label(form_frame, text="邮箱", font=("微软雅黑", 11), bg="white").grid(
            row=4, column=0, sticky="e", pady=8, padx=10
        )
        email_var = tk.StringVar(value=student.get("email", ""))
        tk.Entry(form_frame, textvariable=email_var, **entry_opts).grid(
            row=4, column=1, sticky="w"
        )

        def save_profile():
            new_name = name_var.get().strip()
            new_phone = phone_var.get().strip()
            new_email = email_var.get().strip()
            new_pwd = pwd_var.get().strip()
            try:
                student = self.dm.get_student(self.student_id) or {}
                self.dm.update_student(
                    self.student_id,
                    name=new_name,
                    class_name=self.class_name,
                    phone=new_phone,
                    email=new_email,
                    password=new_pwd,
                    avatar=student.get("avatar", ""),
                )
                # 强制再保存一次，确保写入
                self.dm.save()
                self.student_name = new_name
                messagebox.showinfo("成功", "个人信息已保存")
                # 刷新顶部标题
                for w in self.win.winfo_children():
                    if isinstance(w, tk.Frame) and w.winfo_children():
                        for child in w.winfo_children():
                            if isinstance(child, tk.Label) and "学生中心" in child.cget(
                                "text"
                            ):
                                child.config(text=f"学生中心 - {self.student_name}")
                                break
                        break
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{e}")

        # 保存按钮
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(
            btn_frame,
            text="保存",
            font=("微软雅黑", 11),
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=10,
            command=save_profile,
        ).pack()

    def _load_avatar(self) -> None:
        """加载学生头像（个人中心 + 侧边栏）."""
        student = self.dm.get_student(self.student_id) or {}
        avatar_path = student.get("avatar", "")
        # 更新个人中心头像
        load_avatar(self.avatar_label, avatar_path)
        # 更新侧边栏头像
        if hasattr(self, "sidebar_avatar_label"):
            load_avatar(self.sidebar_avatar_label, avatar_path, size=(50, 50))
        self.win.update_idletasks()

    def _change_avatar(self) -> None:
        """更换学生头像."""
        student = self.dm.get_student(self.student_id) or {}
        current = student.get("avatar", "")

        def save_callback(path: str) -> None:
            """保存头像路径并刷新显示."""
            print("=" * 50)
            print("保存头像路径:", path)
            try:
                self.dm.update_student(self.student_id, avatar=path)
                updated = self.dm.get_student(self.student_id)
                print("更新后学生数据:", updated)
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
                "错误", f"更换头像时发生异常：{e}\n请检查是否安装了 Pillow 库。"
            )

    def _change_password(self) -> None:
        """修改个人密码."""
        top = tk.Toplevel(self.win)
        top.title("修改密码")
        top.geometry("300x180")
        top.resizable(False, False)
        top.transient(self.win)
        top.grab_set()

        win_x = self.win.winfo_x() + 60
        win_y = self.win.winfo_y() + 120
        top.geometry(f"+{win_x}+{win_y}")

        tk.Label(top, text="原密码：").pack(pady=(10, 0))
        old_entry = ttk.Entry(top, show="*")
        old_entry.pack()

        tk.Label(top, text="新密码：").pack()
        new_entry = ttk.Entry(top, show="*")
        new_entry.pack()

        def do_change():
            old = old_entry.get().strip()
            new_pwd = new_entry.get().strip()
            if not old or not new_pwd:
                messagebox.showwarning("提示", "密码不能为空", parent=top)
                return
            student = self.dm.get_student(self.student_id)
            if not student or student.get("password") != old:
                messagebox.showerror("错误", "原密码不正确", parent=top)
                return
            self.dm.data["students"][self.student_id]["password"] = new_pwd
            self.dm.save()
            messagebox.showinfo("成功", "密码修改成功", parent=top)
            top.destroy()

        ttk.Button(top, text="确认修改", command=do_change).pack(pady=10)

    # ========== 成绩查询页面 ==========
    def _build_scores_page(self, parent: tk.Frame) -> None:
        """构建成绩查询页面.

        Args:
            parent: 父容器。
        """
        tk.Label(
            parent,
            text="成绩查询",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        stats = self.dm.stats(self.student_id)

        table_frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ["科目", "成绩", "等级"]
        widths = [200, 120, 120]
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        level_tags = {
            "优秀": ("#D1FAE5", "#10B981"),
            "良好": ("#DBEAFE", "#3B82F6"),
            "中等": ("#FEF9C3", "#F59E0B"),
            "及格": ("#FEF9C3", "#F59E0B"),
            "不及格": ("#FEE2E2", "#EF4444"),
            "未录入": ("#F3F4F6", "#9CA3AF"),
        }
        for tag, (bg, fg) in level_tags.items():
            tree.tag_configure(tag, background=bg, foreground=fg)

        score_values = []
        if stats:
            scores = stats.get("scores", {})
            for idx, (subject, score) in enumerate(scores.items()):
                level = self._get_level(score)
                display = str(score) if score is not None else "—"
                tree.insert("", "end", values=(subject, display, level), tags=(level,))
                if score is not None:
                    score_values.append(score)

        # 统计摘要
        summary_frame = tk.Frame(parent, bg="white")
        summary_frame.pack(pady=10, fill="x")

        total = round(sum(score_values), 2) if score_values else 0.0
        avg = round(total / len(score_values), 2) if score_values else 0.0
        high = max(score_values) if score_values else 0.0
        low = min(score_values) if score_values else 0.0

        summary_items = [
            ("总分", str(total)),
            ("平均分", str(avg)),
            ("最高分", str(high)),
            ("最低分", str(low)),
            ("科目数", str(len(score_values))),
        ]
        for label, value in summary_items:
            card = tk.Frame(summary_frame, bg="#F0F9FF", bd=1, relief="solid")
            card.pack(side="left", expand=True, fill="both", padx=5)
            tk.Label(
                card,
                text=label,
                font=("微软雅黑", 10),
                bg="#F0F9FF",
                fg="#64748B",
            ).pack(pady=(5, 0))
            tk.Label(
                card,
                text=value,
                font=("微软雅黑", 14, "bold"),
                bg="#F0F9FF",
                fg="#0F766E",
            ).pack(pady=(0, 5))

    # ========== 排名查询页面 ==========
    def _build_ranking_page(self, parent: tk.Frame) -> None:
        """构建排名查询页面.

        Args:
            parent: 父容器。
        """
        tk.Label(
            parent,
            text="排名查询",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        stats = self.dm.stats(self.student_id)
        if not stats:
            tk.Label(
                parent,
                text="暂无成绩数据",
                font=("微软雅黑", 12),
                bg="white",
            ).pack(pady=20)
            return

        subjects = list(stats.get("scores", {}).keys())

        ctrl_frame = tk.Frame(parent, bg="white")
        ctrl_frame.pack(pady=5)
        tk.Label(
            ctrl_frame,
            text="选择科目：",
            font=("微软雅黑", 11),
            bg="white",
        ).pack(side="left")
        subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=subject_var,
            values=subjects,
            state="readonly",
            width=20,
        )
        subject_combo.pack(side="left", padx=5)

        container = tk.Frame(parent, bg="white")
        container.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(container, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=5)
        right_frame = tk.Frame(container, bg="white")
        right_frame.pack(side="right", fill="both", expand=True, padx=5)

        tk.Label(
            left_frame,
            text="单科班级排名",
            font=("微软雅黑", 12, "bold"),
            bg="white",
            fg="#0F766E",
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            right_frame,
            text="总分班级排名",
            font=("微软雅黑", 12, "bold"),
            bg="white",
            fg="#0F766E",
        ).pack(anchor="w", pady=(0, 5))

        sub_tree = ttk.Treeview(
            left_frame,
            columns=["排名", "学号", "姓名", "成绩"],
            show="headings",
            height=15,
        )
        for col, width in zip(["排名", "学号", "姓名", "成绩"], [60, 120, 100, 80]):
            sub_tree.heading(col, text=col)
            sub_tree.column(col, width=width, anchor="center")
        sub_tree.pack(fill="both", expand=True)
        sub_tree.tag_configure("me", background="#DBEAFE")

        total_tree = ttk.Treeview(
            right_frame,
            columns=["排名", "学号", "姓名", "总分", "平均分"],
            show="headings",
            height=15,
        )
        for col, width in zip(
            ["排名", "学号", "姓名", "总分", "平均分"],
            [60, 120, 100, 80, 80],
        ):
            total_tree.heading(col, text=col)
            total_tree.column(col, width=width, anchor="center")
        total_tree.pack(fill="both", expand=True)
        total_tree.tag_configure("me", background="#DBEAFE")

        def refresh_subject_rank(*_):
            sub = subject_var.get()
            if not sub:
                return
            sub_rankings = self.dm.ranking(by="subject", subject=sub)
            for item in sub_tree.get_children():
                sub_tree.delete(item)
            for idx, r in enumerate(sub_rankings):
                tag = (
                    "me"
                    if r["id"] == self.student_id
                    else ("odd" if idx % 2 == 0 else "even")
                )
                score_val = r["scores"].get(sub)
                display = str(score_val) if score_val is not None else "—"
                sub_tree.insert(
                    "",
                    "end",
                    values=(r["rank"], r["id"], r["name"], display),
                    tags=(tag,),
                )

        subject_var.trace_add("write", refresh_subject_rank)
        if subjects:
            subject_combo.set(subjects[0])

        # 总分排名（班级）
        if self.class_name:
            class_stats = self.dm.get_class_stats(self.class_name)
            if class_stats:
                for s in class_stats.get("students", []):
                    tag = "me" if s["sid"] == self.student_id else ""
                    total_tree.insert(
                        "",
                        "end",
                        values=(
                            s["rank"],
                            s["sid"],
                            s["name"],
                            s["total"],
                            s["avg"],
                        ),
                        tags=(tag,),
                    )

    # ========== 分析报告页面 ==========
    def _build_analysis_page(self, parent: tk.Frame) -> None:
        """构建成绩分析报告页面.

        Args:
            parent: 父容器。
        """
        tk.Label(
            parent,
            text="成绩分析报告",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        stats = self.dm.stats(self.student_id)
        if not stats:
            tk.Label(
                parent,
                text="暂无成绩数据",
                font=("微软雅黑", 12),
                bg="white",
            ).pack(pady=20)
            return

        scores = stats.get("scores", {})
        total = stats["total"]
        avg = stats["avg"]

        # 总体评价
        eval_frame = tk.Frame(parent, bg="#F0F9FF", bd=1, relief="solid")
        eval_frame.pack(fill="x", padx=10, pady=10)
        if avg >= 90:
            eval_text = "表现优异，继续保持！"
            eval_color = "#10B981"
        elif avg >= 80:
            eval_text = "成绩良好，还有提升空间！"
            eval_color = "#3B82F6"
        elif avg >= 70:
            eval_text = "成绩中等，需要更加努力！"
            eval_color = "#F59E0B"
        elif avg >= 60:
            eval_text = "成绩及格，请加强学习！"
            eval_color = "#F97316"
        else:
            eval_text = "成绩不及格，请尽快补习！"
            eval_color = "#EF4444"
        tk.Label(
            eval_frame,
            text=eval_text,
            font=("微软雅黑", 14, "bold"),
            fg=eval_color,
            bg="#F0F9FF",
        ).pack(pady=10)

        # 成绩预警
        warning_frame = tk.Frame(parent, bg="white")
        warning_frame.pack(fill="x", padx=10, pady=5)
        fail_subjects = [
            sub for sub, sc in scores.items() if sc is not None and sc < 60
        ]
        if fail_subjects:
            warn_label = tk.Label(
                warning_frame,
                text=f"成绩预警：{', '.join(fail_subjects)} 不及格，"
                "请重点复习并准备补考！",
                font=("微软雅黑", 11, "bold"),
                fg="#EF4444",
                bg="#FEE2E2",
            )
            warn_label.pack(fill="x", padx=10, pady=5)
        else:
            tk.Label(
                warning_frame,
                text="暂无成绩预警，继续保持！",
                font=("微软雅黑", 11),
                fg="#10B981",
                bg="white",
            ).pack(anchor="w")

        # 详细分析
        detail_frame = tk.Frame(parent, bg="white")
        detail_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scored = {k: v for k, v in scores.items() if v is not None}
        high_sub = max(scored, key=scored.get) if scored else "—"
        low_sub = min(scored, key=scored.get) if scored else "—"
        high_score = scored.get(high_sub, "—") if scored else "—"
        low_score = scored.get(low_sub, "—") if scored else "—"

        # 班级平均对比
        class_avg_text = "暂无班级数据"
        if self.class_name:
            class_stats = self.dm.get_class_stats(self.class_name)
            if class_stats:
                class_avg = class_stats.get("avg", 0)
                diff = round(avg - class_avg, 2)
                if diff >= 0:
                    class_avg_text = f"高于班级平均分 {diff} 分"
                else:
                    class_avg_text = f"低于班级平均分 {abs(diff)} 分"

        # 学习建议
        suggestions = []
        if avg >= 90:
            suggestions.append("整体表现非常出色，建议保持当前学习节奏。")
        elif avg >= 80:
            suggestions.append("整体成绩良好，可在薄弱科目上适当投入更多时间。")
        elif avg >= 70:
            suggestions.append("整体成绩中等，建议制定系统复习计划。")
        elif avg >= 60:
            suggestions.append("整体成绩刚及格，建议查漏补缺，夯实基础。")
        else:
            suggestions.append("整体成绩不及格，建议寻求老师帮助，制定专项补习计划。")

        if fail_subjects:
            suggestions.append(f"重点加强：{', '.join(fail_subjects)}。")
        if scored:
            best = max(scored, key=scored.get)
            suggestions.append(f"优势科目：{best}，可继续保持。")

        report_lines = [
            f"学生：{self.student_name}（{self.student_id}）",
            f"班级：{self.class_name or '未分配'}",
            "",
            f"总分：{total}",
            f"平均分：{avg}",
            f"最高分科目：{high_sub}（{high_score}）",
            f"最低分科目：{low_sub}（{low_score}）",
            f"与班级平均对比：{class_avg_text}",
            "",
            "学习建议：",
        ] + [f"  {i+1}. {s}" for i, s in enumerate(suggestions)]

        report_text = "\n".join(report_lines)

        text_widget = tk.Text(
            detail_frame,
            font=("微软雅黑", 11),
            bg="white",
            wrap="word",
            padx=10,
            pady=10,
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", report_text)
        text_widget.config(state="disabled")

        # 导出按钮
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=10)
        ttk.Button(
            btn_frame,
            text="导出报告为TXT",
            style="info.TButton",
            command=lambda: self._export_report(report_text),
        ).pack(side="left", padx=5)

    def _export_report(self, report_text: str) -> None:
        """导出分析报告为TXT文件.

        Args:
            report_text: 报告文本内容。
        """
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")],
            initialfile=f"成绩分析报告_{self.student_name}.txt",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report_text)
                messagebox.showinfo("成功", f"报告已保存到：{path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{e}")

    # ========== 通知公告页面 ==========
    def _build_notices_page(self, parent):
        """构建通知公告页面（只读列表）."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="📢 通知公告", font=("微软雅黑", 16, "bold"), bg="white"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 获取通知列表（student 角色）
        notices = (
            self.dm.get_notices(role="student")
            if hasattr(self.dm, "get_notices")
            else []
        )

        if not notices:
            tk.Label(
                parent,
                text="暂无通知公告",
                font=("微软雅黑", 12),
                bg="white",
                fg="#888888",
            ).pack(pady=20)
            return

        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ["标题", "发布者", "日期", "接收对象"]
        self._student_notice_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=18
        )
        widths = [250, 100, 120, 100]
        for col, width in zip(columns, widths):
            self._student_notice_tree.heading(col, text=col)
            self._student_notice_tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self._student_notice_tree.yview
        )
        self._student_notice_tree.configure(yscrollcommand=vsb.set)

        self._student_notice_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for notice in notices:
            self._student_notice_tree.insert(
                "",
                "end",
                values=(
                    notice.get("title", ""),
                    notice.get("publisher", ""),
                    notice.get("date", ""),
                    notice.get("target", "all"),
                ),
            )

        def _on_double_click(event):
            selection = self._student_notice_tree.selection()
            if not selection:
                return
            values = self._student_notice_tree.item(selection[0], "values")
            title = values[0]

            for n in notices:
                if n.get("title") == title:
                    dialog = tk.Toplevel(self.win)
                    dialog.title(f"通知详情 - {title}")
                    dialog.geometry("500x400")
                    dialog.transient(self.win)

                    tk.Label(
                        dialog, text=title, font=("微软雅黑", 14, "bold"), bg="white"
                    ).pack(anchor="w", padx=20, pady=(20, 10))

                    info = f"发布者：{n.get('publisher', '')}  |  日期：{n.get('date', '')}"
                    tk.Label(
                        dialog,
                        text=info,
                        font=("微软雅黑", 10),
                        bg="white",
                        fg="#666666",
                    ).pack(anchor="w", padx=20, pady=(0, 15))

                    content_text = tk.Text(dialog, font=("微软雅黑", 11), wrap="word")
                    content_text.insert("1.0", n.get("content", ""))
                    content_text.config(state="disabled")
                    content_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                    break

        self._student_notice_tree.bind("<Double-1>", _on_double_click)

    # ------------------------------------------------------------------
    # 课表查看（只读）
    # ------------------------------------------------------------------

    def _build_schedule_view_page(self, parent):
        """构建课表查看页面（只读）."""
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

        tk.Button(
            header_frame,
            text="📜 查看历史",
            font=("微软雅黑", 11),
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
            font=("微软雅黑", 11),
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
        self._schedule_view_tree.tag_configure("oddrow", background="#F8FAFC")
        self._schedule_view_tree.tag_configure("evenrow", background="#FFFFFF")

        # 加载数据
        self._refresh_schedule_tree()

    def _refresh_schedule_tree(self):
        """刷新课表Treeview."""
        tree = getattr(self, "_schedule_view_tree", None)
        if tree is None:
            return
        for item in tree.get_children():
            tree.delete(item)

        schedules = self.dm.get_schedules()
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

    def _schedule_show_history(self):
        """查看课表变更历史."""
        history_win = tk.Toplevel(self.win)
        history_win.title("课表变更历史")
        history_win.geometry("750x450")
        history_win.transient(self.win)

        tk.Label(
            history_win,
            text="📜 课表变更历史",
            font=("微软雅黑", 14, "bold"),
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
        tree.tag_configure("oddrow", background="#F8FAFC")
        tree.tag_configure("evenrow", background="#FFFFFF")

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
