"""学生成绩管理系统主程序入口."""

import os
import sys
import traceback

# 确保项目根目录在导入路径中
if hasattr(sys, "_MEIPASS"):
    # PyInstaller 打包后环境
    _project_root = sys._MEIPASS
else:
    _project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def _log(msg: str) -> None:
    """日志占位函数，不再写入文件."""
    pass


def _show_error(title: str, msg: str) -> None:
    """在 GUI 不可用时用 tkinter 弹窗显示错误."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, msg)
        root.destroy()
    except Exception:
        pass


# 以下导入依赖上方的 sys.path 设置，需在路径配置后执行
import customtkinter as ctk  # noqa: E402
from modules.data_manager import DataManager  # noqa: E402
from modules.login import LoginWindow  # noqa: E402


def _reset_tk_state() -> None:
    """重置 tkinter 全局状态，避免退出登录后重新创建窗口时异常.

    退出登录后，tkinter 的 _default_root 和 ttkbootstrap 的 Style
    单例可能仍指向旧窗口，导致新窗口创建失败或样式错乱。
    此处手动重置为已知安全的初始状态。
    """
    import tkinter as tk
    from ttkbootstrap import Style

    tk._default_root = None
    if hasattr(Style, "instance"):
        Style.instance = None


def main() -> None:
    """主程序入口，管理登录循环和角色分发."""
    role_map = {
        "admin": ("app", "App"),
        "teacher": ("teacher_app", "TeacherApp"),
        "student": ("student_app", "StudentApp"),
    }

    try:
        while True:
            # 重置 customtkinter 主题，避免样式残留导致输入框异常
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")

            _log("创建 DataManager...")
            dm = DataManager()
            _log("DataManager 创建成功")

            _log("显示登录窗口...")
            login = LoginWindow(data_manager=dm)
            result = login.run()
            _log(f"登录结果: {result.get('success')}, role={result.get('role')}")

            if not result.get("success"):
                _log("登录已取消")
                break

            _reset_tk_state()

            role = result.get("role")
            user = result.get("user", {})
            _log(f"用户角色: {role}, 用户信息: {user.get('id', '')}")

            if role not in role_map:
                _log(f"未知角色: {role}")
                print(f"未知角色: {role}")
                break

            module_name, class_name = role_map[role]
            _log(f"动态导入模块: {module_name}, 类: {class_name}")
            try:
                module = __import__(module_name, fromlist=[class_name])
                _log(f"模块导入成功: {module_name}")
            except Exception as e:
                _log(f"模块导入失败: {e}\n{traceback.format_exc()}")
                _show_error("导入错误", f"无法加载模块 {module_name}：\n{e}")
                break

            try:
                app_cls = getattr(module, class_name)
                _log(f"获取类成功: {class_name}")
            except Exception as e:
                _log(f"获取类失败: {e}\n{traceback.format_exc()}")
                _show_error("错误", f"无法找到类 {class_name}：\n{e}")
                break

            _log(f"创建 {class_name} 实例...")
            try:
                app_instance = app_cls(data_manager=dm, user_info=user)
                _log(f"{class_name} 实例创建成功")
            except Exception as e:
                _log(f"创建实例失败: {e}\n{traceback.format_exc()}")
                _show_error("启动错误", f"无法启动主程序：\n{e}")
                break

            _log(f"调用 {class_name}.run()...")
            try:
                app_result = app_instance.run()
                _log(f"run() 返回: {app_result}")
            except Exception as e:
                _log(f"run() 异常: {e}\n{traceback.format_exc()}")
                _show_error("运行错误", f"程序运行异常：\n{e}")
                break

            logout = (
                app_result.get("logout", False)
                if isinstance(app_result, dict)
                else False
            )

            if not logout:
                break
    except Exception as e:
        _log(f"主循环异常: {e}\n{traceback.format_exc()}")
        _show_error("程序异常", f"发生未预期的错误：\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
