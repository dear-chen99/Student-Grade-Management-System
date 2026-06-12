"""登录窗口模块 - Login Window for Student Grade Management System."""

import os
from tkinter import messagebox, Canvas

import customtkinter as ctk
from PIL import Image, ImageTk

# 设置主题
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    """
    登录窗口类.

    提供用户名和密码输入，验证成功后返回 True，否则返回 False。
    """

    def __init__(self):
        """初始化登录窗口，加载界面元素和背景图片."""
        super().__init__()

        self.title("登录 - 学生成绩管理系统")
        self.geometry("900x550")
        self.resizable(False, False)

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.iconbitmap(os.path.join(project_root, "img", "icon.ico"))

        self.login_success = False

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
            self, fg_color="white", corner_radius=0, width=400, height=450
        )

        self.title_label = ctk.CTkLabel(
            self.card,
            text="欢迎登录",
            font=("微软雅黑", 18, "bold"),
            text_color="#2C3E50",
        )
        self.title_label.pack(pady=(30, 20))

        self.username_entry = ctk.CTkEntry(
            self.card, placeholder_text="请输入用户名", height=40, corner_radius=10
        )
        self.username_entry.pack(pady=10, padx=25, fill="x")

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="请输入密码",
            height=40,
            corner_radius=10,
            show="*",
        )
        self.password_entry.pack(pady=10, padx=25, fill="x")

        self.login_button = ctk.CTkButton(
            self.card,
            text="立即登录",
            font=("微软雅黑", 14, "bold"),
            height=40,
            corner_radius=10,
            fg_color="#0374BF",
            hover_color="#2980B9",
            command=self._login_action,
        )
        self.login_button.pack(pady=20, padx=90, fill="x")

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

    def _login_action(self):
        """验证用户名和密码，成功则设置登录标志."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if username == "admin" and password == "123456":
            self.login_success = True
            self.destroy()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误！")

    def run(self):
        """启动窗口主循环，返回登录结果."""
        self.mainloop()
        return self.login_success


if __name__ == "__main__":
    app = LoginWindow()
    if app.run():
        print("登录成功")
    else:
        print("登录已取消")
