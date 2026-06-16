"""登录窗口模块 - Login Window for Student Grade Management System."""

import os
import sys

# 确保项目根目录在导入路径中（允许直接运行本文件）
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# 以下导入依赖上方的 sys.path 设置，需在路径配置后执行
import tkinter as tk  # noqa: E402
from tkinter import messagebox, Canvas  # noqa: E402

import customtkinter as ctk  # noqa: E402
from PIL import Image, ImageTk  # noqa: E402

from modules.data_manager import DataManager  # noqa: E402

# 设置主题
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    """登录窗口类.

    提供管理员、教师、学生三种角色登录入口，
    验证成功后返回角色信息和用户标识。
    """

    def __init__(self, data_manager: DataManager | None = None):
        """初始化登录窗口，加载界面元素和背景图片.

        Args:
            data_manager: 数据管理器实例，用于验证教师和学生账号。
        """
        super().__init__()

        self.title("登录 - 学生成绩管理系统")
        self.geometry("900x550")
        self.resizable(False, False)

        project_root = _parent_dir
        icon_path = os.path.join(project_root, "img", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass  # 忽略图标加载失败

        self.dm = data_manager if data_manager else DataManager()
        self.login_result = {"success": False}
        self.current_role = "admin"

        # 窗口居中
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 550) // 2
        self.geometry(f"900x550+{x}+{y}")

        # 隐藏窗口，后台渲染
        self.withdraw()

        self.image_path = os.path.join(project_root, "img", "bg.jpeg")
        self.bg_image = None
        self.photo_image = None
        self._preload_background()

        # 全屏 Canvas
        self.canvas = Canvas(self, bg="#2C3E50", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 登录卡片
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

        # 标题
        from PIL import Image

        # 定义Logo路径
        logo_path = os.path.join(project_root, "img", "横向logo.png")
        # 初始化CTkImage（适配深浅主题，统一尺寸）
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(180, 45),
            )
        else:
            logo_img = None

        self.title_label = ctk.CTkLabel(self.card, image=logo_img, text="")
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
        try:
            if os.path.exists(self.image_path):
                self.bg_image = Image.open(self.image_path)
        except Exception as e:
            print(f"图片加载失败: {e}")

    def _prepare_and_show(self):
        """准备背景、文字和卡片布局，然后显示窗口."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10:
            w, h = 900, 550

        self.canvas.delete("all")

        # 绘制全屏背景
        if self.bg_image:
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

        self.card.place(relx=0.75, rely=0.5, anchor="center")
        self.card.lift()

        self.update()
        self.after(50, self._show_window)

    def _show_window(self):
        """解除隐藏，显示窗口并获取焦点."""
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
        """修复输入框高度异常."""
        self.account_entry.configure(height=40)
        self.password_entry.configure(height=40)
        self.update_idletasks()

    def _refresh_placeholders(self):
        """刷新输入框占位符，使其立即显示（解决占位符不同步问题）。"""
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
        # 强制刷新
        self.account_entry.configure(state="disabled")
        self.account_entry.configure(state="normal")
        self.password_entry.configure(state="disabled")
        self.password_entry.configure(state="normal")

        # 强制恢复输入框高度
        self.account_entry.configure(height=40)
        self.password_entry.configure(height=40)
        self.update_idletasks()

    def _switch_role(self, role: str) -> None:
        """切换登录角色。"""
        self.current_role = role
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

        # 清空输入框内容
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

        # 可选：将焦点移到登录按钮，避免输入框立即获取焦点
        self.login_button.focus_set()

    def _login_action(self):
        """根据当前角色验证账号密码，成功则设置登录结果."""
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

        Args:
            account: 账号（管理员用户名 / 教师工号 / 学号）。
            password: 密码。

        Returns:
            包含 success、role、user 字段的字典。
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

        Returns:
            包含 success、role、user 字段的字典。
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
