"""登录窗口模块 - Login Window for Student Grade Management System.

提供图形化登录界面，支持管理员、教师、学生三种角色切换登录。

本模块基于 ``customtkinter`` 和 ``tkinter`` 构建，包含背景图片渲染、
角色选择标签栏、账号密码输入框以及登录验证逻辑。登录成功后通过
``run()`` 方法返回包含角色和用户信息的结果字典，供主程序入口进行
后续界面分发。

Attributes:
    ctk: customtkinter 模块实例，已全局设置主题为 Light + blue。
"""

import logging
import os
import sys

# ------------------------------------------------------------------
# 运行时路径配置
# ------------------------------------------------------------------
# 确保项目根目录在导入路径中（允许直接运行本文件进行调试）
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# 以下导入依赖上方的 sys.path 设置，需在路径配置后执行
import tkinter as tk  # noqa: E402
from tkinter import messagebox, Canvas  # noqa: E402

import customtkinter as ctk  # noqa: E402

# 尝试导入 Pillow，若缺失则设置标志并继续运行
PIL_OK: bool = False
try:
    from PIL import Image, ImageTk  # noqa: E402

    PIL_OK = True
except ImportError:
    pass

from modules.data_manager import DataManager  # noqa: E402

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# 全局主题配置
# ------------------------------------------------------------------
# 设置 customtkinter 外观模式与默认配色主题
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    """登录窗口类.

    提供管理员、教师、学生三种角色登录入口，
    验证成功后返回角色信息和用户标识。

    界面布局::

        +-------------------------------+
        |  左侧背景图 + 系统标题文字      |
        |                               |  +------------------+
        |                               |  | 角色标签栏        |
        |                               |  | 账号输入框        |
        |                               |  | 密码输入框        |
        |                               |  | 登录按钮          |
        +-------------------------------+  +------------------+

    Attributes:
        dm: DataManager 实例，用于账号密码验证。
        login_result: 登录结果字典，包含 success、role、user 字段。
        current_role: 当前选中的角色字符串（admin/teacher/student）。
    """

    def __init__(self, data_manager: DataManager | None = None):
        """初始化登录窗口，加载界面元素和背景图片.

        初始化流程：
        1. 设置窗口标题、尺寸、图标并居中。
        2. 预加载左侧背景图。
        3. 构建右侧白色登录卡片，包含角色选择、Logo、输入框和按钮。
        4. 默认切换到管理员角色，并在短暂延迟后显示窗口。

        Args:
            data_manager: 数据管理器实例，用于验证教师和学生账号。
                          为 ``None`` 时自动创建新的 DataManager 实例。
        """
        super().__init__()

        self.title("登录 - 学生成绩管理系统")
        self.geometry("900x550")
        self.resizable(False, False)

        project_root = _parent_dir
        # 尝试加载窗口图标
        icon_path = os.path.join(project_root, "img", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                logger.warning("图标加载失败: %s (路径: %s)", e, icon_path)

        # 保存数据管理器实例和登录结果初始状态
        self.dm = data_manager if data_manager else DataManager()
        self.login_result = {"success": False}
        self.current_role = "admin"

        # 窗口居中计算
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 550) // 2
        self.geometry(f"900x550+{x}+{y}")

        # 隐藏窗口，后台完成全部渲染后再一次性显示，避免闪烁
        self.withdraw()

        # 预加载背景图片资源
        self.image_path = os.path.join(project_root, "img", "bg.jpeg")
        self.bg_image = None
        self.photo_image = None
        self._preload_background()

        # 全屏 Canvas 作为左侧背景图的绘制载体
        self.canvas = Canvas(self, bg="#2C3E50", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 登录卡片：右侧白色矩形区域
        self.card = ctk.CTkFrame(
            self, fg_color="white", corner_radius=0, width=400, height=500
        )

        # 角色选择标签栏（先创建组件）
        self.role_frame = tk.Frame(self.card, bg="white")
        self.role_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.role_frame.columnconfigure(0, weight=1)
        self.role_frame.columnconfigure(1, weight=1)
        self.role_frame.columnconfigure(2, weight=1)

        self.role_buttons = {}
        roles = [
            ("admin", "管理员"),
            ("teacher", "教师"),
            ("student", "学生"),
        ]
        for col, (role_key, role_text) in enumerate(roles):
            btn = tk.Label(
                self.role_frame,
                text=role_text,
                font=("微软雅黑", 12),
                bg="white",
                fg="#495057",
                cursor="hand2",
            )
            btn.grid(row=0, column=col, sticky="ew", padx=5)
            btn.bind("<Button-1>", lambda e, r=role_key: self._switch_role(r))
            self.role_buttons[role_key] = btn

        # 标题 Logo
        logo_path = os.path.join(project_root, "img", "横向logo.png")
        if PIL_OK and os.path.exists(logo_path):
            logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(180, 45),
            )
            self.title_label = ctk.CTkLabel(self.card, image=logo_img, text="")
        else:
            self.title_label = ctk.CTkLabel(
                self.card,
                text="学生成绩管理系统",
                font=("微软雅黑", 18, "bold"),
                text_color="#2C3E50",
            )
        self.title_label.pack(pady=(10, 20))

        # 用户名/工号/学号输入框
        self.account_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="请输入用户名",
            height=40,
            corner_radius=10,
        )
        self.account_entry.pack(pady=10, padx=25, fill="x")

        # 密码输入框
        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="请输入密码",
            height=40,
            corner_radius=10,
            show="*",
        )
        self.password_entry.pack(pady=10, padx=25, fill="x")

        # 登录按钮
        self.login_button = ctk.CTkButton(
            self.card,
            text="登录",
            font=("微软雅黑", 14, "bold"),
            height=40,
            corner_radius=10,
            fg_color="#0374BF",
            hover_color="#2980B9",
            command=self._login_action,
        )
        self.login_button.pack(pady=20, padx=90, fill="x")

        # ====== 重要：UI组件已全部创建，现在可以安全切换角色 ======
        self._switch_role("admin")

        # 强制设置输入框高度，解决退出登录后样式异常
        self.account_entry.configure(height=40)
        self.password_entry.configure(height=40)
        self.update_idletasks()

        # 渲染完成后一次性显示
        self.after(10, self._prepare_and_show)

    def _preload_background(self):
        """预加载背景图片，避免显示时卡顿."""
        if not PIL_OK:
            self.bg_image = None
            return
        try:
            if os.path.exists(self.image_path):
                self.bg_image = Image.open(self.image_path)
        except Exception as e:
            print(f"图片加载失败: {e}")
            self.bg_image = None

    def _prepare_and_show(self):
        """准备背景、文字和卡片布局，然后显示窗口.

        根据当前窗口实际尺寸（或回退到默认值）绘制左侧背景图与系统标题文字，
        并将登录卡片放置在右侧居中位置。
        """
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10:
            w, h = 900, 550

        self.canvas.delete("all")

        # 绘制全屏背景
        if PIL_OK and self.bg_image:
            resized_img = self.bg_image.resize((w, h), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(resized_img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        else:
            self.canvas.config(bg="#2C3E50")

        # 左侧文字
        text_x = w // 3.5
        text_y = h // 2
        self.canvas.create_text(
            text_x,
            text_y - 50,
            text="学生成绩管理系统",
            font=("微软雅黑", 26, "bold"),
            fill="white",
        )
        self.canvas.create_text(
            text_x,
            text_y + 10,
            text="登录以管理你的班级、成绩与数据",
            font=("微软雅黑", 12),
            fill="#EBEBEB",
        )

        # 将登录卡片放置到右侧居中位置
        self.card.place(relx=0.75, rely=0.5, anchor="center")
        self.card.lift()

        self.update()
        self.after(50, self._show_window)

    def _show_window(self):
        """解除隐藏，显示窗口并获取焦点.

        显示窗口后多次强制刷新输入框高度，确保 customtkinter 渲染完成后
        输入框尺寸不会被压缩。
        """
        self.deiconify()
        self.lift()
        self.focus_force()
        # 强制刷新输入框高度
        self.account_entry.configure(height=40)
        self.password_entry.configure(height=40)
        self.update_idletasks()
        self.after(100, self._refresh_placeholders)
        # 延迟再次强制恢复高度，确保占位符刷新后不被压缩
        self.after(250, self._fix_entry_height)

    def _fix_entry_height(self) -> None:
        """修复输入框高度异常.

        在窗口显示后再次强制设置输入框高度，处理 customtkinter 在某些情况下
        会回退高度的问题。
        """
        self.account_entry.configure(height=40)
        self.password_entry.configure(height=40)
        self.update_idletasks()

    def _refresh_placeholders(self):
        """刷新输入框占位符，使其立即显示（解决占位符不同步问题）。

        通过临时禁用再启用输入框的方式强制 customtkinter 内部状态刷新，
        确保占位符文字能够正确呈现。
        """
        placeholders = {
            "admin": ("请输入用户名", "请输入密码"),
            "teacher": ("请输入教师工号", "请输入密码"),
            "student": ("请输入学号", "请输入密码"),
        }
        acc_ph, pwd_ph = placeholders.get(
            self.current_role, ("请输入用户名", "请输入密码")
        )
        self.account_entry.configure(placeholder_text=acc_ph)
        self.password_entry.configure(placeholder_text=pwd_ph)
        self.update_idletasks()
        # 强制刷新：临时禁用再启用，使内部 Canvas 重绘
        self.account_entry.configure(state="disabled")
        self.account_entry.configure(state="normal")
        self.password_entry.configure(state="disabled")
        self.password_entry.configure(state="normal")

        # 强制恢复输入框高度
        self.account_entry.configure(height=40)
        self.password_entry.configure(height=40)
        self.update_idletasks()

    def _switch_role(self, role: str) -> None:
        """切换登录角色.

        更新角色标签栏的选中样式，并根据新角色切换输入框占位符，
        同时清空已输入的账号和密码。

        Args:
            role: 目标角色标识，可选 "admin"、"teacher"、"student"。
        """
        self.current_role = role
        # 更新角色按钮样式：选中项加粗并变色，其余恢复默认
        for key, btn in self.role_buttons.items():
            if key == role:
                btn.configure(font=("微软雅黑", 12, "bold"), fg="#0374BF")
            else:
                btn.configure(font=("微软雅黑", 12), fg="#495057")
        placeholders = {
            "admin": ("请输入用户名", "请输入密码"),
            "teacher": ("请输入教师工号", "请输入密码"),
            "student": ("请输入学号", "请输入密码"),
        }
        acc_ph, pwd_ph = placeholders.get(role, ("请输入用户名", "请输入密码"))

        # 清空输入框内容，避免切换角色后残留上一次输入
        self.account_entry.delete(0, "end")
        self.password_entry.delete(0, "end")

        # 设置占位符
        self.account_entry.configure(placeholder_text=acc_ph)
        self.password_entry.configure(placeholder_text=pwd_ph)

        # 强制刷新：临时禁用再启用（使内部状态重置）
        self.account_entry.configure(state="disabled")
        self.account_entry.configure(state="normal")
        self.password_entry.configure(state="disabled")
        self.password_entry.configure(state="normal")

        # 强制恢复输入框高度
        self.account_entry.configure(height=40)
        self.password_entry.configure(height=40)
        self.update_idletasks()

        # 将焦点移到登录按钮，避免输入框立即获取焦点导致占位符异常
        self.login_button.focus_set()

    def _login_action(self):
        """根据当前角色验证账号密码，成功则设置登录结果.

        从输入框读取账号和密码，调用 ``_verify_login()`` 进行验证。
        验证成功时关闭登录窗口并保存结果；失败时弹出错误提示。
        """
        account = self.account_entry.get().strip()
        password = self.password_entry.get().strip()
        result = self._verify_login(account, password)
        if result["success"]:
            self.login_result = result
            self.destroy()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误！")

    def _verify_login(self, account: str, password: str) -> dict:
        """根据角色执行对应的验证逻辑.

        分别调用 DataManager 中的管理员、教师、学生认证方法，
        构造统一格式的返回字典。

        Args:
            account: 账号（管理员用户名 / 教师工号 / 学号）。
            password: 密码。

        Returns:
            包含 ``success``（bool）、``role``（str）、``user``（dict） 字段的字典。
        """
        role = self.current_role
        if role == "admin":
            if self.dm.authenticate_admin(account, password):
                return {
                    "success": True,
                    "role": "admin",
                    "user": {"username": account},
                }
        elif role == "teacher":
            teacher = self.dm.authenticate_teacher(account, password)
            if teacher:
                return {
                    "success": True,
                    "role": "teacher",
                    "user": teacher,
                }
        elif role == "student":
            student = self.dm.authenticate_student(account, password)
            if student:
                return {
                    "success": True,
                    "role": "student",
                    "user": student,
                }
        return {"success": False}

    def run(self) -> dict:
        """启动窗口主循环，返回登录结果.

        阻塞调用，直到用户登录成功、取消登录或关闭窗口。

        Returns:
            包含 ``success``、``role``、``user`` 字段的字典。
        """
        self.mainloop()
        return self.login_result


if __name__ == "__main__":
    app = LoginWindow()
    result = app.run()
    if result["success"]:
        print(f"登录成功: {result['role']} - {result['user']}")
    else:
        print("登录已取消")
