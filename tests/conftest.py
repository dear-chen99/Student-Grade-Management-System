"""
Pytest 配置文件.

提供测试所需的 fixtures 和配置，包括临时数据目录、临时数据文件、
示例学生数据、示例科目列表和示例班级列表等共享资源。
"""

import os
import sys
import tempfile
import shutil
import pytest

# 添加项目根目录到 Python 路径，确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_data_dir():
    """提供临时测试数据目录.

    Yields:
        str: 临时目录的绝对路径，测试结束后自动清理。
    """
    temp_dir = tempfile.mkdtemp()  # 创建临时目录
    yield temp_dir
    # 测试完成后清理临时目录
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_data_file(test_data_dir):
    """提供临时测试数据文件路径.

    Args:
        test_data_dir: 由 test_data_dir fixture 提供的临时目录。

    Returns:
        str: 临时 JSON 数据文件的完整路径。
    """
    return os.path.join(test_data_dir, "test_grades.json")


@pytest.fixture
def sample_student_data():
    """提供示例学生数据.

    Returns:
        dict: 包含两名示例学生的字典，用于快速构造测试数据。
    """
    return {
        "001": {"name": "张三", "class": "一班", "scores": {"数学": 90, "语文": 85}},
        "002": {"name": "李四", "class": "二班", "scores": {"数学": 85, "语文": 90}},
    }


@pytest.fixture
def sample_subjects():
    """提供示例科目列表.

    Returns:
        list[str]: 包含数学、语文、英语的科目名称列表。
    """
    return ["数学", "语文", "英语"]


@pytest.fixture
def sample_classes():
    """提供示例班级列表.

    Returns:
        list[str]: 包含一班、二班、三班的班级名称列表。
    """
    return ["一班", "二班", "三班"]
