#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块 - Configuration Module

包含系统常量、颜色配置和全局设置。
"""

from typing import Any

# 颜色配置
COLORS: dict[str, str] = {
    "primary": "#6366F1",
    "secondary": "#8B5CF6",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#3B82F6",
    "dark": "#1E293B",
    "light": "#F8FAFC",
    "white": "#FFFFFF",
    "gray": "#64748B",
    "bg": "#F1F5F9",
}

# 窗口配置
WINDOW_CONFIG: dict[str, Any] = {
    "title": "学生成绩管理系统",
    "width": 1200,
    "height": 780,
    "min_width": 1000,
    "min_height": 620,
}

# 登录配置
LOGIN_CONFIG: dict[str, str] = {
    "default_username": "admin",
    "default_password": "123456",
}

# 图表配置
CHART_CONFIG: dict[str, Any] = {
    "font_family": "Microsoft YaHei",
    "passing_score": 60,
    "excellent_score": 90,
    "default_colors": [
        "#6366F1",
        "#8B5CF6",
        "#3B82F6",
        "#10B981",
        "#F59E0B",
        "#EF4444",
    ],
}

# 数据配置
DATA_CONFIG: dict[str, str] = {
    "backup_suffix": ".bak",
    "temp_suffix": ".tmp",
}