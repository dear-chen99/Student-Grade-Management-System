#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 组件模块 - UI Components Module

包含自定义 UI 组件，如渐变框架、现代卡片、状态栏、导航栏、数据表格等。
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class GradientFrame(tk.Canvas):
    """渐变框架组件。

    用于创建渐变色背景的 Canvas，常用于标题栏等装饰位置。

    Attributes:
        color1: 起始颜色（十六进制字符串）。
        color2: 结束颜色（十六进制字符串）。
        height: 渐变区域高度。
    """

    def __init__(
        self,
        parent: tk.Widget,
        color1: str,
        color2: str,
        height: int = 3,
        **kwargs: Any,
    ) -> None:
        """初始化渐变框架。

        Args:
            parent: 父容器。
            color1: 起始颜色（如 "#6366F1"）。
            color2: 结束颜色（如 "#8B5CF6"）。
            height: 渐变高度（像素）。
            **kwargs: 传递给 tk.Canvas 的额外参数。
        """
        tk.Canvas.__init__(self, parent, **kwargs)
        self.color1: str = color1
        self.color2: str = color2
        self.height: int = height
        self.bind("<Configure>", self._draw)

    def _draw(self, event: Optional[tk.Event] = None) -> None:
        """绘制渐变效果。

        Args:
            event: tkinter Configure 事件，可选。
        """
        w = self.winfo_width()
        h = self.height
        self.delete("gradient")

        try:
            r1 = int(self.color1[1:3], 16)
            g1 = int(self.color1[3:5], 16)
            b1 = int(self.color1[5:7], 16)
            r2 = int(self.color2[1:3], 16)
            g2 = int(self.color2[3:5], 16)
            b2 = int(self.color2[5:7], 16)
        except (ValueError, IndexError):
            r1, g1, b1 = 99, 102, 241
            r2, g2, b2 = 139, 92, 246

        for i in range(h + 1):
            r = round(r1 + (r2 - r1) * i / h)
            g = round(g1 + (g2 - g1) * i / h)
            b = round(b1 + (b2 - b1) * i / h)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_line(0, i, w, i, fill=color, tags="gradient")

        self.lower("gradient")


class ModernCard(tk.Frame):
    """现代卡片组件。

    用于创建带阴影效果的卡片容器，提升界面美观度。

    Attributes:
        inner: 内部容器 tk.Frame，用于放置实际内容。
    """

    def __init__(
        self, parent: tk.Widget, bg: str = "white", **kwargs: Any
    ) -> None:
        """初始化现代卡片。

        Args:
            parent: 父容器。
            bg: 背景颜色，默认为 "white"。
            **kwargs: 传递给 tk.Frame 的额外参数。
        """
        super().__init__(parent, bg=bg, **kwargs)
        self.configure(relief="flat", bd=0)

        # 阴影层
        shadow = tk.Frame(self, bg="#E2E8F0", bd=0)
        shadow.pack(fill="both", expand=True, padx=2, pady=2)

        # 内容层
        inner = tk.Frame(shadow, bg=bg, relief="flat", bd=0)
        inner.pack(fill="both", expand=True)
        self.inner: tk.Frame = inner


class StatusBar(tk.Frame):
    """状态栏组件。

    用于显示系统状态信息。

    Attributes:
        status_var: 状态文本变量。
        label: 状态标签。
    """

    def __init__(self, parent: tk.Widget, **kwargs: Any) -> None:
        """初始化状态栏。

        Args:
            parent: 父容器。
            **kwargs: 传递给 tk.Frame 的额外参数。
        """
        super().__init__(parent, **kwargs)
        self.configure(bg="#F1F5F9", height=30)

        self.status_var: tk.StringVar = tk.StringVar(value="就绪")
        self.label: tk.Label = tk.Label(
            self,
            textvariable=self.status_var,
            bg="#F1F5F9",
            fg="#64748B",
            font=("微软雅黑", 9),
            anchor="w",
        )
        self.label.pack(side="left", padx=10, fill="x", expand=True)

    def set_status(self, message: str) -> None:
        """设置状态信息。

        Args:
            message: 状态消息文本。
        """
        self.status_var.set(message)

    def get_status(self) -> str:
        """获取当前状态信息。

        Returns:
            当前状态消息文本。
        """
        return self.status_var.get()


class NavigationBar(tk.Frame):
    """导航栏组件。

    用于页面切换的导航菜单。

    Attributes:
        callback: 页面切换回调函数。
        buttons: 导航按钮字典。
        current_page: 当前激活的页面标识。
    """

    def __init__(
        self,
        parent: tk.Widget,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> None:
        """初始化导航栏。

        Args:
            parent: 父容器。
            callback: 页面切换回调函数，接收页面标识字符串。
            **kwargs: 传递给 tk.Frame 的额外参数。
        """
        super().__init__(parent, **kwargs)
        self.configure(bg="#FFFFFF", height=50)
        self.callback: Optional[Callable[[str], None]] = callback
        self.buttons: dict[str, ttk.Button] = {}
        self.current_page: Optional[str] = None

        self.nav_items: list[tuple[str, str]] = [
            ("dashboard", "📊 数据概览"),
            ("entry", "📝 成绩录入"),
            ("analysis", "📈 图表分析"),
            ("class", "🏫 班级管理"),
            ("search", "🔍 数据查询"),
        ]

        self._create_buttons()

    def _create_buttons(self) -> None:
        """创建导航按钮。"""
        style = ttk.Style()
        style.configure(
            "Nav.TButton", font=("微软雅黑", 10), padding=(15, 8)
        )

        for key, text in self.nav_items:
            btn = ttk.Button(
                self,
                text=text,
                style="Nav.TButton",
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(side="left", padx=5, pady=8)
            self.buttons[key] = btn

    def _on_click(self, page_key: str) -> None:
        """按钮点击事件处理。

        Args:
            page_key: 页面标识。
        """
        if self.callback:
            self.callback(page_key)
        self.set_active(page_key)

    def set_active(self, page_key: str) -> None:
        """设置当前激活的页面。

        Args:
            page_key: 页面标识。
        """
        self.current_page = page_key


class DataTable(ttk.Treeview):
    """数据表格组件。

    用于显示学生成绩等数据，继承自 ttk.Treeview。

    Attributes:
        继承自 ttk.Treeview。
    """

    def __init__(
        self,
        parent: tk.Widget,
        columns: list[str],
        widths: Optional[list[int]] = None,
        **kwargs: Any,
    ) -> None:
        """初始化数据表格。

        Args:
            parent: 父容器。
            columns: 列名列表。
            widths: 列宽列表，可选，默认 100。
            **kwargs: 传递给 ttk.Treeview 的额外参数。
        """
        super().__init__(parent, columns=columns, show="headings", **kwargs)

        for i, col in enumerate(columns):
            self.heading(col, text=col)
            width = widths[i] if widths and i < len(widths) else 100
            self.column(col, width=width, minwidth=50)

    def clear(self) -> None:
        """清空表格所有数据。"""
        for item in self.get_children():
            self.delete(item)

    def add_row(
        self, values: list[Any], tags: Optional[list[str]] = None
    ) -> str:
        """添加一行数据。

        Args:
            values: 行数据列表。
            tags: 标签列表，可选。

        Returns:
            新行的 ID 字符串。
        """
        return self.insert("", "end", values=values, tags=tags or ())

    def get_selected(self) -> list[str]:
        """获取当前选中的行 ID 列表。

        Returns:
            选中行 ID 列表。
        """
        return self.selection()