#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest 配置文件

提供测试所需的 fixtures 和配置
"""

import os
import sys
import tempfile
import shutil
import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_data_dir():
    """提供临时测试数据目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_data_file(test_data_dir):
    """提供临时测试数据文件路径"""
    return os.path.join(test_data_dir, "test_grades.json")


@pytest.fixture
def sample_student_data():
    """提供示例学生数据"""
    return {
        "001": {
            "name": "张三",
            "class": "一班",
            "scores": {"数学": 90, "语文": 85}
        },
        "002": {
            "name": "李四",
            "class": "二班",
            "scores": {"数学": 85, "语文": 90}
        }
    }


@pytest.fixture
def sample_subjects():
    """提供示例科目列表"""
    return ["数学", "语文", "英语"]


@pytest.fixture
def sample_classes():
    """提供示例班级列表"""
    return ["一班", "二班", "三班"]
