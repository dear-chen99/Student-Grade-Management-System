"""
学生成绩管理系统 - 源代码包

包含主应用、UI组件和工具函数。
"""

import os
import sys

# 将项目根目录添加到 Python 路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
