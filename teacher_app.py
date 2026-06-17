"""教师界面模块 - Teacher App for Student Grade Management System."""

import logging
import os
import csv
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from ttkbootstrap import Window, Style

from modules.data_manager import DataManager
from src.utils.avatar_utils import load_avatar, change_avatar
from src.utils.excel_handler import (
    is_excel_available,
    create_template,
    import_from_excel,
    export_to_excel,
    get_default_filename as get_excel_filename,
)
from src.utils.export import export_to_csv, get_default_filename as get_csv_filename

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(_handler)

# Excel 库可用性
EX_OK: bool = is_excel_available()

# 尝试导入 matplotlib 用于图表展示
try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np

    if os.sys.platform.startswith("win"):
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    elif os.sys.platform.startswith("darwin"):
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
    MAT_OK = False

TEAL_COLOR = "#00BFA5"
TEAL_DARK = "#00897B"


class TeacherApp:
    """教师专属界面类，带左侧菜单栏和右侧动态页面"""

    def __init__(
        self,
        data_manager: DataManager | None = None,
        user_info: dict | None = None,
    ) -> None:
        """初始化实例，配置数据管理器和用户信息."""
        self.dm = data_manager if data_manager else DataManager()
        self.user_info = user_info or {}
        self.teacher_id = self.user_info.get("teacher_id", "")
        self.teacher_name = self.user_info.get("name", "教师")
        self._logout_flag = False  # 退出登录标志

        self.win = Window(themename="cosmo")
        self.win.title("教师工作台 - 学生成绩管理系统")
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
        """启动应用程序主循环，返回退出登录标志."""
        self.win.mainloop()
        return {"logout": getattr(self, "_logout_flag", False)}

    def _on_close(self) -> None:
        """窗口关闭事件处理，保存数据并退出."""
        try:
            self.dm.save()
        except Exception as e:
            logger.warning("窗口关闭时保存数据失败: %s", e)
        self.win.destroy()

    def _logout(self) -> None:
        """退出登录，返回登录界面."""
        if messagebox.askyesno("确认退出", "确定要退出登录吗？"):
            self._logout_flag = True
            try:
                self.dm.save()
            except Exception as e:
                logger.warning("退出登录时保存数据失败: %s", e)
            self.win.destroy()

    # ========== UI 构建 ==========
    def _build_ui(self) -> None:
        # 顶部横幅
        """构建主界面布局和侧边栏导航."""
        header = tk.Frame(self.win, bg=TEAL_COLOR, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text=f"👨‍🏫 教师工作台 - {self.teacher_name}",
            font=("微软雅黑", 16, "bold"),
            fg="white",
            bg=TEAL_COLOR,
        ).pack(side="left", padx=20, pady=12)

        user_frame = tk.Frame(header, bg=TEAL_COLOR)
        user_frame.pack(side="right", padx=20, pady=12)

        tk.Label(
            user_frame,
            text=f"👤 {self.teacher_name}",
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
            command=self._logout,
            padx=12,
            pady=4,
        ).pack(side="left")

        main_container = tk.Frame(self.win, bg="#F3F4F6")
        main_container.pack(fill="both", expand=True)

        # 左侧侧边栏菜单
        sidebar = tk.Frame(main_container, width=200, bg="#0F766E")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # 侧边栏顶部头像
        avatar_frame = tk.Frame(sidebar, bg="#0F766E", height=80)
        avatar_frame.pack(fill="x", pady=(15, 5))
        avatar_frame.pack_propagate(False)
        try:
            teacher_data = self.dm.get_teacher(self.teacher_id) or {}
            avatar_path = teacher_data.get("avatar", "")
            from src.utils.avatar_utils import load_avatar

            self.sidebar_avatar_label = tk.Label(avatar_frame, bg="#0F766E")
            self.sidebar_avatar_label.pack(pady=5)
            load_avatar(self.sidebar_avatar_label, avatar_path, size=(50, 50))
        except Exception:
            tk.Label(
                avatar_frame, text="👤", font=("微软雅黑", 28), bg="#0F766E", fg="white"
            ).pack(pady=5)
        tk.Label(
            avatar_frame,
            text=self.teacher_name,
            font=("微软雅黑", 11, "bold"),
            fg="white",
            bg="#0F766E",
        ).pack()

        # 定义页面映射
        self.page_builders = {
            "仪表盘": self._build_dashboard_page,
            "🏫 班级": self._build_class_page,
            "🔍 查询": self._build_search_page,
            "📈 图表": self._build_chart_page,
            "成绩录入": self._build_grade_input_page,
            "班级统计": self._build_class_stats_page,
            "考勤管理": self._build_attendance_page,
            "📊 成绩报表": self._build_grade_report_page,
            "💬 学生评语": self._build_student_comments_page,
            "📢 通知公告": self._build_notices_page,
            "📅 课表查看": self._build_schedule_view_page,
            "个人中心": self._build_profile_page,
        }

        self.nav_buttons = []

        # -------------- 1. 先单独放【仪表盘】（ttk.Button）--------------
        idx = 0
        text, builder = list(self.page_builders.items())[idx]

        def cmd(b=builder, btn_idx=idx):
            """命令执行入口."""
            self._switch_page(b)
            self._set_active_button(btn_idx)

        btn = ttk.Button(sidebar, text=text, style="Sidebar.TButton", command=cmd)
        btn.pack(fill="x", padx=15, ipady=5)
        self.nav_buttons.append(btn)

        # -------------- 2. 仪表盘与其他菜单之间的空隙 --------------
        spacer = tk.Frame(sidebar, height=20, bg="#0F766E")
        spacer.pack(fill="x")

        # -------------- 3. 其他菜单（tk.Label）--------------
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

            def _on_click(e, b=builder, target_idx=idx):
                """侧边栏按钮点击回调."""
                self._set_active_button(target_idx)
                self._switch_page(b)

            btn.bind("<Button-1>", _on_click)
            btn.pack(fill="x", padx=15, ipady=8)
            self.nav_buttons.append(btn)

        # 右侧内容区域
        self.content_area = tk.Frame(main_container, bg="white")
        self.content_area.pack(side="right", fill="both", expand=True)

        # 默认选中【仪表盘】
        self._switch_page(self._build_dashboard_page)
        self._set_active_button(0)
    """切换当前显示的页面."""

    def _switch_page(self, builder_func):
        """切换当前显示的页面."""
        for w in self.content_area.winfo_children():
            w.destroy()
        page_frame = tk.Frame(self.content_area, bg="white")
        page_frame.pack(fill="both", expand=True, padx=10, pady=10)
        builder_func(page_frame)
    """设置侧边栏激活按钮样式."""

    def _set_active_button(self, active_idx):
        """设置侧边栏激活按钮样式."""
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

    """构建仪表盘页面."""
    # ========== 仪表盘页面 ==========
    def _build_dashboard_page(self, parent):
        """构建仪表盘页面."""
        courses = self._get_teacher_courses()
        class_set = {
            cinfo.get("class_name", "")
            for cinfo in courses.values()
            if cinfo.get("class_name")
        }
        total_students = 0
        for cinfo in courses.values():
            class_name = cinfo.get("class_name", "")
            class_stats = self.dm.get_class_stats(class_name)
            if class_stats:
                total_students += class_stats.get("count", 0)

        banner = tk.Frame(parent, bg=TEAL_COLOR, height=80)
        banner.pack(fill="x")
        tk.Label(
            banner,
            text=f"👋 欢迎回来，{self.teacher_name}老师",
            font=("微软雅黑", 18, "bold"),
            fg="white",
            bg=TEAL_COLOR,
        ).pack(pady=(12, 2))
        tk.Label(
            banner,
            text=f"当前角色：教师 | {self.dm.get_teacher(self.teacher_id).get('name', self.teacher_name)}",
            font=("微软雅黑", 10),
            fg="#e0f2f1",
            bg=TEAL_COLOR,
        ).pack()

        card_row = tk.Frame(parent, bg="white")
        card_row.pack(fill="x", pady=10)

        """创建信息卡片组件."""
        def create_card(container, icon, title, value, color):
            card = tk.Frame(container, bg="white", relief="solid", bd=1)
            card.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(card, text=icon, font=("微软雅黑", 20), bg="white").pack(
                anchor="w", padx=10, pady=5
            )
            tk.Label(
                card, text=title, font=("微软雅黑", 10), fg="#6b7280", bg="white"
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

        create_card(card_row, "📚", "授课课程数", len(courses), TEAL_COLOR)
        create_card(card_row, "🏫", "教学班级数", len(class_set), "#8B5CF6")
        create_card(card_row, "👥", "教授学生总数", total_students, "#10B981")
        create_card(
            card_row, "📊", "平均及格率", f"{self._get_avg_pass_rate()}%", "#F59E0B"
        )

        info_frame = tk.Frame(parent, bg="#F0F9FF", bd=1, relief="solid")
        info_frame.pack(fill="x", pady=10)
        tk.Label(
            info_frame,
            text="💡 提示：点击左侧「成绩录入」选择课程并录入成绩",
            font=("微软雅黑", 11),
            bg="#F0F9FF",
        ).pack(pady=10)
        """计算平均及格率."""

    def _get_avg_pass_rate(self):
        """计算平均及格率."""
        courses = self._get_teacher_courses()
        rates = []
        for cinfo in courses.values():
            subject = cinfo["name"]
            analysis = self.dm.analyze_subject(subject)
            if analysis:
                rates.append(analysis.get("pass_rate", 0))
        if rates:
            return round(sum(rates) / len(rates), 1)
        return 0
    """构建成绩录入页面."""

    # ========== 成绩录入页面 ==========
    def _build_grade_input_page(self, parent):
        """构建成绩录入页面."""
        courses = self._get_teacher_courses()
        if not courses:
            tk.Label(
                parent,
                text="暂无课程，请联系管理员分配",
                font=("微软雅黑", 12),
                bg="white",
            ).pack(pady=20)
            return

        select_frame = tk.Frame(parent, bg="white")
        select_frame.pack(pady=10, fill="x", padx=10)
        tk.Label(
            select_frame, text="选择课程：", font=("微软雅黑", 11), bg="white"
        ).pack(side="left")
        self.course_var = tk.StringVar()
        course_display = [
            f"{cinfo['name']} ({cinfo.get('class_name', '')})"
            for cinfo in courses.values()
        ]
        self.course_combo = ttk.Combobox(
            select_frame,
            textvariable=self.course_var,
            values=course_display,
            width=30,
            state="readonly",
        )
        self.course_combo.pack(side="left", padx=10)
        ttk.Button(select_frame, text="加载", command=self._load_selected_course).pack(
            side="left"
        )

        self.course_id_map = {
            f"{cinfo['name']} ({cinfo.get('class_name', '')})": cid
            for cid, cinfo in courses.items()
        }

        self.grade_table_frame = tk.Frame(parent, bg="white")
        self.grade_table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.stats_frame = tk.Frame(parent, bg="#F0F9FF", bd=1, relief="solid")
        self.stats_frame.pack(fill="x", padx=10, pady=5)
        self.stats_label = tk.Label(
            self.stats_frame, text="", font=("微软雅黑", 11), bg="#F0F9FF", fg="#495057"
        )
        self.stats_label.pack(pady=10)

        if len(courses) == 1:
            self.course_combo.current(0)
            """加载选中课程的学生成绩."""
            self._load_selected_course()

    def _load_selected_course(self):
        """加载选中课程的学生成绩."""
        selected = self.course_var.get()
        if not selected or selected not in self.course_id_map:
            return
        course_id = self.course_id_map[selected]
        course = self.dm.get_course(course_id)
        if not course:
            return
        self.current_course_id = course_id
        self.current_course_name = course["name"]
        self.current_class_name = course.get("class_name", "")

        for w in self.grade_table_frame.winfo_children():
            w.destroy()

        btn_frame = tk.Frame(self.grade_table_frame, bg="white")
        btn_frame.pack(pady=5, anchor="w")
        ttk.Button(
            btn_frame,
            text="💾 保存成绩",
            style="success.TButton",
            command=self._save_grades,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="📥 批量导入",
            style="primary.TButton",
            command=self._import_scores,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="📤 导出成绩",
            style="info.TButton",
            command=self._export_scores,
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame, text="📊 统计", style="warning.TButton", command=self._show_stats
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame,
            text="🗑️ 清空成绩",
            style="danger.TButton",
            command=self._clear_course_scores,
        ).pack(side="left", padx=4)

        columns = ["学号", "姓名", "成绩"]
        widths = [140, 140, 140]
        self.tg_tree = ttk.Treeview(
            self.grade_table_frame, columns=columns, show="headings", height=18
        )
        for col, width in zip(columns, widths):
            self.tg_tree.heading(col, text=col)
            self.tg_tree.column(col, width=width, anchor="center")
        self.tg_tree.pack(fill="both", expand=True)
        self.tg_tree.tag_configure("odd", background="#F8FAFC")
        self.tg_tree.tag_configure("even", background="#FFFFFF")
        self.tg_tree.bind("<Double-1>", self._tg_cell_double_click)

        self.tg_entries = {}
        self._load_students_for_course()
        """为指定课程加载学生列表."""
        self._show_stats()

    def _load_students_for_course(self):
        """为指定课程加载学生列表."""
        for item in self.tg_tree.get_children():
            self.tg_tree.delete(item)
        self.tg_entries.clear()
        subject = self.current_course_name
        class_name = self.current_class_name
        if not subject:
            return
        idx = 0
        for sid, sinfo in self.dm.students.items():
            stu_class = sinfo.get("class", "")
            if class_name and stu_class != class_name:
                continue
            tag = "odd" if idx % 2 == 0 else "even"
            score = sinfo.get("scores", {}).get(subject, "")
            display_score = score if score != "" else "—"
            item_id = self.tg_tree.insert(
                "", "end", values=(sid, sinfo["name"], display_score), tags=(tag,)
            )
            self.tg_entries[item_id] = {"sid": sid, "score": score}
            """表格单元格双击编辑回调."""
            idx += 1

    def _tg_cell_double_click(self, event):
        """表格单元格双击编辑回调."""
        row_id = self.tg_tree.identify_row(event.y)
        col = self.tg_tree.identify_column(event.x)
        if not row_id or col != "#3":
            return
        x, y, w, h = self.tg_tree.bbox(row_id, col)
        current = self.tg_tree.set(row_id, col)
        if current == "—":
            current = ""
        var = tk.StringVar(value=current)
        entry = tk.Entry(
            self.tg_tree, textvariable=var, justify="center", font=("微软雅黑", 11)
        )
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus()
        entry.select_range(0, "end")

        """保存编辑内容."""
        def save_edit(_event=None):
            val = var.get().strip()
            if val == "":
                display = "—"
            else:
                try:
                    score = float(val)
                    if score < 0 or score > 100:
                        messagebox.showwarning("输入错误", "成绩必须在 0-100 之间")
                        entry.focus()
                        return
                    display = str(score)
                except ValueError:
                    messagebox.showwarning("输入错误", "请输入有效的数字")
                    entry.focus()
                    return
            self.tg_tree.set(row_id, col, display)
            self.tg_entries[row_id]["score"] = val
            entry.destroy()
            # 自动保存成绩
            sid = self.tg_entries[row_id]["sid"]
            subject = self.current_course_name
            if val == "":
                self.dm.set_score(sid, subject, None)
            else:
                self.dm.set_score(sid, subject, float(val))
            self._show_status(f"{subject} 成绩已自动保存", "ok")

        """保存当前编辑的成绩数据."""
        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    def _save_grades(self):
        """保存当前编辑的成绩数据."""
        subject = self.current_course_name
        if not subject:
            return
        count = 0
        errors = []
        for item_id, info in self.tg_entries.items():
            sid = info["sid"]
            score_str = self.tg_tree.set(item_id, "成绩")
            if score_str == "—" or score_str == "":
                continue
            try:
                score = float(score_str)
                if score < 0 or score > 100:
                    errors.append(f"学号 {sid} 成绩 {score} 超出范围")
                    continue
                self.dm.set_score(sid, subject, score)
                count += 1
            except Exception as e:
                errors.append(f"学号 {sid}: {e}")
        if errors:
            messagebox.showwarning("保存警告", "\n".join(errors[:5]))
        if count > 0:
            messagebox.showinfo("成功", f"成绩保存成功，共 {count} 条记录")
            self._load_students_for_course()
            self._show_stats()
        elif not errors:
            messagebox.showinfo("提示", "没有需要保存的成绩")

    def _clear_course_scores(self):
        """清空当前课程的所有成绩."""
        subject = self.current_course_name
        if not subject:
            return
        if not messagebox.askyesno(
            "危险操作确认", f"确定要清空「{subject}」的所有成绩吗？\n\n此操作不可恢复！"
        ):
            return
        count = 0
        for sid, sinfo in self.dm.students.items():
            if subject in sinfo.get("scores", {}):
                del sinfo["scores"][subject]
                count += 1
        self.dm.save()
        messagebox.showinfo("成功", f"已清空 {count} 名学生的成绩")
        """从外部文件导入成绩数据."""
        self._load_students_for_course()
        self._show_stats()

    def _import_scores(self):
        """从外部文件导入成绩数据."""
        fp = filedialog.askopenfilename(
            title="选择成绩文件", filetypes=[("CSV", "*.csv"), ("文本", "*.txt")]
        )
        if not fp:
            return
        subject = self.current_course_name
        if not subject:
            return
        count = 0
        errors = []
        try:
            with open(fp, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 2:
                        continue
                    sid = str(row[0]).strip()
                    score_str = str(row[1]).strip()
                    if not sid or not score_str:
                        continue
                    try:
                        score = float(score_str)
                        if score < 0 or score > 100:
                            errors.append(f"学号 {sid} 成绩超出范围")
                            continue
                        self.dm.set_score(sid, subject, score)
                        count += 1
                    except ValueError:
                        errors.append(f"学号 {sid} 成绩格式错误")
                    except Exception as e:
                        errors.append(f"学号 {sid}: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"文件读取失败: {e}")
            return
        if errors:
            messagebox.showwarning("导入警告", "\n".join(errors[:10]))
        messagebox.showinfo("成功", f"导入完成，成功 {count} 条")
        """将成绩数据导出为文件."""
        self._load_students_for_course()
        self._show_stats()

    def _export_scores(self):
        """将成绩数据导出为文件."""
        subject = self.current_course_name
        if not subject:
            return
        fp = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"{subject}_成绩.csv",
        )
        if not fp:
            return
        try:
            with open(fp, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["学号", "姓名", "成绩"])
                for item_id in self.tg_tree.get_children():
                    vals = self.tg_tree.item(item_id, "values")
                    writer.writerow(vals)
            messagebox.showinfo("成功", f"成绩已导出到：{os.path.basename(fp)}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def _show_stats(self):
        """显示成绩统计信息."""
        subject = self.current_course_name
        if not subject:
            return
        analysis = self.dm.analyze_subject(subject)
        if not analysis:
            self.stats_label.config(text="该课程暂无成绩数据")
            return
        info = (
            f"平均分: {analysis['avg']} | 最高分: {analysis['max']} | "
            f"最低分: {analysis['min']} | 及格率: {analysis['pass_rate']}% | "
            f"优秀率: {analysis['excellent_rate']}%"
        )
        """构建班级统计页面."""
        self.stats_label.config(text=info)

    # ========== 班级统计页面 ==========
    def _build_class_stats_page(self, parent):
        """构建班级统计页面."""
        courses = self._get_teacher_courses()
        if not courses:
            tk.Label(
                parent, text="暂无课程数据", font=("微软雅黑", 12), bg="white"
            ).pack(pady=20)
            return

        tk.Label(
            parent, text="📊 班级成绩统计", font=("微软雅黑", 14, "bold"), bg="white"
        ).pack(pady=4)
        select_frame = tk.Frame(parent, bg="white")
        select_frame.pack(pady=10)
        tk.Label(select_frame, text="选择课程：", bg="white").pack(side="left")
        stat_course_var = tk.StringVar()
        course_list = [
            f"{cinfo['name']} ({cinfo.get('class_name', '')})"
            for cinfo in courses.values()
        ]
        stat_combo = ttk.Combobox(
            select_frame,
            textvariable=stat_course_var,
            values=course_list,
            width=30,
            state="readonly",
        )
        stat_combo.pack(side="left", padx=5)
        result_frame = tk.Frame(parent, bg="white")
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        """加载统计数据."""
        def load_stats():
            for w in result_frame.winfo_children():
                w.destroy()
            sel = stat_course_var.get()
            if not sel:
                return
            target_cid = None
            for cid, cinfo in courses.items():
                if f"{cinfo['name']} ({cinfo.get('class_name', '')})" == sel:
                    target_cid = cid
                    break
            if not target_cid:
                return
            course = self.dm.get_course(target_cid)
            if not course:
                return
            subject = course["name"]
            analysis = self.dm.analyze_subject(subject)
            if not analysis:
                tk.Label(result_frame, text="暂无成绩数据", bg="white").pack(pady=20)
                return
            info = (
                f"参考人数: {analysis['count']} | 平均分: {analysis['avg']} | "
                f"最高分: {analysis['max']} | 最低分: {analysis['min']} | "
                f"及格率: {analysis['pass_rate']}% | 优秀率: {analysis['excellent_rate']}%"
            )
            tk.Label(
                result_frame,
                text=info,
                font=("微软雅黑", 11, "bold"),
                bg="white",
                fg="#0F766E",
            ).pack(pady=10)
            dist = analysis.get("distribution", {})
            tree = ttk.Treeview(
                result_frame, columns=["分数段", "人数"], show="headings", height=6
            )
            tree.heading("分数段", text="分数段")
            tree.heading("人数", text="人数")
            tree.column("分数段", width=120, anchor="center")
            tree.column("人数", width=100, anchor="center")
            tree.pack(pady=10)
            for seg, count in dist.items():
                tree.insert("", "end", values=(seg, count))

        ttk.Button(
            select_frame, text="查看统计", style="primary.TButton", command=load_stats
        ).pack(side="left", padx=10)
        if course_list:
            stat_combo.current(0)
            load_stats()

    # ========== 个人中心页面 ==========
    def _build_profile_page(self, parent):
        """构建教师个人中心页面."""
        tk.Label(
            parent, text="个人中心", font=("微软雅黑", 14, "bold"), bg="white"
        ).pack(pady=4)

        teacher = self.dm.get_teacher(self.teacher_id) or {}

        # 头像区域（水平排列）
        avatar_frame = tk.Frame(parent, bg="white")
        avatar_frame.pack(pady=15)
        tk.Label(
            avatar_frame,
            text="教师头像",
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

        # 工号（只读）
        tk.Label(form_frame, text="教师工号", font=("微软雅黑", 11), bg="white").grid(
            row=0, column=0, sticky="e", pady=8, padx=10
        )
        id_entry = tk.Entry(
            form_frame, font=("微软雅黑", 11), width=35, relief="solid", bd=1
        )
        id_entry.insert(0, self.teacher_id)
        id_entry.config(state="readonly", readonlybackground="#F3F4F6")
        id_entry.grid(row=0, column=1, sticky="w")

        # 密码
        tk.Label(form_frame, text="教师密码", font=("微软雅黑", 11), bg="white").grid(
            row=1, column=0, sticky="e", pady=8, padx=10
        )
        pwd_frame = tk.Frame(form_frame, bg="white")
        pwd_frame.grid(row=1, column=1, sticky="w")
        pwd_var = tk.StringVar(value=teacher.get("password", ""))
        pwd_entry = tk.Entry(pwd_frame, textvariable=pwd_var, show="*", **entry_opts)
        pwd_entry.pack(side="left")

        """切换密码显示/隐藏."""
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
        tk.Label(form_frame, text="教师名称", font=("微软雅黑", 11), bg="white").grid(
            row=2, column=0, sticky="e", pady=8, padx=10
        )
        name_var = tk.StringVar(value=self.teacher_name)
        tk.Entry(form_frame, textvariable=name_var, **entry_opts).grid(
            row=2, column=1, sticky="w"
        )

        # 手机号
        tk.Label(form_frame, text="手机号", font=("微软雅黑", 11), bg="white").grid(
            row=3, column=0, sticky="e", pady=8, padx=10
        )
        phone_var = tk.StringVar(value=teacher.get("phone", ""))
        tk.Entry(form_frame, textvariable=phone_var, **entry_opts).grid(
            row=3, column=1, sticky="w"
        )

        # 邮箱
        tk.Label(form_frame, text="邮箱", font=("微软雅黑", 11), bg="white").grid(
            row=4, column=0, sticky="e", pady=8, padx=10
        )
        email_var = tk.StringVar(value=teacher.get("email", ""))
        tk.Entry(form_frame, textvariable=email_var, **entry_opts).grid(
            row=4, column=1, sticky="w"
        )

        """保存个人资料."""
        def save_profile():
            new_name = name_var.get().strip()
            new_phone = phone_var.get().strip()
            new_email = email_var.get().strip()
            new_pwd = pwd_var.get().strip()
            teacher = self.dm.get_teacher(self.teacher_id) or {}
            self.dm.update_teacher(
                self.teacher_id,
                name=new_name,
                phone=new_phone,
                email=new_email,
                password=new_pwd,
                avatar=teacher.get("avatar", ""),
            )
            if new_name:
                self.teacher_name = new_name
            messagebox.showinfo("成功", "个人信息已保存")
            for w in self.win.winfo_children():
                if isinstance(w, tk.Frame) and w.winfo_children():
                    for child in w.winfo_children():
                        if isinstance(child, tk.Label) and "教师工作台" in child.cget(
                            "text"
                        ):
                            child.config(text=f"教师工作台 - {self.teacher_name}")
                            break
                    break

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
        """加载教师头像（个人中心 + 侧边栏）."""
        teacher = self.dm.get_teacher(self.teacher_id) or {}
        avatar_path = teacher.get("avatar", "")
        # 更新个人中心头像
        load_avatar(self.avatar_label, avatar_path)
        # 更新侧边栏头像
        if hasattr(self, "sidebar_avatar_label"):
            load_avatar(self.sidebar_avatar_label, avatar_path, size=(50, 50))
        self.win.update_idletasks()

    def _change_avatar(self) -> None:
        """更换教师头像."""
        teacher = self.dm.get_teacher(self.teacher_id) or {}
        current = teacher.get("avatar", "")

        def save_callback(path: str) -> None:
            """保存头像路径并刷新显示."""
            print("=" * 50)
            print("保存头像路径:", path)
            try:
                self.dm.update_teacher(self.teacher_id, avatar=path)
                updated = self.dm.get_teacher(self.teacher_id)
                print("更新后教师数据:", updated)
                self._load_avatar()
                messagebox.showinfo("成功", "头像已更新并保存")
            except Exception as e:
                print("ERROR in save_callback:", e)
                messagebox.showerror("保存失败", f"无法保存头像：{e}")

        try:
            result = change_avatar(self.win, current, save_callback)
            if result is None and current:
                # 用户取消操作，不做任何提示
                pass
        except Exception as e:
            messagebox.showerror(
                "错误", f"更换头像时发生异常：{e}\n请检查是否安装了 Pillow 库。"
            )

    # ========== 辅助方法 ==========
    def _get_teacher_courses(self) -> dict[str, dict]:
        """获取当前教师所授课程列表."""
        teacher = self.dm.data["teachers"].get(self.teacher_id)
        if not teacher:
            return {}
        course_ids = teacher.get("course_ids", [])
        courses = self.dm.courses
        return {cid: courses[cid] for cid in course_ids if cid in courses}

    def _change_password(self):
        """修改用户密码."""
        dialog = tk.Toplevel(self.win)
        dialog.title("修改密码")
        dialog.transient(self.win)
        dialog.grab_set()
        dialog.resizable(False, False)
        win_x = self.win.winfo_x()
        win_y = self.win.winfo_y()
        dialog.geometry(f"300x220+{win_x + 60}+{win_y + 120}")

        tk.Label(dialog, text="原密码：", font=("微软雅黑", 11)).pack(pady=(15, 2))
        old_var = tk.StringVar()
        tk.Entry(dialog, textvariable=old_var, show="*").pack()

        tk.Label(dialog, text="新密码：", font=("微软雅黑", 11)).pack(pady=(10, 2))
        new_var = tk.StringVar()
        tk.Entry(dialog, textvariable=new_var, show="*").pack()

        tk.Label(dialog, text="确认新密码：", font=("微软雅黑", 11)).pack(pady=(10, 2))
        confirm_var = tk.StringVar()
        tk.Entry(dialog, textvariable=confirm_var, show="*").pack()

        """执行密码修改操作."""
        def do_change():
            old = old_var.get().strip()
            new = new_var.get().strip()
            confirm = confirm_var.get().strip()
            teacher = self.dm.data["teachers"].get(self.teacher_id)
            if not teacher:
                return
            if teacher.get("password") != old:
                messagebox.showerror("错误", "原密码不正确")
                return
            if not new:
                messagebox.showwarning("提示", "新密码不能为空")
                return
            if new != confirm:
                messagebox.showerror("错误", "两次输入的新密码不一致")
                return
            teacher["password"] = new
            self.dm.save()
            messagebox.showinfo("成功", "密码已修改")
            dialog.destroy()

        ttk.Button(
            dialog, text="确认修改", style="primary.TButton", command=do_change
        ).pack(pady=15)

    # ========== 考勤管理页面 ==========
    def _build_attendance_page(self, parent: tk.Frame) -> None:
        """构建考勤管理页面."""
        tk.Label(
            parent,
            text="考勤管理",
            font=("微软雅黑", 14, "bold"),
            bg="white",
        ).pack(pady=4)

        courses = self._get_teacher_courses()
        course_list = list(courses.keys())

        # 控制区
        ctrl = tk.Frame(parent, bg="white")
        ctrl.pack(fill="x", pady=5)

        tk.Label(ctrl, text="课程：", bg="white", font=("微软雅黑", 11)).pack(
            side="left"
        )
        course_var = tk.StringVar()
        course_cb = ttk.Combobox(
            ctrl,
            textvariable=course_var,
            values=course_list,
            width=25,
            state="readonly",
        )
        course_cb.pack(side="left", padx=5)
        if course_list:
            course_cb.set(course_list[0])

        tk.Label(ctrl, text="日期：", bg="white", font=("微软雅黑", 11)).pack(
            side="left", padx=(15, 0)
        )
        import datetime

        date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(ctrl, textvariable=date_var, width=12, font=("微软雅黑", 11)).pack(
            side="left", padx=5
        )

        # 按钮区（先占位，按钮在函数定义后添加）
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=5, anchor="w")

        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, pady=5)

        columns = ["学号", "姓名", "班级", "出勤状态"]
        widths = [100, 100, 150, 120]
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True)
        tree.tag_configure("odd", background="#F8FAFC")
        tree.tag_configure("even", background="#FFFFFF")
        tree.tag_configure("absent", background="#FEF2F2")
        tree.tag_configure("late", background="#FEF3C7")
        tree.tag_configure("leave", background="#E0F2FE")

        status_map = {
            "出勤": "present",
            "缺勤": "absent",
            "迟到": "late",
            "请假": "leave",
        }
        reverse_map = {v: k for k, v in status_map.items()}
        status_options = list(status_map.keys())

        """执行操作."""
        def load_students():
            for item in tree.get_children():
                tree.delete(item)
            cid = course_var.get()
            if not cid or cid not in courses:
                return
            date_str = date_var.get().strip()
            class_name = courses[cid].get("class_name", "")
            existing = self.dm.get_attendance(date_str, cid)
            students = [
                (sid, stu)
                for sid, stu in self.dm.students.items()
                if stu.get("class", "") == class_name
            ]
            for idx, (sid, stu) in enumerate(students):
                status = existing.get(sid, "present")
                tag = (
                    status
                    if status != "present"
                    else ("odd" if idx % 2 == 0 else "even")
                )
                tree.insert(
                    "",
                    "end",
                    values=(
                        sid,
                        stu["name"],
                        class_name,
                        reverse_map.get(status, "出勤"),
                    ),
                    tags=(tag,),
                )
            _update_stats(len(students), existing)

        """更新统计数据显示."""
        def _update_stats(total, existing):
            present = sum(1 for s in existing.values() if s == "present")
            absent = sum(1 for s in existing.values() if s == "absent")
            late = sum(1 for s in existing.values() if s == "late")
            leave = sum(1 for s in existing.values() if s == "leave")
            rate = round(present / total * 100, 1) if total else 0.0
            stat_lbl.config(
                text=(
                    f"总人数: {total} | 出勤: {present} | 缺勤: {absent} | "
                    f"迟到: {late} | 请假: {leave} | 出勤率: {rate}%"
                )
            )

        """保存考勤记录."""
        def save_attendance(silent: bool = False):
            cid = course_var.get()
            date_str = date_var.get().strip()
            if not cid or not date_str:
                if not silent:
                    messagebox.showwarning("提示", "请选择课程和日期")
                return
            records = {}
            for item in tree.get_children():
                vals = tree.item(item, "values")
                if len(vals) >= 4:
                    records[vals[0]] = status_map.get(vals[3], "present")
            self.dm.batch_record_attendance(date_str, cid, records)
            if not silent:
                messagebox.showinfo("成功", "考勤已保存")
                load_students()

        """批量设置考勤状态."""
        def set_all_status(status_key):
            for item in tree.get_children():
                vals = list(tree.item(item, "values"))
                if len(vals) >= 4:
                    vals[3] = status_key
                    tree.item(item, values=tuple(vals))
            cid = course_var.get()
            date_str = date_var.get().strip()
            if cid and date_str:
                records = {}
                for item in tree.get_children():
                    vals = tree.item(item, "values")
                    if len(vals) >= 4:
                        records[vals[0]] = status_map.get(vals[3], "present")
                _update_stats(
                    len(tree.get_children()),
                    records,
                )
                # 自动保存考勤
                save_attendance(silent=True)

        """树形控件点击回调."""
        def on_tree_click(event):
            region = tree.identify_region(event.x, event.y)
            if region != "cell":
                return
            col = tree.identify_column(event.x)
            if col != "#4":
                return
            row = tree.identify_row(event.y)
            if not row:
                return
            vals = list(tree.item(row, "values"))
            if len(vals) < 4:
                return
            current = vals[3]
            idx = status_options.index(current) if current in status_options else 0
            next_idx = (idx + 1) % len(status_options)
            vals[3] = status_options[next_idx]
            tree.item(row, values=tuple(vals))
            status_val = status_map.get(vals[3], "present")
            tag = (
                status_val
                if status_val != "present"
                else ("odd" if tree.index(row) % 2 == 0 else "even")
            )
            tree.item(row, tags=(tag,))
            # 更新统计
            cid = course_var.get()
            date_str = date_var.get().strip()
            if cid and date_str:
                records = {}
                for item in tree.get_children():
                    v = tree.item(item, "values")
                    if len(v) >= 4:
                        records[v[0]] = status_map.get(v[3], "present")
                _update_stats(len(tree.get_children()), records)
                # 自动保存考勤
                save_attendance(silent=True)

        tree.bind("<ButtonRelease-1>", on_tree_click)

        # 向占位 btn_frame 添加按钮
        ttk.Button(
            btn_frame, text="加载学生", style="primary.TButton", command=load_students
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame, text="保存考勤", style="success.TButton", command=save_attendance
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="全部出勤",
            style="info.TButton",
            command=lambda: set_all_status("出勤"),
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="全部缺勤",
            style="danger.TButton",
            command=lambda: set_all_status("缺勤"),
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="查看历史",
            style="warning.TButton",
            command=self._show_attendance_history,
        ).pack(side="left", padx=5)

        # 统计标签
        stat_lbl = tk.Label(
            parent,
            text="请选择课程和日期",
            font=("微软雅黑", 11, "bold"),
            bg="#E6F7F0",
            fg="#0F766E",
        )
        stat_lbl.pack(fill="x", pady=5)

        if course_list:
            load_students()

    def _show_attendance_history(self) -> None:
        """显示考勤历史记录弹窗."""
        dialog = tk.Toplevel(self.win)
        dialog.title("考勤历史")
        dialog.geometry("700x500")
        dialog.transient(self.win)
        win_x = self.win.winfo_x()
        win_y = self.win.winfo_y()
        dialog.geometry(f"700x500+{win_x + 60}+{win_y + 120}")

        courses = self._get_teacher_courses()
        course_list = list(courses.keys())

        ctrl = tk.Frame(dialog, bg="white")
        ctrl.pack(fill="x", pady=5, padx=10)

        tk.Label(ctrl, text="课程：", bg="white", font=("微软雅黑", 11)).pack(
            side="left"
        )
        course_var = tk.StringVar()
        course_cb = ttk.Combobox(
            ctrl,
            textvariable=course_var,
            values=course_list,
            width=25,
            state="readonly",
        )
        course_cb.pack(side="left", padx=5)
        if course_list:
            course_cb.set(course_list[0])

        columns = ["日期", "总人数", "出勤", "缺勤", "迟到", "请假", "出勤率"]
        widths = [120, 80, 60, 60, 60, 60, 80]
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=18)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=5)
        tree.tag_configure("odd", background="#F8FAFC")
        tree.tag_configure("even", background="#FFFFFF")

        """加载历史记录."""
        def load_history():
            for item in tree.get_children():
                tree.delete(item)
            cid = course_var.get()
            if not cid:
                return
            dates = self.dm.get_attendance_dates(cid)
            for idx, date_str in enumerate(dates):
                stats = self.dm.get_attendance_stats(date_str, cid)
                tag = "odd" if idx % 2 == 0 else "even"
                tree.insert(
                    "",
                    "end",
                    values=(
                        date_str,
                        stats["total"],
                        stats["present"],
                        stats["absent"],
                        stats["late"],
                        stats["leave"],
                        f"{stats['rate']}%",
                    ),
                    tags=(tag,),
                )

        ttk.Button(
            ctrl, text="查询", style="primary.TButton", command=load_history
        ).pack(side="left", padx=10)
        ttk.Button(
            ctrl,
            text="删除选中",
            style="danger.TButton",
            command=lambda: self._delete_attendance_record(tree, course_var),
        ).pack(side="left", padx=5)

        if course_list:
            load_history()

    def _delete_attendance_record(self, tree, course_var) -> None:
        """删除选中的考勤记录."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中一条记录")
            return
        vals = tree.item(selected[0], "values")
        if not vals or not vals[0]:
            return
        date_str = vals[0]
        cid = course_var.get()
        if messagebox.askyesno("确认", f"确定删除 {date_str} 的考勤记录吗？"):
            self.dm.delete_attendance(date_str, cid)
            tree.delete(selected[0])

    # ========== 成绩报表页面 ==========
    def _build_grade_report_page(self, parent):
        """构建成绩报表页面（班级统计/年级统计，含标准差）."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="📊 成绩报表", font=("微软雅黑", 16, "bold"), bg="white"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 选择课程
        courses = self._get_teacher_courses()
        course_list = list(courses.keys())

        ctrl = tk.Frame(parent, bg="white")
        ctrl.pack(fill="x", padx=20, pady=5)

        tk.Label(ctrl, text="选择课程：", bg="white", font=("微软雅黑", 11)).pack(
            side="left"
        )
        course_var = tk.StringVar()
        course_cb = ttk.Combobox(
            ctrl,
            textvariable=course_var,
            values=course_list,
            width=25,
            state="readonly",
        )
        course_cb.pack(side="left", padx=5)
        if course_list:
            course_cb.set(course_list[0])

        ttk.Button(
            ctrl, text="生成报表", style="primary.TButton", command=lambda: _generate()
        ).pack(side="left", padx=10)

        report_frame = tk.Frame(parent, bg="white")
        report_frame.pack(fill="both", expand=True, padx=20, pady=10)

        """生成报表数据."""
        def _generate():
            for w in report_frame.winfo_children():
                w.destroy()

            cid = course_var.get()
            if not cid or cid not in courses:
                messagebox.showwarning("提示", "请选择课程")
                return

            course = courses[cid]
            subject = course["name"]
            class_name = course.get("class_name", "")

            # 获取该课程所有学生成绩
            scores = []
            students_in_class = []
            for sid, sinfo in self.dm.students.items():
                if class_name and sinfo.get("class", "") != class_name:
                    continue
                score = sinfo.get("scores", {}).get(subject, "")
                if score != "" and score is not None:
                    try:
                        scores.append(float(score))
                        students_in_class.append((sid, sinfo["name"], float(score)))
                    except (ValueError, TypeError):
                        pass

            if not scores:
                tk.Label(
                    report_frame,
                    text="暂无成绩数据",
                    font=("微软雅黑", 12),
                    bg="white",
                    fg="#888888",
                ).pack(pady=20)
                return

            # 班级统计
            stat_frame = tk.LabelFrame(
                report_frame,
                text="班级统计",
                font=("微软雅黑", 12, "bold"),
                bg="white",
                fg=TEAL_COLOR,
            )
            stat_frame.pack(fill="x", pady=10)

            import math

            avg = sum(scores) / len(scores)
            max_s = max(scores)
            min_s = min(scores)
            variance = sum((s - avg) ** 2 for s in scores) / len(scores)
            std_dev = math.sqrt(variance)
            pass_count = len([s for s in scores if s >= 60])
            pass_rate = pass_count / len(scores) * 100
            excellent_count = len([s for s in scores if s >= 90])
            excellent_rate = excellent_count / len(scores) * 100

            stat_grid = tk.Frame(stat_frame, bg="white")
            stat_grid.pack(padx=20, pady=10, fill="x")

            stats_info = [
                ("总人数", f"{len(scores)}"),
                ("平均分", f"{avg:.1f}"),
                ("最高分", f"{max_s:.0f}"),
                ("最低分", f"{min_s:.0f}"),
                ("标准差", f"{std_dev:.2f}"),
                ("方差", f"{variance:.2f}"),
                ("及格人数", f"{pass_count}"),
                ("及格率", f"{pass_rate:.1f}%"),
                ("优秀人数", f"{excellent_count}"),
                ("优秀率", f"{excellent_rate:.1f}%"),
            ]

            for i, (label, value) in enumerate(stats_info):
                row, col = divmod(i, 5)
                cell = tk.Frame(stat_grid, bg="white", relief="solid", bd=1)
                cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                stat_grid.columnconfigure(col, weight=1)
                tk.Label(
                    cell, text=label, font=("微软雅黑", 10), bg="white", fg="#6b7280"
                ).pack(pady=(5, 0))
                tk.Label(
                    cell,
                    text=value,
                    font=("微软雅黑", 14, "bold"),
                    bg="white",
                    fg=TEAL_COLOR,
                ).pack(pady=(0, 5))

            # 成绩明细表
            detail_frame = tk.LabelFrame(
                report_frame,
                text="成绩明细",
                font=("微软雅黑", 12, "bold"),
                bg="white",
                fg=TEAL_COLOR,
            )
            detail_frame.pack(fill="both", expand=True, pady=10)

            columns = ["学号", "姓名", "成绩", "等级"]
            tree = ttk.Treeview(
                detail_frame, columns=columns, show="headings", height=12
            )
            for col_name in columns:
                tree.heading(col_name, text=col_name)
                tree.column(col_name, width=120, anchor="center")
            tree.pack(fill="both", expand=True, padx=10, pady=5)
            tree.tag_configure("excellent", background="#E6F7F0")
            tree.tag_configure("good", background="#F0F9FF")
            tree.tag_configure("pass", background="#FFF8E1")
            tree.tag_configure("fail", background="#FEF2F2")

            for sid, name, score in sorted(
                students_in_class, key=lambda x: x[2], reverse=True
            ):
                if score >= 90:
                    grade = "优秀"
                    tag = "excellent"
                elif score >= 80:
                    grade = "良好"
                    tag = "good"
                elif score >= 60:
                    grade = "及格"
                    tag = "pass"
                else:
                    grade = "不及格"
                    tag = "fail"
                tree.insert(
                    "", "end", values=(sid, name, f"{score:.0f}", grade), tags=(tag,)
                )

        if course_list:
            _generate()

    # ========== 学生评语页面 ==========
    def _build_student_comments_page(self, parent):
        """构建学生评语页面（左侧学生列表，右侧历史+新评语）."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="💬 学生评语", font=("微软雅黑", 16, "bold"), bg="white"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 选择课程
        courses = self._get_teacher_courses()
        course_list = list(courses.keys())

        ctrl = tk.Frame(parent, bg="white")
        ctrl.pack(fill="x", padx=20, pady=5)

        tk.Label(ctrl, text="选择课程：", bg="white", font=("微软雅黑", 11)).pack(
            side="left"
        )
        course_var = tk.StringVar()
        course_cb = ttk.Combobox(
            ctrl,
            textvariable=course_var,
            values=course_list,
            width=25,
            state="readonly",
        )
        course_cb.pack(side="left", padx=5)
        if course_list:
            course_cb.set(course_list[0])

        main_pane = tk.Frame(parent, bg="white")
        main_pane.pack(fill="both", expand=True, padx=20, pady=10)

        # 左侧学生列表
        left_frame = tk.LabelFrame(
            main_pane,
            text="学生列表",
            font=("微软雅黑", 11, "bold"),
            bg="white",
            width=250,
        )
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        student_tree = ttk.Treeview(
            left_frame, columns=["学号", "姓名"], show="headings", height=20
        )
        student_tree.heading("学号", text="学号")
        student_tree.heading("姓名", text="姓名")
        student_tree.column("学号", width=100, anchor="center")
        student_tree.column("姓名", width=100, anchor="center")
        student_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # 右侧评语区域
        right_frame = tk.Frame(main_pane, bg="white")
        right_frame.pack(side="right", fill="both", expand=True)

        history_label = tk.Label(
            right_frame,
            text="选择一位学生查看评语",
            font=("微软雅黑", 12),
            bg="white",
            fg="#888888",
        )
        history_label.pack(pady=20)

        # 评语历史区域
        history_frame = tk.Frame(right_frame, bg="white")
        history_frame.pack(fill="both", expand=True)

        # 新评语输入区域
        input_frame = tk.LabelFrame(
            right_frame, text="撰写新评语", font=("微软雅黑", 11, "bold"), bg="white"
        )
        input_frame.pack(fill="x", pady=(10, 0))

        comment_text = tk.Text(
            input_frame, font=("微软雅黑", 11), height=4, wrap="word"
        )
        comment_text.pack(fill="x", padx=10, pady=5)

        save_btn = tk.Button(
            input_frame,
            text="保存评语",
            font=("微软雅黑", 11),
            bg=TEAL_COLOR,
            fg="white",
            activebackground=TEAL_DARK,
            relief="flat",
            cursor="hand2",
            command=lambda: _save_comment(),
        )
        save_btn.pack(pady=(0, 10))

        selected_sid = [None]

        """加载学生列表."""
        def _load_students():
            for item in student_tree.get_children():
                student_tree.delete(item)
            cid = course_var.get()
            if not cid or cid not in courses:
                return
            class_name = courses[cid].get("class_name", "")
            for sid, sinfo in self.dm.students.items():
                if class_name and sinfo.get("class", "") != class_name:
                    continue
                student_tree.insert("", "end", values=(sid, sinfo["name"]))

        """学生选择变更回调."""
        def _on_student_select(event):
            selection = student_tree.selection()
            if not selection:
                return
            values = student_tree.item(selection[0], "values")
            sid = values[0]
            selected_sid[0] = sid
            _load_comments(sid)

        """加载学生评语列表."""
        def _load_comments(sid):
            for w in history_frame.winfo_children():
                w.destroy()
            history_label.config(text=f"学号 {sid} 的评语记录")

            student = self.dm.students.get(sid, {})
            comments = student.get("comments", [])

            if not comments:
                tk.Label(
                    history_frame,
                    text="暂无评语记录",
                    font=("微软雅黑", 11),
                    bg="white",
                    fg="#888888",
                ).pack(pady=10)
                return

            # 创建带滚动条的评语列表容器
            canvas = tk.Canvas(history_frame, bg="white", highlightthickness=0)
            v_scroll = ttk.Scrollbar(
                history_frame, orient="vertical", command=canvas.yview
            )
            canvas.configure(yscrollcommand=v_scroll.set)

            v_scroll.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

            list_frame = tk.Frame(canvas, bg="white")
            canvas.create_window((0, 0), window=list_frame, anchor="nw")

            for orig_idx in range(len(comments) - 1, -1, -1):
                c = comments[orig_idx]
                card = tk.Frame(
                    list_frame,
                    bg="#F8FAFC",
                    bd=1,
                    relief="solid",
                    highlightbackground="#E2E8F0",
                    highlightthickness=1,
                )
                card.pack(fill="x", padx=5, pady=5, ipadx=8, ipady=8)

                header = tk.Frame(card, bg="#F8FAFC")
                header.pack(fill="x", padx=10, pady=(8, 4))

                tk.Label(
                    header,
                    text=c.get("date", ""),
                    font=("微软雅黑", 10, "bold"),
                    bg="#F8FAFC",
                    fg="#0F766E",
                ).pack(side="left")

                btn_frame = tk.Frame(header, bg="#F8FAFC")
                btn_frame.pack(side="right")

                tk.Label(
                    header,
                    text=f"教师：{c.get('teacher', '')}",
                    font=("微软雅黑", 10),
                    bg="#F8FAFC",
                    fg="#64748B",
                ).pack(side="right", padx=(0, 8))

                def _start_edit(
                    card=card,
                    content=c.get("content", ""),
                    idx=orig_idx,
                ):
                    # 清除卡片中除 header 外的所有内容
                    """开始行内编辑."""
                    for w in card.winfo_children()[1:]:
                        w.destroy()

                    edit_frame = tk.Frame(card, bg="#F8FAFC")
                    edit_frame.pack(fill="x", padx=10, pady=(0, 8))

                    edit_text = tk.Text(
                        edit_frame,
                        font=("微软雅黑", 11),
                        height=4,
                        wrap="word",
                    )
                    edit_text.pack(fill="x")
                    edit_text.insert("1.0", content)

                    btn_row = tk.Frame(edit_frame, bg="#F8FAFC")
                    btn_row.pack(fill="x", pady=(5, 0))

                    def _commit_edit():
                        """提交行内编辑结果."""
                        new_content = edit_text.get("1.0", "end-1c").strip()
                        if not new_content:
                            messagebox.showwarning("提示", "评语内容不能为空")
                            return
                        self.dm.data["students"][sid]["comments"][idx][
                            "content"
                        ] = new_content
                        self.dm.save()
                        _load_comments(sid)
                        self._show_status("评语已更新", "ok")

                    ttk.Button(
                        btn_row,
                        text="保存",
                        style="success.TButton",
                        command=_commit_edit,
                    ).pack(side="right", padx=(4, 0))
                    ttk.Button(
                        btn_row,
                        text="取消",
                        style="secondary.TButton",
                        command=lambda: _load_comments(sid),
                    ).pack(side="right", padx=(4, 0))

                tk.Button(
                    btn_frame,
                    text="编辑",
                    font=("微软雅黑", 9),
                    bg="#E2E8F0",
                    fg="#374151",
                    relief="flat",
                    cursor="hand2",
                    command=_start_edit,
                ).pack(side="right")

                content = c.get("content", "")
                tk.Message(
                    card,
                    text=content,
                    font=("微软雅黑", 11),
                    bg="#F8FAFC",
                    fg="#1F2937",
                    anchor="w",
                    width=500,
                ).pack(fill="x", padx=10, pady=(0, 8))

            list_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            canvas.bind(
                "<Configure>",
                lambda e: canvas.config(scrollregion=canvas.bbox("all")),
            )
            """保存评语内容."""

        def _save_comment():
            sid = selected_sid[0]
            if not sid:
                messagebox.showwarning("提示", "请先选择一位学生")
                return
            content_text = comment_text.get("1.0", "end-1c").strip()
            if not content_text:
                messagebox.showwarning("提示", "请输入评语内容")
                return

            import datetime

            new_comment = {
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "content": content_text,
                "teacher": self.teacher_name,
                "teacher_id": self.teacher_id,
            }

            # 保存评语到学生数据（直接操作原始数据，
            # students 属性返回深拷贝，赋值无法持久化）
            student = self.dm.data["students"].get(sid, {})
            if "comments" not in student:
                student["comments"] = []
            student["comments"].append(new_comment)
            self.dm.data["students"][sid] = student
            self.dm.save()

            messagebox.showinfo("成功", "评语已保存")
            comment_text.delete("1.0", "end")
            _load_comments(sid)

        student_tree.bind("<<TreeviewSelect>>", _on_student_select)

        ttk.Button(
            ctrl, text="加载学生", style="primary.TButton", command=_load_students
        ).pack(side="left", padx=10)

        if course_list:
            _load_students()

    # ========== 通知公告页面 ==========
    def _build_notices_page(self, parent):
        """构建通知公告页面（只读列表）."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="📢 通知公告", font=("微软雅黑", 16, "bold"), bg="white"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 获取通知列表（teacher 角色）
        notices = (
            self.dm.get_notices(role="teacher")
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
        self._teacher_notice_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=18
        )
        widths = [250, 100, 120, 100]
        for col, width in zip(columns, widths):
            self._teacher_notice_tree.heading(col, text=col)
            self._teacher_notice_tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self._teacher_notice_tree.yview
        )
        self._teacher_notice_tree.configure(yscrollcommand=vsb.set)

        self._teacher_notice_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for notice in notices:
            self._teacher_notice_tree.insert(
                "",
                "end",
                values=(
                    notice.get("title", ""),
                    notice.get("publisher", ""),
                    notice.get("date", ""),
                    notice.get("target", "all"),
                ),
            )
            """列表双击回调."""

        def _on_double_click(event):
            selection = self._teacher_notice_tree.selection()
            if not selection:
                return
            values = self._teacher_notice_tree.item(selection[0], "values")
            title = values[0]

            # 找到对应通知
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

        self._teacher_notice_tree.bind("<Double-1>", _on_double_click)

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
            font=("微软雅黑", 10),
            bg="#95A5A6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._refresh_schedule_tree,
            padx=12,
            pady=4,
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

    # ========== Excel 导入导出页面 ==========

    # ------------------------------------------------------------------
    # 从管理员端迁移: _build_excel_page
    # ------------------------------------------------------------------
    def _build_excel_page(self, parent: tk.Frame) -> None:
        """构建 Excel 导入导出页面."""
        # 创建主内容容器
        self._excel_parent = tk.Frame(parent, bg="white")
        self._excel_parent.pack(fill="both", expand=True)

        tk.Label(
            self._excel_parent,
            text="📥 Excel 导入导出",
            font=("微软雅黑", 14, "bold"),
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

    # ========== 班级管理页面 ==========

    # ------------------------------------------------------------------
    # 从管理员端迁移: _build_class_page
    # ------------------------------------------------------------------
    def _build_class_page(self, parent: tk.Frame) -> None:
        """构建班级管理页面，支持添加、删除、查看班级详情和右键菜单操作.

        Args:
            parent: 父容器 Frame，用于放置班级管理页面内容。
        """
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
        ttk.Button(
            btn_frame,
            text="🗑️ 删除班级",
            style="danger.TButton",
            command=self._class_delete_selected,
        ).pack(side="left", padx=4)
        columns = ["班级名称", "学生人数", "平均分", "最高分", "最低分", "操作"]
        widths = [150, 80, 80, 80, 80, 120]

        # 1. 创建外层容器 frame（用于装表格和滚动条）
        frame = tk.Frame(parent, bg="white")
        frame.pack(pady=(0, 10), fill="both", expand=True)

        # 2. 创建表格
        self.cl_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

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

        # 8. 绑定右键菜单事件
        self.cl_tree.bind("<Button-3>", self._class_show_context_menu)

        # 9. 创建右键菜单
        self.cl_context_menu = tk.Menu(self.win, tearoff=0)
        self.cl_context_menu.add_command(
            label="查看详情", command=self._class_menu_show_detail
        )
        self.cl_context_menu.add_separator()
        self.cl_context_menu.add_command(
            label="删除班级", command=self._class_menu_delete, foreground="red"
        )

        # 10. 刷新数据
        self._refresh_class_tree()

    # ========== 成绩管理页面 ==========

    # ------------------------------------------------------------------
    # 从管理员端迁移: _build_manage_page
    # ------------------------------------------------------------------
    def _build_manage_page(self, parent: tk.Frame) -> None:
        """构建成绩管理页面，支持成绩过滤、排序、删除和科目管理功能.

        Args:
            parent: 父容器 Frame，用于放置成绩管理页面内容。
        """
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
        filter_label = tk.Label(
            btn_frame,
            text="班级过滤：",
            font=("微软雅黑", 13),
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
            "<<ComboboxSelected>>", lambda e: self._refresh_manage_tree()
        )

        # 成绩范围筛选
        score_label = tk.Label(
            btn_frame,
            text="成绩范围：",
            font=("微软雅黑", 13),
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
            "<<ComboboxSelected>>", lambda e: self._refresh_manage_tree()
        )

        ttk.Button(
            btn_frame,
            text="🗑️ 删除",
            style="danger.TButton",
            command=self._manage_delete_selected,
        ).pack(side="left", padx=4)

        # ========== 新增：重置所有按钮 ==========
        ttk.Button(
            btn_frame,
            text="♻️ 重置",
            style="danger.TButton",
            command=self._reset_all_data,
        ).pack(side="left", padx=4)
        # =======================================

        subjects = self.dm.subjects
        columns = ["学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        widths = [110, 90, 90] + self._calc_subject_widths(subjects) + [80, 80]
        self.mg_tree = self._create_treeview(parent, columns, widths, 18)
        # ====== 新增：颜色预警标签 ======
        self.mg_tree.tag_configure("fail", foreground="#EF4444")  # 不及格 → 红色
        self.mg_tree.tag_configure("warn", foreground="#F59E0B")  # 偏低 → 橙色
        self.mg_tree.tag_configure("good", foreground="#10B981")  # 全优 → 绿色
        # 全部缺考 → 灰色
        self.mg_tree.tag_configure("empty_all", foreground="#9CA3AF")
        # ========================================
        self.mg_tree.bind("<Double-1>", self._manage_cell_double_click)

        # ====== 列头点击排序 ======
        self._mg_sort_asc = True
        self._mg_sort_col = ""
        for col in columns:

            def _make_sort_cmd(c):
                """创建列排序回调，避免 lambda 闭包陷阱."""
                return lambda: self._manage_sort_tree(c)

            self.mg_tree.heading(col, command=_make_sort_cmd(col))

        self._refresh_manage_tree()

    # ========== 查询页面 ==========

    # ------------------------------------------------------------------
    # 从管理员端迁移: _build_search_page
    # ------------------------------------------------------------------
    def _build_search_page(self, parent: tk.Frame) -> None:
        """构建搜索查询页面，支持按学号或姓名搜索学生及其成绩.

        Args:
            parent: 父容器 Frame，用于放置搜索查询页面内容。
        """
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
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            search_frame,
            text="🔄 全部",
            style="warning.TButton",
            command=self._refresh_search_list,
        ).pack(side="left", padx=(8, 8))
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
            width=32,
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
            command=lambda: self._search_show_history(
                self.dv["sid"].get() if hasattr(self, "dv") else ""
            ),
        ).pack(side="right")

        self.dv = {}
        info_frame = tk.Frame(detail_frame, bg="white")
        info_frame.pack(pady=3)
        for i, (key, label) in enumerate(
            [("sid", "学号"), ("name", "姓名"), ("cls", "班级")]
        ):
            tk.Label(
                info_frame, text=f"{label}：", bg="white", font=("微软雅黑", 12)
            ).grid(row=i, column=0, sticky="w", padx=10, pady=2)
            self.dv[key] = tk.StringVar(value="—")
            tk.Label(
                info_frame,
                textvariable=self.dv[key],
                font=("微软雅黑", 13, "bold"),
                bg="white",
            ).grid(row=i, column=1, sticky="w", padx=10, pady=2)

        self.stt = ttk.Treeview(
            detail_frame, columns=["科目", "成绩", "等级"], show="headings", height=12
        )
        for col, width in [("科目", 120), ("成绩", 80), ("等级", 80)]:
            self.stt.heading(col, text=col)
            self.stt.column(col, width=width, anchor="center")
        self.stt.pack(pady=10, padx=10, fill="both", expand=True)

        level_tags = [
            ("excellent", "#D1FAE5"),
            ("good", "#DBEAFE"),
            ("pass_", "#FEF9C3"),
            ("fail", "#FEE2E2"),
        ]
        for tag, bg in level_tags:
            self.stt.tag_configure(tag, background=bg)

        summary_frame = tk.Frame(detail_frame, bg="#F0F9FF")
        summary_frame.pack(pady=5, fill="x")
        for label, key in [("总分", "total"), ("平均分", "avg")]:
            lbl = tk.Label(
                summary_frame,
                text=label + ":",
                bg="#F0F9FF",
                font=("微软雅黑", 12),
            )
            lbl.pack(side="left", padx=30)
            self.dv[key] = tk.StringVar(value="—")
            tk.Label(
                summary_frame,
                textvariable=self.dv[key],
                font=("微软雅黑", 18, "bold"),
                fg="#1E3A8A",
                bg="#F0F9FF",
            ).pack(side="left", padx=10)

        self._refresh_search_list()

    # ========== 图表页面 ==========

    # ------------------------------------------------------------------
    # 从管理员端迁移: _build_chart_page
    # ------------------------------------------------------------------
    def _build_chart_page(self, parent: tk.Frame) -> None:
        """构建图表分析页面，支持趋势图、箱线图、散点图和排名图展示.

        Args:
            parent: 父容器 Frame，用于放置图表页面内容。

        Note:
            若未安装 matplotlib，会显示警告信息。
        """
        if not MAT_OK:
            tk.Label(
                parent,
                text="⚠️ 未安装 matplotlib，无法使用图表功能",
                fg="red",
                font=("微软雅黑", 12),
            ).pack(expand=True)
            return

        tk.Label(
            parent, text="📈 数据图表", font=("微软雅黑", 14, "bold"), bg="white"
        ).pack(pady=4)
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
            ttk.Button(
                control_frame, text=text, style="primary.TButton", command=cmd
            ).pack(side="left", padx=3)

        tk.Label(
            control_frame,
            text="科目（仅成绩分布使用）：",
            bg="white",
            fg="#64748B",
            font=("微软雅黑", 9),
        ).pack(side="left", padx=(10, 2))
        """根据分数返回等级."""
        first_subject = self.dm.subjects[0] if self.dm.subjects else ""
        self.ch_subj = tk.StringVar(value=first_subject)
        self.ch_cb = ttk.Combobox(
            control_frame,
            textvariable=self.ch_subj,
            values=self.dm.subjects,
            width=10,
            state="readonly",
        )
        self.ch_cb.pack(side="left")
        """根据分数返回等级标签文本."""
        self.ch_subj.trace("w", lambda *args: self._chart_histogram())

        self.ct = tk.Frame(parent, bg="white")
        self.ct.pack(fill="both", expand=True)

        if self.dm.students:  # 有数据才显示，避免报错
            self._chart_total_ranking()

    # ========== 公共工具方法 ==========

    @staticmethod
    def _get_level(score: float) -> str:
        """根据分数返回等级."""
        if score >= 90:
            return "优秀"
        if score >= 75:
            return "良好"
        if score >= 60:
            return "及格"
        return "不及格"

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

    def _check_excel_available(self) -> bool:
        """检查 Excel 相关依赖是否已安装.

        Returns:
            True 表示 openpyxl 可用，False 表示未安装。

        若不可用，会弹出提示框引导用户安装依赖。
        """
        if not EX_OK:
            logger.error("Excel 操作失败: 库未安装")
            messagebox.showerror("缺少库", "请执行：pip install openpyxl")
            return False
        return True

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
        self._show_status(
            f"学生 {len(self.dm.students)} 人 | 班级 {len(self.dm.classes)} 个"
        )

    def _update_clock(self) -> None:
        """更新时钟标签为当前日期时间."""
        self.clock.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.win.after(1000, self._update_clock)

    """计算科目列宽度."""
    def _refresh_all_pages(self) -> None:
        """刷新所有页面的数据和 UI 显示.

        依次调用各页面的刷新方法，包括成绩管理、查询、班级、
        Excel、录入、分析和图表页面。如果某页面表格已被销毁，
        则静默跳过，避免程序崩溃。
        """
        if hasattr(self, "mg_tree"):
            self._refresh_manage_tree()
        if hasattr(self, "ex_tree"):
            """创建并配置 Treeview 表格控件."""
            if hasattr(self, "_excel_parent"):
                self._refresh_excel_tree(self._excel_parent)
        if hasattr(self, "se_list"):
            self._refresh_search_list()
        if hasattr(self, "da_cards"):
            self._refresh_dashboard()
        if hasattr(self, "cl_tree"):
            self._refresh_class_tree()

    def _calc_subject_widths(
        self, subjects: list[str], min_width: int = 72
    ) -> list[int]:
        """计算科目列宽度."""
        return [max(min_width, len(s) * 14) for s in subjects]

    def _create_treeview(
        self,
        parent: tk.Frame,
        columns: list[str],
        widths: list[int],
        height: int = 14,
        pack_frame: bool = True,
    ) -> ttk.Treeview:
        """创建并配置 Treeview 表格控件."""
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

    # ========== Excel 页面方法 ==========

    def _refresh_excel_tree(self, parent) -> None:
        """刷新 Excel 导入导出页面的表格，包含列头和行数据.

        Args:
            parent: 父容器 Frame，用于放置表格组件。

        Note:
            每次刷新会先销毁旧表格容器，再重新创建表头和数据行。
        """
        # ====== 1. 清理旧的表格容器 ======
        if hasattr(self, "excel_frame"):
            self.excel_frame.destroy()
            delattr(self, "excel_frame")

        # ====== 2. 重新创建表格容器 ======
        self.excel_frame = tk.Frame(parent, bg="white")
        self.excel_frame.pack(fill="both", expand=True)

        # ====== 3. 获取最新的科目列表 ======
        subjects = self.dm.subjects
        columns = ["学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        widths = [100, 90, 90] + self._calc_subject_widths(subjects) + [80, 80]

        # ====== 4. 创建新的 Treeview ======
        self.ex_tree = ttk.Treeview(
            self.excel_frame, columns=columns, show="headings", height=16
        )
        v_scroll = ttk.Scrollbar(
            self.excel_frame, orient="vertical", command=self.ex_tree.yview
        )
        h_scroll = ttk.Scrollbar(
            self.excel_frame, orient="horizontal", command=self.ex_tree.xview
        )
        self.ex_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # ====== 5. 设置列宽和标题 ======
        for col, width in zip(columns, widths):
            self.ex_tree.heading(col, text=col)
            self.ex_tree.column(col, width=width, anchor="center")

        # ====== 6. 配置斑马纹样式 ======
        self.ex_tree.tag_configure("odd", background="#F8FAFC")
        self.ex_tree.tag_configure("even", background="#FFFFFF")

        # ====== 7. 放置滚动条 ======
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.ex_tree.pack(fill="both", expand=True)

        # ========== ✅ 核心修改：无数据时填充 30 个空行 ==========
        # 获取所有学生数据
        student_items = list(self.dm.students.items())

        if not student_items:
            # 如果没有学生数据，生成 30 个空行
            for i in range(30):
                # 生成对应列数的空值（全部为空字符串）
                empty_vals = ["" for _ in range(len(columns))]
                # 应用斑马纹样式
                tag = "odd" if i % 2 == 0 else "even"
                # 插入空行
                self.ex_tree.insert("", "end", values=empty_vals, tags=(tag,))
            # 填充完空行后直接返回，不再执行下面的数据插入
            self.win.update_idletasks()
            return
        # ========================================================

        # ========== 以下代码只在有数据时执行 ==========
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

        # 强制刷新布局
        self.win.update_idletasks()

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
            messagebox.showerror("错误", "模板创建失败")

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
            messagebox.showerror("导入失败", error)
        else:
            # ====== 用 try...except 包裹刷新逻辑，防止程序静默崩溃 ======
            try:
                self._refresh_all_pages()
                self._update_status()
                self._refresh_subject_ui()
            except Exception as e:
                import traceback

                traceback.print_exc()  # 在终端打印详细报错信息
                logger.warning(f"导入数据后刷新界面时出现可忽略的错误: {e}")
            # ===========================================================

            messagebox.showinfo("完成", f"成功导入 {count} 名学生")
            logger.info("Excel 导入成功: %s (%d 条)", filepath, count)

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

    def _show_export_dialog(self, export_type: str) -> None:
        """显示导出选项对话框（全部或指定班级）.

        Args:
            export_type: 导出类型，取值为 "excel" 或 "csv"。

        弹窗固定在主窗口左上区域，用户可选择导出全部班级，
        或从下拉框中选择特定班级进行导出。
        """
        dialog = tk.Toplevel(self.win)
        dialog.title("导出选项")
        dialog.geometry("380x230")
        dialog.grab_set()
        dialog.transient(self.win)

        # 将弹窗定位到主窗口左上角区域（美观对齐）
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

        # 全部班级选项
        tk.Radiobutton(
            dialog,
            text="导出全部班级",
            variable=selected_class,
            value="全部",
            font=("微软雅黑", 13),
        ).pack(anchor="w", padx=40, pady=4)

        # 指定班级选项 + 下拉框
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
        """执行数据导出."""
        class_combo.pack(side="left", padx=5)

        def do_export() -> None:
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

        弹出保存对话框，根据参数决定导出全部数据或仅导出指定班级，
        导出成功后更新状态栏提示。
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=get_excel_filename(),
        )
        if not filepath:
            return

        if not class_name:
            # 导出全部
            if export_to_excel(filepath, self.dm):
                self._show_status("Excel 导出成功", "ok")
                logger.info("Excel 导出成功: %s", filepath)
            else:
                logger.error("Excel 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")
        else:
            # 导出指定班级：创建临时数据管理器副本
            if self._export_excel_by_class(filepath, class_name):
                self._show_status(f"Excel 导出成功（{class_name}）", "ok")
                logger.info("Excel 导出成功（%s）: %s", class_name, filepath)
            else:
                logger.error("Excel 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")

    def _do_export_csv(self, class_name: str = "") -> None:
        """执行 CSV 导出（可选按班级过滤）.

        Args:
            class_name: 要导出的班级名称。空字符串表示导出全部班级。

        弹出保存对话框，根据参数决定导出全部数据或仅导出指定班级，
        导出成功后更新状态栏提示。
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=get_csv_filename(),
        )
        if not filepath:
            return

        if not class_name:
            # 导出全部
            if export_to_csv(filepath, self.dm):
                self._show_status("CSV 导出成功", "ok")
                logger.info("CSV 导出成功: %s", filepath)
            else:
                logger.error("CSV 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")
        else:
            # 导出指定班级
            if self._export_csv_by_class(filepath, class_name):
                self._show_status(f"CSV 导出成功（{class_name}）", "ok")
                logger.info("CSV 导出成功（%s）: %s", class_name, filepath)
            else:
                logger.error("CSV 导出失败: %s", filepath)
                messagebox.showerror("错误", "导出失败")

    def _export_excel_by_class(self, filepath: str, class_name: str) -> bool:
        """按班级导出 Excel.

        Args:
            filepath: 导出的文件保存路径。
            class_name: 要过滤并导出的班级名称。

        Returns:
            True 表示导出成功，False 表示导出失败。

        使用 openpyxl 创建新工作簿，仅包含指定班级的学生，
        按总分降序排列，并生成排名、等级等统计信息。
        """
        try:
            import openpyxl

            wb = openpyxl.Workbook()
            ws = wb.active
            if ws is None:
                return False
            ws.title = f"{class_name}成绩表"

            subjects = list(self.dm.subjects)
            ws.append(
                ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分", "等级"]
            )

            # 过滤指定班级的学生并排序
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

        使用 csv 模块写入 UTF-8-SIG 编码文件，仅包含指定班级的学生，
        按总分降序排列，并生成排名等统计信息。
        """
        try:
            import csv

            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                subjects = list(self.dm.subjects)
                header = (
                    ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
                )
                writer.writerow(header)

                # 过滤指定班级的学生并排序
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

    # ========== 管理页面方法 ==========

    def _refresh_manage_tree(self) -> None:
        """刷新成绩管理表格，应用班级过滤、成绩范围过滤、排序和颜色预警.

        Raises:
            tk.TclError: 当表格控件已被销毁时捕获并静默返回。
        """
        try:
            # 检查表格是否存在且有效
            if not self.mg_tree.winfo_exists():
                return  # 表格已被销毁，说明当前不在管理页面，直接返回
        except (tk.TclError, AttributeError):
            return  # 表格不存在，直接返回，避免在非管理页面重建

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

            vals = (
                [sid, stu["name"], stu.get("class", "")]
                + [stu["scores"].get(s, "-") for s in self.dm.subjects]
                + [st["total"], st["avg"]]
            )

            # 成绩范围过滤
            if filter_score != "全部":
                score_vals = vals[3:3 + subject_count]
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
                    except (ValueError, TypeError):
                        pass

                if all_empty:
                    continue
                if filter_score == "不及格 (<60)" and (not pass_ok):  # 任一 < 60
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

        # ========== 核心修改：如果没有数据，生成 30 个空行 ==========
        if not rows:
            for i in range(30):
                # 生成 30 列的空值（对应 "学号", "姓名", "班级", ... "总分", "平均分"）
                empty_vals = ["" for _ in range(len(columns))]
                # 应用斑马纹样式
                tag = "odd" if i % 2 == 0 else "even"
                # 插入空行
                self.mg_tree.insert("", "end", values=empty_vals, tags=(tag,))
            return  # 填充完空行后直接返回，不再执行下面的排序和插入
        # ============================================================

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
            score_vals = vals[3:3 + subject_count]
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
                except (ValueError, TypeError):
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
            status_text = f"{' '.join(parts)}：共 {shown}/{total} 人"
            self._show_status(status_text, "info")
        else:
            self._show_status(f"全部学生共 {total} 人", "info")

    @staticmethod
    def _mg_sort_key(vals: list, col_idx: int) -> float | str:
        """生成排序键值（数字优先，文本兜底）."""
        v = vals[col_idx]
        if v == "-" or v == "" or v is None:
            return -1
        try:
            return float(v)
        except (ValueError, TypeError):
            return str(v).lower()

    def _manage_sort_tree(self, col: str) -> None:
        """按指定列头排序（切换升降序）."""
        if self._mg_sort_col == col:
            self._mg_sort_asc = not self._mg_sort_asc
        else:
            self._mg_sort_col = col
            self._mg_sort_asc = True  # 默认降序（高分在前）
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

        # 编辑姓名或班级
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
            """提交成绩编辑."""

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
        """编辑成绩管理表格中选中的学生基本信息（姓名和班级）."""
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
        cls = simpledialog.askstring(
            "班级", "新班级：", initialvalue=stu.get("class", "")
        )
        if cls is None:
            return
        try:
            self.dm.upd_stu(sid, name, cls)
            self._refresh_manage_tree()
            self._show_status("信息已更新", "ok")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _manage_delete_selected(self) -> None:
        """删除成绩管理表格中选中的学生记录."""
        selected = self.mg_tree.selection()
        if not selected:
            return

        # 获取所有选中的学号
        selected_sids = [self.mg_tree.item(item, "values")[0] for item in selected]

        # 确认删除
        if messagebox.askyesno(
            "确认删除", f"确定要删除选中的 {len(selected_sids)} 名学生吗？"
        ):
            for sid in selected_sids:
                self.dm.del_stu(sid)
            self._refresh_manage_tree()
            self._update_status()
            self._show_status(f"已删除 {len(selected_sids)} 名学生", "ok")

    def _reset_all_data(self) -> None:
        """重置所有数据到初始状态（删除所有学生、科目、成绩."""
        if messagebox.askyesno(
            "确认重置",
            "确定要删除所有数据并重置系统吗？\n此操作将删除所有学生、科目和成绩，且不可撤销！",
        ):
            # 1. 清空 DataManager 的数据
            self.dm.data = {"subjects": [], "students": {}, "history": []}

            # 2. 保存重置后的数据
            self.dm.save()

            # 3. 强制刷新成绩管理表格的表头（关键修复）
            if hasattr(self, "mg_tree"):
                # 获取当前表格的父容器，以便稍后重新创建
                parent = self.mg_tree.master
                # 销毁旧的表格（包括表头）
                self.mg_tree.destroy()

                # 根据新的空科目列表重新创建表格
                new_subjects = self.dm.subjects
                columns = ["学号", "姓名", "班级"] + new_subjects + ["总分", "平均分"]
                base_widths = [110, 90, 90]
                widths = (
                    base_widths + self._calc_subject_widths(new_subjects) + [80, 80]
                )

                # 创建新的 Treeview
                self.mg_tree = ttk.Treeview(
                    parent, columns=columns, show="headings", height=18
                )
                # 重新配置预警标签
                self.mg_tree.tag_configure("fail", foreground="#EF4444")
                self.mg_tree.tag_configure("warn", foreground="#F59E0B")
                self.mg_tree.tag_configure("good", foreground="#10B981")
                self.mg_tree.tag_configure("empty_all", foreground="#9CA3AF")
                # 重新配置斑马纹
                self.mg_tree.tag_configure("odd", background="#F8FAFC")
                self.mg_tree.tag_configure("even", background="#FFFFFF")
                # 重新绑定双击事件
                self.mg_tree.bind("<Double-1>", self._manage_cell_double_click)

                # 重新设置列宽和标题
                for col, width in zip(columns, widths):
                    self.mg_tree.heading(col, text=col)
                    """执行搜索查询."""
                    self.mg_tree.column(col, width=width, anchor="center")

                # 重新绑定列头点击排序
                for col in columns:
                    self.mg_tree.heading(
                        col, command=lambda c=col: self._manage_sort_tree(c)
                    )

                # 将新的表格放入父容器
                self.mg_tree.pack(fill="both", expand=True)

            # 4. 刷新所有页面（包括新创建的成绩管理表格）
            self._refresh_all_pages()

            # 5. 更新状态栏
            self._update_status()
            self._show_status("系统已重置为初始状态", "ok")

            # 6. 记录日志
            logger.info("所有数据已重置")
    """显示搜索结果详情."""

    # ========== 查询页面方法 ==========

    def _search_execute(self) -> None:
        """执行搜索查询."""
        keyword = self.se_var.get().strip()
        results = self.dm.search(keyword) if keyword else list(self.dm.students.keys())
        results.sort()
        self.se_list.delete(0, "end")
        for sid in results:
            stu = self.dm.get_stu(sid)
            if stu:
                self.se_list.insert(
                    "end", f"{sid} | {stu['name']} | {stu.get('class', '')}"
                )
        if len(results) == 1:
            self.se_list.selection_set(0)
            self._search_show_detail(None)

    def _refresh_search_list(self) -> None:
        """清空搜索框并重新执行搜索，显示所有学生数据."""
        self.se_var.set("")
        self._search_execute()

    def _search_show_detail(self, event: tk.Event) -> None:
        """显示搜索结果详情."""
        selected = self.se_list.curselection()
        if not selected:
            return
        sid = self.se_list.get(selected[0]).split("|")[0].strip()
        """显示搜索历史记录."""
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
                self.stt.insert(
                    "", "end", values=(subject, score, level), tags=(base_tag, tag)
                )

    def _search_show_history(self, student_id: str) -> None:
        """显示搜索历史记录."""
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

        # 将弹窗定位到主窗口左上角区域（美观对齐）
        self.win.update_idletasks()
        win_x = self.win.winfo_x()
        win_y = self.win.winfo_y()
        dialog.geometry(f"+{win_x + 210}+{win_y + 200}")

        dialog.grab_set()

        tk.Label(
            dialog,
            text=f"学生 {student_id} 的成绩修改历史",
            font=("微软雅黑", 12, "bold"),
        ).pack(pady=8)

        if not history:
            tk.Label(
                dialog, text="暂无修改记录", font=("微软雅黑", 11), fg="#64748B"
            ).pack(expand=True)
            ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=8)
            return

        columns = ["时间", "科目", "旧成绩", "新成绩"]
        widths = [140, 100, 80, 80]
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=14)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        """删除选中的搜索记录."""
        tree.tag_configure("odd", background="#F8FAFC")
        tree.tag_configure("even", background="#FFFFFF")

        for i, record in enumerate(history):
            base_tag = "odd" if i % 2 == 0 else "even"
            old_val = record.get("old")
            new_val = record.get("new")
            old_str = str(old_val) if old_val is not None else "—"
            new_str = str(new_val) if new_val is not None else "—"
            tree.insert(
                """刷新科目相关界面."""
                "",
                "end",
                values=(
                    record.get("time", "")[:16],
                    record.get("subject", ""),
                    old_str,
                    new_str,
                ),
                tags=(base_tag,),
            )

        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=8)

    def _search_delete_selected(self) -> None:
        """删除选中的搜索记录."""
        selected = self.se_list.curselection()
        if not selected:
            return
        sid = self.se_list.get(selected[0]).split("|")[0].strip()
        if messagebox.askyesno("确认", f"确定删除 {sid} 吗？"):
            self.dm.del_stu(sid)
            self._refresh_search_list()
            self._show_status(f"已删除 {sid}", "warn")

    def _refresh_subject_ui(self) -> None:
        """刷新科目相关界面."""
        subjects = self.dm.subjects
        """清空图表区域."""
        if hasattr(self, "an_cb"):
            self.an_cb["values"] = subjects
        if hasattr(self, "ch_cb"):
            self.ch_cb["values"] = subjects
        """显示指定类型的图表."""
        if hasattr(self, "mg_tree"):
            self._refresh_manage_tree()
            widths = self._calc_subject_widths(subjects)
            cols = self.mg_tree["columns"]
            for i, w in enumerate(widths, start=3):
                if i < len(cols):
                    self.mg_tree.column(cols[i], width=w, minwidth=50)
            """绘制总分排名图."""
            # 更新列头排序绑定
            for col in cols:
                self.mg_tree.heading(
                    col, command=lambda c=col: self._manage_sort_tree(c)
                )
        if hasattr(self, "mg_class_cb"):
            self.mg_class_cb["values"] = ["全部班级"] + self.dm.classes
        if hasattr(self, "ex_tree") and hasattr(self, "_excel_parent"):
            self._refresh_excel_tree(self._excel_parent)

    # ========== 图表页面方法 ==========

    def _clear_chart_area(self) -> None:
        """清空图表区域."""
        for w in self.ct.winfo_children():
            w.destroy()

    def _show_chart(self, figure: "Figure") -> None:
        """显示指定类型的图表."""
        self._clear_chart_area()
        canvas = FigureCanvasTkAgg(figure, self.ct)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(figure)

    def _chart_total_ranking(self) -> None:
        """绘制总分排名图."""
        ranking = self.dm.ranking()
        if not ranking:
            """绘制平均分对比图."""
            messagebox.showinfo("提示", "暂无学生数据")
            return
        """获取对应颜色值."""
        fig = Figure(figsize=(max(7, len(ranking) * 0.6), 4))
        ax = fig.add_subplot(111)

        def get_color(x):
            if x["rank"] == 1:
                return "#FCD34D"
            elif x["rank"] == 3:
                return "#F97316"
            else:
                return "#3B82F6"

        bar_colors = [get_color(x) for x in ranking]
        ax.bar(
            [x["name"] for x in ranking],
            [x["total"] for x in ranking],
            color=bar_colors,
        )
        ax.set_title("总分排名")
        fig.tight_layout()
        self._show_chart(fig)

    """绘制成绩分布直方图."""
    def _chart_avg_comparison(self) -> None:
        """绘制平均分对比图."""
        ranking = self.dm.ranking(by="avg")
        if not ranking:
            messagebox.showinfo("提示", "暂无学生数据")
            return
        fig = Figure(figsize=(max(7, len(ranking) * 0.6), 4))
        ax = fig.add_subplot(111)
        avgs = [x["avg"] for x in ranking]
        bar_colors = [
            (
                "#10B981"
                if v >= 90
                else "#3B82F6" if v >= 75 else "#F59E0B" if v >= 60 else "#EF4444"
            )
            for v in avgs
        ]
        ax.bar([x["name"] for x in ranking], avgs, color=bar_colors)
        ax.axhline(60, color="red", ls="--")
        ax.axhline(90, color="green", ls="--")
        ax.set_title("平均分对比")
        ax.set_ylim(0, 105)
        fig.tight_layout()
        self._show_chart(fig)

    """绘制成绩雷达图."""
    def _chart_histogram(self) -> None:
        """绘制成绩分布直方图."""
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
        ax.hist(
            analysis["scores"],
            bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            color="#3B82F6",
        )
        ax.axvline(
            analysis["avg"], color="red", ls="--", label=f"均分 {analysis['avg']}"
        )
        """绘制成绩箱线图."""
        ax.axvline(60, color="orange", ls=":", label="及格线")
        ax.set_title(f"{subject} 成绩分布")
        ax.legend()
        self._show_chart(fig)

    def _chart_radar(self) -> None:
        """绘制成绩雷达图."""
        if len(self.dm.subjects) < 3:
            messagebox.showinfo("提示", "至少需要 3 个科目才能生成雷达图")
            return
        avgs = [
            self.dm.analyze_subject(s)["avg"] if self.dm.analyze_subject(s) else 0
            for s in self.dm.subjects
        ]
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
        """绘制成绩箱线图."""
        if not self.dm.subjects:
            messagebox.showinfo("提示", "暂无科目数据")
            return
        data = []
        labels = []
        for s in self.dm.subjects:
            """添加班级."""
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
        """添加班级."""
        name = simpledialog.askstring("添加班级", "请输入班级名称：")
        if not name:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("提示", "班级名称不能为空")
            return
        try:
            existing = [
                s for s in self.dm.data["students"].values() if s.get("class") == name
            ]
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
        """刷新班级列表表格数据，展示班级统计信息.

        Note:
            若表格控件尚未创建，会直接返回不执行任何操作。
        """
        # 1. 清空现有数据
        if not hasattr(self, "cl_tree") or not self.cl_tree:
            return  # 表格还没创建，直接返回
        self.cl_tree.delete(*self.cl_tree.get_children())

        classes = self.dm.classes

        # ========== 核心修改开始 ==========
        if not classes:
            # 如果没有班级数据，自动填充 30 个空行
            for i in range(30):
                # 循环产生斑马纹
                tag = "odd" if i % 2 == 0 else "even"
                # 根据定义的6个列填充空值：
                # ["班级名称", "学生人数", "平均分", "最高分", "最低分", "操作"]
                """班级列表双击回调."""
                empty_vals = ["", "", "", "", "", ""]
                self.cl_tree.insert("", "end", values=empty_vals, tags=(tag,))
            return  # 填充完直接返回，不再显示下方的文字
        # ========== 核心修改结束 ==========

        # --- 以下代码是在"有真实班级数据"时执行的 ---
        for idx, cls_name in enumerate(classes):
            stats = self.dm.get_class_stats(cls_name)
            if stats:
                """显示班级详情."""
                base_tag = "odd" if idx % 2 == 0 else "even"
                self.cl_tree.insert(
                    "",
                    "end",
                    values=(
                        cls_name,
                        stats["count"],
                        stats["total_avg"],
                        stats["max_total"],
                        stats["min_total"],
                        "查看详情",  # 对应的"操作"列
                    ),
                    tags=(base_tag,),
                )

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

        # 将弹窗定位到主窗口左上角区域（美观对齐）
        self.win.update_idletasks()
        win_x = self.win.winfo_x()
        win_y = self.win.winfo_y()
        dialog.geometry(f"+{win_x + 210}+{win_y + 200}")
        tk.Label(dialog, text=f"🏫 {class_name}", font=("微软雅黑", 14, "bold")).pack(
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
                font=("微软雅黑", 10),
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
        tree.tag_configure("odd", background="#F8FAFC")
        tree.tag_configure("even", background="#FFFFFF")
        tree.tag_configure("fail", foreground="#EF4444")
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
            messagebox.showwarning("提示", "请先选中一个班级")
            return
        vals = self.cl_tree.item(selected[0], "values")
        if not vals or not vals[0]:
            messagebox.showwarning("提示", "请先选中一个班级")
            return
        self._class_do_delete(vals[0])

    def _class_do_delete(self, class_name: str) -> None:
        """执行删除班级操作（将该班级所有学生的班级字段清空）."""
        if not class_name:
            return
        if not messagebox.askyesno(
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
            self.dm.save()
            messagebox.showinfo(
                "删除成功",
                f"班级「{class_name}」已删除，共清空 {count} 名学生的班级信息",
            )
            self._refresh_class_tree()
        except Exception as e:
            messagebox.showerror("错误", f"删除班级失败: {e}")

    # ========== 仪表盘刷新方法 ==========

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
                    bar_colors = [
                        "#6366F1",
                        "#8B5CF6",
                        "#3B82F6",
                        "#10B981",
                        "#F59E0B",
                        "#EF4444",
                    ][: len(avgs)]
                    bars = ax.bar(self.dm.subjects, avgs, color=bar_colors, width=0.6)
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
                    ax.axhline(60, color="#EF4444", ls="--", alpha=0.7, label="及格线")
                    ax.set_title("科目均分对比", fontsize=12, fontweight="bold", pad=10)
                    ax.legend(fontsize=8)
                    fig.tight_layout(pad=1.0)
                    canvas = FigureCanvasTkAgg(fig, self.da_subj_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
                except Exception as e:
                    logger.error("刷新仪表盘图表失败: %s", e)
                    tk.Label(
                        self.da_subj_frame, text=f"图表加载失败: {e}", bg="white"
                    ).pack()
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
                        font=("微软雅黑", 10),
                        bg="white",
                        anchor="w",
                    ).pack(fill="x", pady=2)
            else:
                tk.Label(
                    self.da_hist_frame,
                    text="暂无修改记录",
                    font=("微软雅黑", 10),
                    bg="white",
                    fg="#9CA3AF",
                ).pack(pady=10)

    # ========== 账号管理页面 ==========
