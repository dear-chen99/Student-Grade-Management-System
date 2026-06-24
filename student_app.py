"""学生界面模块 - Student App for Student Grade Management System.

本模块实现了学生专属界面，提供仪表盘、个人信息管理、成绩查询、
排名查询、成绩分析报告、通知公告以及课表查看等功能。界面采用
左侧导航栏 + 右侧动态内容区的布局，基于 tkinter 与 ttkbootstrap
构建。

主要组件:
    StudentApp: 学生应用主类，负责界面初始化、页面切换与数据展示。
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from ttkbootstrap import Window, Style

from modules.data_manager import DataManager
from src.config import UI_COLORS, FONTS, DIALOG_SIZES
from src.utils.avatar_utils import load_avatar, change_avatar
from src.utils.base_app import BaseApp, TEAL_COLOR, TEAL_DARK
from src.utils.ui_utils import (
    create_dialog,
    show_info,
    show_warning,
    show_error,
    confirm,
    validate_password,
)

class StudentApp(BaseApp):
    """学生专属界面类，带左侧菜单栏和右侧动态页面.

    本类封装了学生端所有 UI 的构建与交互逻辑，包括：
    - 初始化主窗口并配置全局样式；
    - 构建顶部标题栏、左侧导航栏及右侧内容区；
    - 提供多个功能页面的动态切换（仪表盘、个人信息、成绩查询等）；
    - 处理数据查询、头像更换、密码修改及报告导出等业务操作。

    Attributes:
        dm (DataManager): 数据管理器实例，负责学生数据与成绩的增删改查。
        user_info (dict): 当前登录学生的用户信息字典。
        student_id (str): 当前学生学号。
        student_name (str): 当前学生姓名。
        class_name (str): 当前学生所在班级名称。
        win (Window): ttkbootstrap 主窗口实例。
        content_area (tk.Frame): 右侧内容展示区域。
        page_builders (dict): 页面名称到构建函数的映射。
        nav_buttons (list): 导航按钮/标签控件列表，用于管理选中状态。
    """

    def __init__(
        self,
        data_manager: DataManager | None = None,
        user_info: dict | None = None,
    ) -> None:
        """初始化学生界面.

        创建主窗口、初始化数据管理器、加载用户信息，并配置全局样式与 UI 布局。

        Args:
            data_manager: 数据管理器实例。若为 None，则自动创建新实例。
            user_info: 当前登录学生信息字典，包含 student_id、name、class 等字段。
        """
        super().__init__(data_manager=data_manager, user_info=user_info)
        self.student_id = self.user_info.get("student_id", "")
        self.student_name = self.user_info.get("name", "学生")
        self.class_name = self.user_info.get("class", "")

        # 页面映射
        self.page_builders = {
            "📊 仪表盘": self._build_dashboard_page,
            "个人信息": self._build_profile_page,
            "成绩查询": self._build_scores_page,
            "排名查询": self._build_ranking_page,
            "分析报告": self._build_analysis_page,
            "📢 通知公告": self._build_notices_page,
            "📅 课表查看": self._build_schedule_view_page,
        }

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_window_title(self) -> str:
        """返回主窗口标题."""
        return "学生中心 - 学生成绩管理系统"

    def _get_header_title(self) -> str:
        """返回顶部横幅标题文本."""
        return f"学生中心 - {self.student_name}"

    def _get_user_display_name(self) -> str:
        """返回右上角显示的用户名称."""
        return self.student_name

    def _get_avatar_data(self) -> dict:
        """返回学生头像数据."""
        student = self.dm.students.get(self.student_id, {})
        return {
            "name": self.student_name,
            "avatar": student.get("avatar", ""),
        }

    def _save_avatar(self, path: str) -> None:
        """保存学生头像路径."""
        self.dm.update_student(self.student_id, avatar=path)

    # ----- 个人中心钩子实现 -----

    def _get_profile_page_title(self) -> str:
        return "个人信息"

    def _get_avatar_label_text(self) -> str:
        return "学生头像"

    def _get_profile_id_label(self) -> str:
        return "学生账号"

    def _get_profile_id_value(self) -> str:
        return self.student_id

    def _get_profile_pwd_label(self) -> str:
        return "学生密码"

    def _get_profile_name_label(self) -> str:
        return "学生名称"

    def _get_profile_name_value(self) -> str:
        return self.student_name

    def _get_profile_data(self) -> dict:
        student = self.dm.get_student(self.student_id) or {}
        return {
            "password": student.get("password", ""),
            "phone": student.get("phone", ""),
            "email": student.get("email", ""),
        }

    def _save_profile_entity(
        self, name: str, phone: str, email: str, password: str
    ) -> None:
        student = self.dm.get_student(self.student_id) or {}
        self.dm.update_student(
            self.student_id,
            name=name,
            class_name=self.class_name,
            phone=phone,
            email=email,
            password=password,
            avatar=student.get("avatar", ""),
        )
        # 强制再保存一次，确保写入持久化存储
        self.dm.save()

    def _on_profile_saved(self, name: str) -> None:
        self.student_name = name
        self._update_header_title_text("学生中心", f"学生中心 - {self.student_name}")

    def _get_current_password(self) -> str:
        student = self.dm.get_student(self.student_id) or {}
        return student.get("password", "")

    def _update_password(self, new_password: str) -> None:
        self.dm.update_student(self.student_id, password=new_password)

    def _get_notice_role(self) -> str:
        return "student"

    def _get_schedule_class_name(self) -> str:
        """返回学生所在班级名称（固定值，无选择器）."""
        return self.class_name

    def _get_level(self, score: float | None) -> str:
        """根据成绩分数返回对应等级.

        等级划分标准：
        - 优秀：>= 90
        - 良好：>= 80
        - 中等：>= 70
        - 及格：>= 60
        - 不及格：< 60
        - 未录入：score 为 None

        Args:
            score: 成绩分数，可能为 None。

        Returns:
            等级字符串，如 "优秀"、"及格"、"未录入" 等。
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
        """构建学生仪表盘页面.

        仪表盘展示欢迎横幅、统计卡片及操作提示。

        Args:
            parent: 页面父容器 Frame。
        """
        self._dashboard_parent = parent
        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        """刷新仪表盘数据与 UI.

        重新从数据管理器获取学生成绩、统计信息及班级排名，
        并渲染欢迎横幅、统计卡片与提示信息。
        """
        parent = self._dashboard_parent
        for w in parent.winfo_children():
            w.destroy()

        # 获取当前学生数据与成绩统计
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

        # ---------- 欢迎横幅 ----------
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
            font=FONTS["caption"],
            fg="#e0f2f1",
            bg=TEAL_COLOR,
        ).pack()

        # ---------- 统计卡片行 ----------
        card_row = tk.Frame(parent, bg="white")
        card_row.pack(fill="x", pady=10)

        # 计算并格式化统计数值
        avg = round(st["avg"], 1) if st else "-"
        total = st.get("total", "-") if st else "-"
        rank_display = f"第 {rank} 名" if rank != "-" else "-"

        # 创建四个统计卡片：科目数、平均分、班级排名、总分
        self._create_dashboard_card(card_row, "📚", "已修科目数", len(subjects), TEAL_COLOR)
        self._create_dashboard_card(card_row, "📊", "平均分", avg, "#8B5CF6")
        self._create_dashboard_card(card_row, "🏆", "班级排名", rank_display, UI_COLORS["success"])
        self._create_dashboard_card(card_row, "📝", "总分", total, UI_COLORS["warning"])

        # ---------- 操作提示栏 ----------
        info_frame = tk.Frame(parent, bg="#F0F9FF", bd=1, relief="solid")
        info_frame.pack(fill="x", pady=10)
        tips = (
            "💡 提示：点击左侧「成绩查询」查看各科详细成绩，"
            "「排名查询」查看班级排名情况。"
        )
        tk.Label(
            info_frame,
            text=tips,
            font=FONTS["body"],
            bg="#F0F9FF",
        ).pack(pady=10)


    # ========== 成绩查询页面 ==========
    def _build_scores_page(self, parent: tk.Frame) -> None:
        """构建成绩查询页面.

        以 Treeview 表格展示各科成绩与等级，并在底部显示统计摘要。

        Args:
            parent: 页面父容器 Frame。
        """
        tk.Label(
            parent,
            text="成绩查询",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        stats = self.dm.stats(self.student_id)

        # 成绩表格容器
        table_frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ["科目", "成绩", "等级"]
        widths = [200, 120, 120]
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        # 配置各等级对应的背景色与前景色标签
        level_tags = {
            "优秀": (UI_COLORS["success_light"], UI_COLORS["success"]),
            "良好": (UI_COLORS["info_light"], "#3B82F6"),
            "中等": (UI_COLORS["warn_light"], UI_COLORS["warning"]),
            "及格": (UI_COLORS["warn_light"], UI_COLORS["warning"]),
            "不及格": (UI_COLORS["danger_light"], UI_COLORS["danger"]),
            "未录入": (UI_COLORS["page_bg"], UI_COLORS["placeholder"]),
        }
        for tag, (bg, fg) in level_tags.items():
            tree.tag_configure(tag, background=bg, foreground=fg)

        # 遍历成绩数据并插入表格
        score_values = []
        if stats:
            scores = stats.get("scores", {})
            for idx, (subject, score) in enumerate(scores.items()):
                level = self._get_level(score)
                display = str(score) if score is not None else "—"
                tree.insert("", "end", values=(subject, display, level), tags=(level,))
                if score is not None:
                    score_values.append(score)

        # ---------- 统计摘要 ----------
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
                font=FONTS["caption"],
                bg="#F0F9FF",
                fg="#64748B",
            ).pack(pady=(5, 0))
            tk.Label(
                card,
                text=value,
                font=FONTS["title"],
                bg="#F0F9FF",
                fg=UI_COLORS["sidebar_bg"],
            ).pack(pady=(0, 5))

    # ========== 排名查询页面 ==========
    def _build_ranking_page(self, parent: tk.Frame) -> None:
        """构建排名查询页面.

        左侧展示单科班级排名，右侧展示总分班级排名。支持科目筛选。

        Args:
            parent: 页面父容器 Frame。
        """
        tk.Label(
            parent,
            text="排名查询",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        stats = self.dm.stats(self.student_id)
        if not stats:
            tk.Label(
                parent,
                text="暂无成绩数据",
                font=FONTS["normal"],
                bg="white",
            ).pack(pady=20)
            return

        subjects = list(stats.get("scores", {}).keys())

        # 科目选择控件
        ctrl_frame = tk.Frame(parent, bg="white")
        ctrl_frame.pack(pady=5)
        tk.Label(
            ctrl_frame,
            text="选择科目：",
            font=FONTS["body"],
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

        # 左右分栏容器
        container = tk.Frame(parent, bg="white")
        container.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(container, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=5)
        right_frame = tk.Frame(container, bg="white")
        right_frame.pack(side="right", fill="both", expand=True, padx=5)

        tk.Label(
            left_frame,
            text="单科班级排名",
            font=FONTS["normal_bold"],
            bg="white",
            fg=UI_COLORS["sidebar_bg"],
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            right_frame,
            text="总分班级排名",
            font=FONTS["normal_bold"],
            bg="white",
            fg=UI_COLORS["sidebar_bg"],
        ).pack(anchor="w", pady=(0, 5))

        # 单科排名 Treeview
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
        sub_tree.tag_configure("me", background=UI_COLORS["info_light"])

        # 总分排名 Treeview
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
        total_tree.tag_configure("me", background=UI_COLORS["info_light"])

        def refresh_subject_rank(*_):
            """刷新单科排名 Treeview.

            根据选中的科目从数据管理器获取排名列表，并高亮当前学生所在行。
            """
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

        # 绑定科目选择变动事件，自动刷新排名
        subject_var.trace_add("write", refresh_subject_rank)
        if subjects:
            subject_combo.set(subjects[0])

        # 加载总分排名（班级）
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

        生成包含总体评价、成绩预警、详细分析数据与学习建议的报告，
        并支持导出为 TXT 文件。

        Args:
            parent: 页面父容器 Frame。
        """
        tk.Label(
            parent,
            text="成绩分析报告",
            font=FONTS["title"],
            bg="white",
        ).pack(pady=4)

        stats = self.dm.stats(self.student_id)
        if not stats:
            tk.Label(
                parent,
                text="暂无成绩数据",
                font=FONTS["normal"],
                bg="white",
            ).pack(pady=20)
            return

        scores = stats.get("scores", {})
        total = stats["total"]
        avg = stats["avg"]

        # ---------- 总体评价 ----------
        eval_frame = tk.Frame(parent, bg="#F0F9FF", bd=1, relief="solid")
        eval_frame.pack(fill="x", padx=10, pady=10)
        # 根据平均分区间生成不同评价文本与颜色
        if avg >= 90:
            eval_text = "表现优异，继续保持！"
            eval_color = UI_COLORS["success"]
        elif avg >= 80:
            eval_text = "成绩良好，还有提升空间！"
            eval_color = "#3B82F6"
        elif avg >= 70:
            eval_text = "成绩中等，需要更加努力！"
            eval_color = UI_COLORS["warning"]
        elif avg >= 60:
            eval_text = "成绩及格，请加强学习！"
            eval_color = "#F97316"
        else:
            eval_text = "成绩不及格，请尽快补习！"
            eval_color = UI_COLORS["danger"]
        eval_label = tk.Label(
            eval_frame,
            text=eval_text,
            font=FONTS["title"],
            bg="#F0F9FF",
        )
        eval_label.pack(pady=10)
        eval_label.configure(fg=eval_color)

        # ---------- 成绩预警 ----------
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
                font=FONTS["body_bold"],
                bg=UI_COLORS["danger_light"],
            )
            warn_label.pack(fill="x", padx=10, pady=5)
            warn_label.configure(fg=UI_COLORS["danger"])
        else:
            safe_label = tk.Label(
                warning_frame,
                text="暂无成绩预警，继续保持！",
                font=FONTS["body"],
                bg="white",
            )
            safe_label.pack(anchor="w")
            safe_label.configure(fg=UI_COLORS["success"])

        # ---------- 详细分析 ----------
        detail_frame = tk.Frame(parent, bg="white")
        detail_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 筛选出已录入成绩的科目，计算最高/最低分科目
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

        # ---------- 学习建议 ----------
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

        # 组装报告文本
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
            font=FONTS["body"],
            bg="white",
            wrap="word",
            padx=10,
            pady=10,
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", report_text)
        text_widget.config(state="disabled")

        # ---------- 导出按钮 ----------
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=10)
        ttk.Button(
            btn_frame,
            text="导出报告为TXT",
            style="info.TButton",
            command=lambda: self._export_report(report_text),
        ).pack(side="left", padx=5)

    def _export_report(self, report_text: str) -> None:
        """导出分析报告为 TXT 文件.

        弹出保存对话框，用户确认后将报告内容写入指定路径。

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
                show_info("成功", f"报告已保存到：{path}")
            except Exception as e:
                show_error("错误", f"保存失败：{e}")


    # ------------------------------------------------------------------
    # 课表查看（只读）
    # ------------------------------------------------------------------

    def _schedule_show_history(self):
        """查看课表变更历史（仅显示本班记录）.

        弹出 Toplevel 窗口，以 Treeview 展示本班课表的历史操作记录（增删改）。
        """
        history_win = tk.Toplevel(self.win)
        history_win.title(f"课表变更历史 - {self.class_name or '本班'}")
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

        # 仅获取本班的历史记录
        history = self.dm.get_schedule_history(
            class_names={self.class_name} if self.class_name else None
        )
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
