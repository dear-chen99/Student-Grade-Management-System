"""头像工具模块 - Avatar Utilities.

提供头像加载、选择和保存功能，支持 PIL 图像处理。

本模块封装了与头像相关的所有操作，包括：
- 根据相对或绝对路径加载头像并缩放到指定尺寸。
- 通过文件对话框选择新头像，自动复制到项目目录并生成唯一文件名。
- 清理旧头像文件，避免磁盘空间浪费。

依赖::

    需要安装 Pillow（PIL）库以支持图像处理。若未安装，
    ``PIL_AVAILABLE`` 将被置为 ``False``，相关函数将安全降级。

"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog
from typing import Any, Callable, Optional

try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ------------------------------------------------------------------
# 项目路径
# ------------------------------------------------------------------
# 获取项目根目录（假设当前文件位于 src/utils/avatar_utils.py）
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def get_avatar_dir() -> str:
    """返回头像存储目录的绝对路径.

    头像文件统一存放在 ``<项目根目录>/img/avatars/`` 下，便于管理和备份。

    Returns:
        头像目录的绝对路径字符串。
    """
    return os.path.join(_PROJECT_ROOT, "img", "avatars")


def load_avatar(
    label: tk.Label,
    avatar_path: str,
    size: tuple[int, int] = (80, 80),
) -> None:
    """加载头像到指定 Label 控件.

    支持相对路径（基于项目根目录解析）和绝对路径。若 PIL 不可用、
    路径为空或文件不存在，则清空 Label 的图像显示。

    Args:
        label: 用于显示头像的 tkinter Label 控件。
        avatar_path: 头像文件路径（相对项目根目录或绝对路径）。
        size: 缩放宽高，默认 (80, 80) 像素。
    """
    if not PIL_AVAILABLE or not avatar_path:
        label.config(text="", image="")
        return

    # 转换为绝对路径（基于项目根目录）
    if not os.path.isabs(avatar_path):
        full_path = os.path.join(_PROJECT_ROOT, avatar_path)
    else:
        full_path = avatar_path

    if not os.path.exists(full_path):
        label.config(text="", image="")
        return

    try:
        img = Image.open(full_path)
        img = img.resize(size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo, text="")
        label.image = photo  # 保持引用，防止被 Python 垃圾回收
    except Exception:
        # 图像损坏或格式不支持，清空显示
        label.config(text="", image="")


def change_avatar(
    parent: tk.Widget,
    current_path: str,
    save_callback: Callable[[str], Any],
    avatar_dir: Optional[str] = None,
) -> Optional[str]:
    """选择新头像文件并保存到项目目录.

    弹出文件选择对话框，将用户选中的图片复制到头像目录，
    生成唯一文件名，并自动删除旧头像文件。最终通过回调函数
    通知调用方更新数据（存储相对路径以保证 JSON 可移植性）。

    Args:
        parent: 父窗口控件，用于挂载文件对话框。
        current_path: 当前头像路径，用于删除旧文件；为空则跳过清理。
        save_callback: 保存回调函数，接收相对项目根目录的路径字符串。
        avatar_dir: 头像存储目录，为 ``None`` 时使用默认目录。

    Returns:
        相对于项目根目录的新头像路径；若用户取消或处理失败则返回 ``None``。
    """
    if not PIL_AVAILABLE:
        return None

    # 确定头像存储目录（优先使用传入参数，否则使用默认绝对路径）
    if avatar_dir is None:
        avatar_dir = get_avatar_dir()
    else:
        avatar_dir = os.path.abspath(avatar_dir)

    # 弹出系统文件选择对话框，限定图片格式
    file_path = filedialog.askopenfilename(
        parent=parent,
        title="选择头像",
        filetypes=[
            ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("所有文件", "*.*"),
        ],
    )
    if not file_path:
        return None

    try:
        os.makedirs(avatar_dir, exist_ok=True)
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
            ext = ".png"
        import uuid

        # 生成唯一文件名，避免覆盖
        new_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(avatar_dir, new_name)
        shutil.copy2(file_path, dest_path)

        # 删除旧头像文件，释放磁盘空间
        if current_path:
            old_full = (
                os.path.join(_PROJECT_ROOT, current_path)
                if not os.path.isabs(current_path)
                else current_path
            )
            if os.path.exists(old_full):
                try:
                    os.remove(old_full)
                except OSError:
                    pass
    except Exception:
        return None

    # 存储相对于项目根目录的路径（便于 JSON 可移植）
    rel_path = os.path.relpath(dest_path, _PROJECT_ROOT)
    save_callback(rel_path)
    return rel_path
