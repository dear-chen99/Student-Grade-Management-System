"""
UI 公共工具模块 - UI Utilities Module.

提供弹窗创建、Treeview 构建、消息提示等公共 UI 工具函数，
减少各应用文件中的重复代码。

主要功能::

    - create_dialog: 创建标准 Toplevel 弹窗（自动居中、模态抓取）。
    - create_treeview: 创建带滚动条和斑马纹的 Treeview。
    - show_info / show_warning / show_error / confirm: 消息提示封装。
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from src.config import UI_COLORS, FONTS, DIALOG_SIZES, DIALOG_OFFSET


def validate_password(password: str) -> tuple[bool, str]:
    """校验密码强度.

    规则：至少 6 位，且必须同时包含字母和数字。

    Args:
        password: 待校验的密码字符串。

    Returns:
        (is_valid, error_msg) 元组。is_valid 为 True 时 error_msg 为空字符串。
    """
    if len(password) < 6:
        return False, "密码至少需要 6 位"
    if not re.search(r"[A-Za-z]", password):
        return False, "密码必须包含字母"
    if not re.search(r"\d", password):
        return False, "密码必须包含数字"
    return True, ""


def create_dialog(
    parent: tk.Misc,
    title: str,
    size: str = "medium",
    modal: bool = True,
    offset: Optional[dict] = None,
) -> tk.Toplevel:
    """创建标准 Toplevel 弹窗，自动定位并配置模态属性.

    Args:
        parent: 父窗口。
        title: 弹窗标题。
        size: DIALOG_SIZES 中的键名（如 "small"/"medium"/"large"），
              也可直接传入 "WxH" 格式的尺寸字符串。
        modal: 是否模态（grab_set + transient）。
        offset: 偏移字典 {"x": int, "y": int}，默认使用 DIALOG_OFFSET。

    Returns:
        配置好的 tk.Toplevel 实例。
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    geometry = DIALOG_SIZES.get(size, size)

    if offset is None:
        offset = DIALOG_OFFSET
    parent.update_idletasks()
    win_x = parent.winfo_x()
    win_y = parent.winfo_y()
    dialog.geometry(f"{geometry}+{win_x + offset['x']}+{win_y + offset['y']}")

    if modal:
        dialog.grab_set()
        dialog.transient(parent)
    return dialog


def create_treeview(
    parent: tk.Frame,
    columns: list[str],
    widths: list[int],
    height: int = 14,
    zebra: bool = True,
    pack: bool = True,
) -> tuple[ttk.Treeview, tk.Frame]:
    """创建带滚动条和斑马纹的 Treeview.

    自动添加垂直/水平滚动条，配置表头与列宽，并应用斑马纹样式。

    Args:
        parent: 父容器 Frame。
        columns: 列标识符列表。
        widths: 对应各列的宽度列表。
        height: 表格显示行数。
        zebra: 是否启用斑马纹（odd/even 行交替背景色）。
        pack: 是否自动将内部 Frame 打包到 parent。

    Returns:
        (ttk.Treeview, tk.Frame) 元组。
    """
    frame = tk.Frame(parent, bg=UI_COLORS["card_bg"])
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

    if zebra:
        tree.tag_configure("odd", background=UI_COLORS["row_odd"])
        tree.tag_configure("even", background=UI_COLORS["row_even"])

    if pack:
        frame.pack(fill="both", expand=True, pady=(15, 0))
    return tree, frame


def show_info(title: str, message: str, parent: Optional[tk.Misc] = None) -> None:
    """显示信息提示框.

    Args:
        title: 提示框标题。
        message: 提示内容。
        parent: 父窗口（可选），设置后弹窗将依附于该窗口。
    """
    if parent:
        messagebox.showinfo(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message)


def show_warning(title: str, message: str, parent: Optional[tk.Misc] = None) -> None:
    """显示警告提示框.

    Args:
        title: 警告框标题。
        message: 警告内容。
        parent: 父窗口（可选）。
    """
    if parent:
        messagebox.showwarning(title, message, parent=parent)
    else:
        messagebox.showwarning(title, message)


def show_error(title: str, message: str, parent: Optional[tk.Misc] = None) -> None:
    """显示错误提示框.

    Args:
        title: 错误框标题。
        message: 错误内容。
        parent: 父窗口（可选）。
    """
    if parent:
        messagebox.showerror(title, message, parent=parent)
    else:
        messagebox.showerror(title, message)


def confirm(title: str, message: str, parent: Optional[tk.Misc] = None) -> bool:
    """显示确认对话框，返回用户选择.

    Args:
        title: 确认框标题。
        message: 确认内容。
        parent: 父窗口（可选）。

    Returns:
        True 表示用户点击"是"，False 表示点击"否"。
    """
    if parent:
        return messagebox.askyesno(title, message, parent=parent)
    return messagebox.askyesno(title, message)
