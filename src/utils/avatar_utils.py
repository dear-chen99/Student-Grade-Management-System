"""头像工具模块 - Avatar Utilities.

提供头像加载、选择和保存功能，支持 PIL 图像处理。
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

# 获取项目根目录（假设当前文件位于 src/utils/avatar_utils.py）
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def get_avatar_dir() -> str:
    """返回头像存储目录的绝对路径."""
    return os.path.join(_PROJECT_ROOT, "img", "avatars")


def load_avatar(
    label: tk.Label,
    avatar_path: str,
    size: tuple[int, int] = (80, 80),
) -> None:
    """加载头像到指定 Label 控件（支持相对/绝对路径，自动基于项目根目录解析）."""
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
        label.image = photo  # 防止被垃圾回收
    except Exception:
        label.config(text="", image="")


def change_avatar(
    parent: tk.Widget,
    current_path: str,
    save_callback: Callable[[str], Any],
    avatar_dir: Optional[str] = None,
) -> Optional[str]:
    """选择新头像文件并保存到绝对路径目录，返回相对于项目根目录的路径."""
    if not PIL_AVAILABLE:
        return None

    # 使用绝对路径目录
    if avatar_dir is None:
        avatar_dir = get_avatar_dir()
    else:
        avatar_dir = os.path.abspath(avatar_dir)

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

        new_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(avatar_dir, new_name)
        shutil.copy2(file_path, dest_path)

        # 删除旧头像
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
