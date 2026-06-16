"""学生成绩管理系统主程序入口."""

import os
import sys

# 确保项目根目录在导入路径中
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 以下导入依赖上方的 sys.path 设置，需在路径配置后执行
import customtkinter as ctk  # noqa: E402
from modules.data_manager import DataManager  # noqa: E402
from modules.login import LoginWindow  # noqa: E402


if __name__ == "__main__":
    try:
        while True:
            # 重置 customtkinter 主题，避免样式残留导致输入框异常
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")

            dm = DataManager()
            login = LoginWindow(data_manager=dm)
            result = login.run()
            if not result.get("success"):
                print("登录已取消")
                break

            # 清理 tkinter 和 ttkbootstrap 状态，防止退出再登录时
            import tkinter as tk
            from ttkbootstrap import Style

            tk._default_root = None
            if hasattr(Style, "instance"):
                Style.instance = None

            role = result.get("role")
            user = result.get("user", {})
            logout = False

            if role == "admin":
                from app import App

                app_result = App(data_manager=dm, user_info=user).run()
                logout = (
                    app_result.get("logout", False)
                    if isinstance(app_result, dict)
                    else False
                )
            elif role == "teacher":
                from teacher_app import TeacherApp

                # 假设 TeacherApp.run() 返回一个 dict 包含 logout 标志
                app_result = TeacherApp(data_manager=dm, user_info=user).run()
                logout = (
                    app_result.get("logout", False)
                    if isinstance(app_result, dict)
                    else False
                )
            elif role == "student":
                from student_app import StudentApp

                app_result = StudentApp(data_manager=dm, user_info=user).run()
                logout = (
                    app_result.get("logout", False)
                    if isinstance(app_result, dict)
                    else False
                )
            if not logout:
                break
    except Exception as e:
        import traceback

        print(f"登录模块加载失败: {e}")
        traceback.print_exc()
        print("尝试直接进入主程序...")
        from app import App

        App().run()
