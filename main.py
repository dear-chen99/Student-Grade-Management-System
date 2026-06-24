"""学生成绩管理系统主程序入口.

本模块作为整个应用程序的启动入口，负责：
1. 配置项目根目录到 Python 导入路径，支持源码运行和 PyInstaller 打包后的运行环境。
2. 提供全局错误弹窗和日志占位函数。
3. 管理登录循环：显示登录窗口 -> 验证身份 -> 根据角色动态加载对应主界面 -> 处理登出/退出。
4. 重置 tkinter 全局状态，避免多次登录后窗口创建异常。

典型执行流程::

    main() -> LoginWindow.run() -> 动态导入角色模块 -> App.run() -> 循环或退出

"""

import logging
import os
import sys
import traceback

# ------------------------------------------------------------------
# 运行时路径配置
# ------------------------------------------------------------------
# 确保项目根目录在导入路径中，以便无论通过 python main.py 还是 PyInstaller 打包 exe 都能正确导入模块
if hasattr(sys, "_MEIPASS"):
    # PyInstaller 打包后环境：资源文件被解压到 _MEIPASS 临时目录
    _project_root = sys._MEIPASS
else:
    # 源码运行环境：以当前文件所在目录为项目根目录
    _project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ------------------------------------------------------------------
# 全局日志配置
# ------------------------------------------------------------------
_logger = logging.getLogger("main")
_logger.setLevel(logging.INFO)
if not _logger.handlers:
    _log_handler = logging.StreamHandler()
    _log_handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s - %(name)s - %(message)s")
    )
    _logger.addHandler(_log_handler)


# ------------------------------------------------------------------
# 全局工具函数
# ------------------------------------------------------------------

def _log(msg: str) -> None:
    """记录日志信息.

    Args:
        msg: 日志消息内容。
    """
    _logger.info(msg)


def _show_error(title: str, msg: str) -> None:
    """在 GUI 不可用时用 tkinter 弹窗显示错误.

    当主程序尚未启动 GUI 或 GUI 已崩溃时，通过原生 tkinter 消息框向用户
    展示致命错误信息，避免程序静默退出。

    Args:
        title: 弹窗标题。
        msg: 弹窗正文内容。
    """
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口，仅显示消息框
        messagebox.showerror(title, msg)
        root.destroy()
    except Exception:
        # tkinter 本身不可用，无法弹窗，只能静默放弃
        pass


# ------------------------------------------------------------------
# 延迟导入项目模块（必须在 sys.path 配置完成后）
# ------------------------------------------------------------------
import customtkinter as ctk
from modules.data_manager import DataManager
from modules.login import LoginWindow


# ------------------------------------------------------------------
# tkinter 状态重置
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# 主程序入口
# ------------------------------------------------------------------

def main() -> None:
    """主程序入口，管理登录循环和角色分发.

    执行流程如下：
    1. 无限循环显示登录窗口，直到用户取消登录或退出程序。
    2. 登录成功后根据角色映射表动态导入对应模块并启动主界面。
    3. 主界面返回后检查是否为"登出"操作：若是则重置状态并重新进入登录流程；否则退出程序。

    Raises:
        SystemExit: 发生未预期致命错误时以状态码 1 退出。
    """
    # 角色到模块/类的映射表，便于根据登录角色动态加载对应界面
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

            # 用户取消登录或关闭窗口，结束主循环
            if not result.get("success"):
                _log("登录已取消")
                break

            _reset_tk_state()

            role = result.get("role")
            user = result.get("user", {})
            _log(f"用户角色: {role}, 用户信息: {user.get('id', '')}")

            # 未知角色直接退出，防止后续动态导入出错
            if role not in role_map:
                _log(f"未知角色: {role}")
                print(f"未知角色: {role}")
                break

            module_name, class_name = role_map[role]
            _log(f"动态导入模块: {module_name}, 类: {class_name}")

            # 动态导入对应角色的主界面模块
            try:
                module = __import__(module_name, fromlist=[class_name])
                _log(f"模块导入成功: {module_name}")
            except Exception as e:
                _log(f"模块导入失败: {e}\n{traceback.format_exc()}")
                _show_error("导入错误", f"无法加载模块 {module_name}：\n{e}")
                break

            # 从模块中获取主界面类
            try:
                app_cls = getattr(module, class_name)
                _log(f"获取类成功: {class_name}")
            except Exception as e:
                _log(f"获取类失败: {e}\n{traceback.format_exc()}")
                _show_error("错误", f"无法找到类 {class_name}：\n{e}")
                break

            # 实例化主界面类并传入数据管理器和用户信息
            _log(f"创建 {class_name} 实例...")
            try:
                app_instance = app_cls(data_manager=dm, user_info=user)
                _log(f"{class_name} 实例创建成功")
            except Exception as e:
                _log(f"创建实例失败: {e}\n{traceback.format_exc()}")
                _show_error("启动错误", f"无法启动主程序：\n{e}")
                break

            # 进入主界面事件循环
            _log(f"调用 {class_name}.run()...")
            try:
                app_result = app_instance.run()
                _log(f"run() 返回: {app_result}")
            except Exception as e:
                _log(f"run() 异常: {e}\n{traceback.format_exc()}")
                _show_error("运行错误", f"程序运行异常：\n{e}")
                break

            # 判断用户是否点击"退出登录"：若是则返回登录窗口，否则彻底退出
            logout = (
                app_result.get("logout", False)
                if isinstance(app_result, dict)
                else False
            )

            if not logout:
                break
    except Exception as e:
        # 捕获主循环中任何未处理的异常，避免程序崩溃时无提示
        _log(f"主循环异常: {e}\n{traceback.format_exc()}")
        _show_error("程序异常", f"发生未预期的错误：\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
