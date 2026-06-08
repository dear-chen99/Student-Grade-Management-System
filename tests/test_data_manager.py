#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataManager 模块单元测试（增强版）

测试数据管理器的各项功能，包括：
- 学生增删改查
- 科目管理
- 成绩管理（含历史记录）
- 统计分析
- 数据持久化（含备份恢复）
- 数据完整性校验
- 搜索功能边界测试
- 预警功能
"""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, mock_open

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager import DataManager, DataIntegrityError, DataLoadError, DataSaveError, StudentNotFoundError, SubjectNotFoundError, InvalidInputError


class TestDataManager(unittest.TestCase):
    """DataManager 核心功能测试类"""

    def setUp(self):
        """测试前准备：创建临时数据文件"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_grades.json")
        self.dm = DataManager(self.test_file)

    def tearDown(self):
        """测试后清理：删除临时文件"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # ==================== 基础功能测试 ====================

    def test_initialization(self):
        """测试 DataManager 初始化"""
        self.assertIsNotNone(self.dm)
        self.assertIsInstance(self.dm.data, dict)
        self.assertIn("subjects", self.dm.data)
        self.assertIn("students", self.dm.data)
        self.assertIn("history", self.dm.data)

    def test_empty_data_structure(self):
        """测试空数据结构创建"""
        self.assertEqual(self.dm.subjects, [])
        self.assertEqual(self.dm.students, {})
        self.assertEqual(self.dm.data["history"], [])

    def test_file_path_properties(self):
        """测试文件路径属性"""
        self.assertEqual(self.dm.fp, self.test_file)
        self.assertEqual(self.dm.bak, self.test_file + ".bak")

    # ==================== 科目管理测试 ====================

    def test_add_subject(self):
        """测试添加科目"""
        self.dm.add_subject("数学")
        self.assertIn("数学", self.dm.subjects)

    def test_add_duplicate_subject(self):
        """测试添加重复科目"""
        self.dm.add_subject("数学")
        with self.assertRaises(Exception) as context:
            self.dm.add_subject("数学")
        self.assertIn("已存在", str(context.exception))

    def test_add_empty_subject(self):
        """测试添加空科目名"""
        with self.assertRaises(Exception) as context:
            self.dm.add_subject("")
        self.assertIn("不能为空", str(context.exception))

    def test_add_subject_with_whitespace(self):
        """测试添加带空格的科目名（自动去除）"""
        self.dm.add_subject("  数学  ")
        self.assertIn("数学", self.dm.subjects)

    def test_delete_subject(self):
        """测试删除科目同时清理成绩"""
        self.dm.add_subject("数学")
        self.dm.add_student("001", "张三", "一班")
        self.dm.set_score("001", "数学", 90)
        self.dm.delete_subject("数学")
        self.assertNotIn("数学", self.dm.subjects)
        # 学生成绩中也不应包含该科目
        self.assertNotIn("数学", self.dm.get_student("001")["scores"])

    def test_delete_nonexistent_subject(self):
        """测试删除不存在的科目（应抛出异常）"""
        with self.assertRaises(SubjectNotFoundError):
            self.dm.delete_subject("不存在的科目")

    def test_add_sub_compatibility(self):
        """测试 add_sub 兼容方法"""
        self.dm.add_sub("英语")
        self.assertIn("英语", self.dm.subjects)

    def test_multiple_subjects(self):
        """测试批量添加多个科目"""
        for sub in ["语文", "数学", "英语", "物理", "化学"]:
            self.dm.add_subject(sub)
        self.assertEqual(len(self.dm.subjects), 5)

    # ==================== 学生管理测试 ====================

    def test_add_student(self):
        """测试添加学生"""
        self.dm.add_student("001", "张三", "一班")
        self.assertIn("001", self.dm.students)
        student = self.dm.get_student("001")
        self.assertEqual(student["name"], "张三")
        self.assertEqual(student["class"], "一班")

    def test_add_duplicate_student(self):
        """测试添加重复学号学生"""
        self.dm.add_student("001", "张三", "一班")
        with self.assertRaises(Exception) as context:
            self.dm.add_student("001", "李四", "二班")
        self.assertIn("已存在", str(context.exception))

    def test_add_empty_student_id(self):
        """测试添加空学号学生"""
        with self.assertRaises(Exception) as context:
            self.dm.add_student("", "张三", "一班")
        self.assertIn("不能为空", str(context.exception))

    def test_add_student_with_whitespace(self):
        """测试添加学生时去除空格"""
        self.dm.add_student("  001  ", "  张三  ", "  一班  ")
        self.assertIn("001", self.dm.students)
        student = self.dm.get_student("001")
        self.assertEqual(student["name"], "张三")
        self.assertEqual(student["class"], "一班")

    def test_update_student(self):
        """测试更新学生信息"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.upd_stu("001", "李四", "二班")
        student = self.dm.get_student("001")
        self.assertEqual(student["name"], "李四")
        self.assertEqual(student["class"], "二班")

    def test_update_student_partial(self):
        """测试仅更新姓名（班级不变）"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.upd_stu("001", "李四", "")
        student = self.dm.get_student("001")
        self.assertEqual(student["name"], "李四")

    def test_delete_student(self):
        """测试删除学生"""
        self.dm.add_student("001", "张三", "一班")
        self.assertIn("001", self.dm.students)
        self.dm.del_stu("001")
        self.assertNotIn("001", self.dm.students)

    def test_delete_nonexistent_student(self):
        """测试删除不存在的学生（应抛出异常）"""
        with self.assertRaises(StudentNotFoundError):
            self.dm.del_stu("999")

    def test_get_nonexistent_student(self):
        """测试获取不存在的学生"""
        student = self.dm.get_student("999")
        self.assertIsNone(student)

    def test_get_student_new_idiom(self):
        """测试 get_student 存在时返回数据"""
        self.dm.add_student("001", "张三", "一班")
        student = self.dm.get_student("001")
        self.assertEqual(student["name"], "张三")

    def test_get_stu_old_idiom(self):
        """测试 get_stu 旧兼容方法"""
        self.dm.add_student("001", "张三", "一班")
        student = self.dm.get_stu("001")
        self.assertIsNotNone(student)
        self.assertEqual(student["name"], "张三")

    def test_student_exists(self):
        """测试学生是否存在"""
        self.dm.add_student("001", "张三", "一班")
        self.assertTrue(self.dm.exists("001"))
        self.assertFalse(self.dm.exists("999"))

    def test_add_stu_compatibility(self):
        """测试 add_stu 兼容方法"""
        self.dm.add_stu("001", "张三", "一班")
        self.assertIn("001", self.dm.students)

    def test_multiple_students(self):
        """测试批量添加学生"""
        for sid in ["001", "002", "003", "004", "005"]:
            self.dm.add_student(sid, f"学生{sid}", "一班")
        self.assertEqual(len(self.dm.students), 5)

    # ==================== 成绩管理测试 ====================

    def test_set_score(self):
        """测试设置成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 95)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 95)

    def test_set_score_invalid_range(self):
        """测试设置超出范围的成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        with self.assertRaises(Exception) as context:
            self.dm.set_score("001", "数学", 150)
        self.assertIn("0-100", str(context.exception))

    def test_set_negative_score(self):
        """测试设置负数成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        with self.assertRaises(Exception):
            self.dm.set_score("001", "数学", -10)

    def test_set_score_zero(self):
        """测试设置零分"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 0)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 0)

    def test_set_score_float(self):
        """测试设置浮点数成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 85.5)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 85.5)

    def test_set_score_to_none(self):
        """测试设置成绩为 None"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("001", "数学", None)
        student = self.dm.get_student("001")
        self.assertIsNone(student["scores"]["数学"])

    def test_batch_set_scores(self):
        """测试批量设置成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.add_subject("语文")
        self.dm.batch_set("001", {"数学": 90, "语文": 85})
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 90)
        self.assertEqual(student["scores"]["语文"], 85)

    def test_batch_set_with_invalid_data(self):
        """测试批量设置时跳过无效数据"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.batch_set("001", {"数学": 90, "语文": "无效"})
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 90)
        self.assertNotIn("语文", student["scores"])

    def test_batch_set_with_out_of_range(self):
        """测试批量设置时跳过超范围成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.batch_set("001", {"数学": 999})
        student = self.dm.get_student("001")
        self.assertNotIn("数学", student["scores"])

    def test_set_score_for_nonexistent_student(self):
        """测试为不存在的学生设置成绩"""
        self.dm.add_subject("数学")
        with self.assertRaises(Exception):
            self.dm.set_score("999", "数学", 90)

    # ==================== 历史记录测试 ====================

    def test_history_empty_initially(self):
        """测试初始历史记录为空"""
        self.assertEqual(self.dm.get_history(), [])

    def test_history_recorded_on_set_score(self):
        """测试设置成绩时记录历史"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        history = self.dm.get_history()
        self.assertEqual(len(history), 1)
        entry = history[0]
        self.assertEqual(entry["sid"], "001")
        self.assertEqual(entry["subject"], "数学")
        self.assertIsNone(entry["old"])
        self.assertEqual(entry["new"], 90)
        self.assertIn("time", entry)
        self.assertIn("operator", entry)

    def test_history_records_old_and_new(self):
        """测试修改成绩时记录新旧值"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("001", "数学", 95)
        history = self.dm.get_history()
        self.assertEqual(len(history), 2)
        last = history[0] if history[1]["time"] < history[0]["time"] else history[1]
        # Find the change entry (old=90, new=95)
        change = [h for h in history if h["old"] == 90 and h["new"] == 95]
        self.assertEqual(len(change), 1)

    def test_history_filter_by_sid(self):
        """测试按学号过滤历史记录"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("002", "数学", 85)
        history_001 = self.dm.get_history(student_id="001")
        self.assertEqual(len(history_001), 1)
        self.assertEqual(history_001[0]["sid"], "001")

    def test_history_filter_by_subject(self):
        """测试按科目过滤历史记录"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.add_subject("语文")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("001", "语文", 85)
        math_history = self.dm.get_history(subject="数学")
        self.assertEqual(len(math_history), 1)
        self.assertEqual(math_history[0]["subject"], "数学")

    def test_history_recorded_on_batch_set(self):
        """测试批量设置时记录历史"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.add_subject("语文")
        self.dm.batch_set("001", {"数学": 90, "语文": 85})
        history = self.dm.get_history()
        self.assertEqual(len(history), 2)

    def test_history_no_change_no_record(self):
        """测试成绩未变化时不记录历史"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("001", "数学", 90)  # 相同值
        history = self.dm.get_history()
        self.assertEqual(len(history), 1)  # 仅第一次设置时记录

    # ==================== 统计分析测试 ====================

    def test_stats_single_student(self):
        """测试单个学生统计"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.add_subject("语文")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("001", "语文", 85)
        stats = self.dm.stats("001")
        self.assertEqual(stats["id"], "001")
        self.assertEqual(stats["name"], "张三")
        self.assertEqual(stats["total"], 175)
        self.assertEqual(stats["avg"], 87.5)

    def test_stats_nonexistent_student(self):
        """测试统计不存在的学生"""
        stats = self.dm.stats("999")
        self.assertIsNone(stats)

    def test_stats_with_missing_scores(self):
        """测试有缺考科目的统计"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.add_subject("语文")
        self.dm.set_score("001", "数学", 90)
        stats = self.dm.stats("001")
        self.assertEqual(stats["total"], 90)
        self.assertEqual(stats["avg"], 90)  # 只统计有成绩的科目

    def test_stats_class_average(self):
        """测试班级平均分统计"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 100)
        self.dm.set_score("002", "数学", 60)
        stats_001 = self.dm.stats("001")
        stats_002 = self.dm.stats("002")
        self.assertAlmostEqual((stats_001["avg"] + stats_002["avg"]) / 2, 80)

    def test_ranking_by_total(self):
        """测试按总分排名"""
        self._add_test_students_for_ranking()
        ranking = self.dm.ranking()
        self.assertEqual(ranking[0]["id"], "003")
        self.assertEqual(ranking[0]["rank"], 1)

    def test_ranking_by_avg(self):
        """测试按平均分排名"""
        self._add_test_students_for_ranking()
        ranking = self.dm.ranking(by="avg")
        self.assertEqual(len(ranking), 3)

    def test_ranking_by_subject(self):
        """测试按科目排名"""
        self._add_test_students_for_ranking()
        ranking = self.dm.ranking(by="subject", subject="数学")
        self.assertEqual(len(ranking), 3)
        self.assertEqual(ranking[0]["id"], "003")

    def test_ranking_empty(self):
        """测试空数据库排名"""
        ranking = self.dm.ranking()
        self.assertEqual(ranking, [])

    def test_ranking_single_student(self):
        """测试单学生排名"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        ranking = self.dm.ranking()
        self.assertEqual(len(ranking), 1)
        self.assertEqual(ranking[0]["rank"], 1)

    def test_ranking_ties(self):
        """测试同分排名"""
        self.dm.add_subject("数学")
        self.dm.add_student("001", "张三", "一班")
        self.dm.set_score("001", "数学", 90)
        self.dm.add_student("002", "李四", "一班")
        self.dm.set_score("002", "数学", 90)
        ranking = self.dm.ranking()
        self.assertEqual(len(ranking), 2)

    def _add_test_students_for_ranking(self):
        """添加测试用学生数据用于排名测试"""
        self.dm.add_subject("数学")
        self.dm.add_student("001", "张三", "一班")
        self.dm.set_score("001", "数学", 70)
        self.dm.add_student("002", "李四", "一班")
        self.dm.set_score("002", "数学", 85)
        self.dm.add_student("003", "王五", "一班")
        self.dm.set_score("003", "数学", 95)

    def _add_test_students_for_analysis(self):
        """添加测试用学生数据用于科目分析测试"""
        self.dm.add_subject("数学")
        self.dm.add_student("001", "张三", "一班")
        self.dm.set_score("001", "数学", 70)
        self.dm.add_student("002", "李四", "一班")
        self.dm.set_score("002", "数学", 85)
        self.dm.add_student("003", "王五", "一班")
        self.dm.set_score("003", "数学", 95)

    # ==================== 科目分析测试 ====================

    def test_analyze_subject(self):
        """测试科目分析"""
        self._add_test_students_for_analysis()
        result = self.dm.analyze_subject("数学")
        self.assertIsNotNone(result)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["max"], 95)
        self.assertEqual(result["min"], 70)
        self.assertAlmostEqual(result["avg"], 83.33, places=2)

    def test_analyze_subject_with_distribution(self):
        """测试科目成绩分布"""
        self._add_test_students_for_analysis()
        result = self.dm.analyze_subject("数学")
        self.assertIn("distribution", result)
        self.assertEqual(result["distribution"]["90-100"], 1)
        self.assertEqual(result["distribution"]["80-89"], 1)
        self.assertEqual(result["distribution"]["70-79"], 1)

    def test_analyze_nonexistent_subject(self):
        """测试分析不存在的科目"""
        result = self.dm.analyze_subject("不存在的科目")
        self.assertIsNone(result)

    def test_analyze_subject_pass_rate(self):
        """测试科目及格率"""
        self._add_test_students_for_analysis()
        result = self.dm.analyze_subject("数学")
        self.assertGreater(result["pass_rate"], 0)

    def test_analyze_subject_excellent_rate(self):
        """测试科目优秀率"""
        self._add_test_students_for_analysis()
        self.dm.set_score("001", "数学", 95)
        result = self.dm.analyze_subject("数学")
        self.assertGreater(result["excellent_rate"], 0)

    def test_analyze_subject_all_zero(self):
        """测试科目全部零分"""
        self.dm.add_subject("数学")
        self.dm.add_student("001", "张三", "一班")
        self.dm.set_score("001", "数学", 0)
        self.dm.add_student("002", "李四", "一班")
        self.dm.set_score("002", "数学", 0)
        result = self.dm.analyze_subject("数学")
        self.assertEqual(result["max"], 0)
        self.assertEqual(result["min"], 0)
        self.assertEqual(result["pass_rate"], 0.0)

    def test_analyze_subject_perfect_score(self):
        """测试科目全部满分"""
        self.dm.add_subject("数学")
        self.dm.add_student("001", "张三", "一班")
        self.dm.set_score("001", "数学", 100)
        result = self.dm.analyze_subject("数学")
        self.assertEqual(result["max"], 100)
        self.assertEqual(result["min"], 100)
        self.assertEqual(result["pass_rate"], 100.0)
        self.assertEqual(result["excellent_rate"], 100.0)

    # ==================== 班级管理测试 ====================

    def test_get_classes(self):
        """测试获取班级列表"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "二班")
        self.dm.add_student("003", "王五", "一班")
        classes = self.dm.classes
        self.assertEqual(len(classes), 2)
        self.assertIn("一班", classes)
        self.assertIn("二班", classes)

    def test_classes_sorted(self):
        """测试班级列表排序"""
        self.dm.add_student("001", "张三", "二班")
        self.dm.add_student("002", "李四", "一班")
        classes = self.dm.classes
        self.assertEqual(classes[0], "一班")
        self.assertEqual(classes[1], "二班")

    def test_classes_empty(self):
        """测试无学生时班级列表为空"""
        classes = self.dm.classes
        self.assertEqual(classes, [])

    def test_classes_unique(self):
        """测试班级列表无重复"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        self.dm.add_student("003", "王五", "一班")
        classes = self.dm.classes
        self.assertEqual(classes, ["一班"])

    def test_get_class_stats(self):
        """测试获取班级统计"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("002", "数学", 80)
        stats = self.dm.get_class_stats("一班")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["class"], "一班")
        self.assertEqual(stats["count"], 2)

    def test_get_class_stats_with_scores(self):
        """测试班级统计含成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.set_score("002", "数学", 80)
        stats = self.dm.get_class_stats("一班")
        self.assertGreater(stats["total_avg"], 0)
        self.assertGreater(stats["max_total"], 0)
        self.assertIn("students", stats)

    def test_get_nonexistent_class_stats(self):
        """测试获取不存在班级的统计"""
        stats = self.dm.get_class_stats("不存在的班级")
        self.assertIsNone(stats)

    def test_get_class_stats_with_empty_class(self):
        """测试获取空班级统计"""
        self.dm.add_student("001", "张三", "")
        stats = self.dm.get_class_stats("")
        self.assertIsNone(stats)

    # ==================== 成绩预警测试 ====================

    def test_get_warnings(self):
        """测试成绩预警"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 55)
        self.dm.set_score("002", "数学", 85)
        warnings = self.dm.get_warnings()
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["name"], "张三")

    def test_no_warnings(self):
        """测试无预警情况"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 85)
        warnings = self.dm.get_warnings()
        self.assertEqual(len(warnings), 0)

    def test_warning_details(self):
        """测试预警详情"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.add_subject("语文")
        self.dm.set_score("001", "数学", 55)
        self.dm.set_score("001", "语文", 45)
        warnings = self.dm.get_warnings()
        self.assertEqual(len(warnings), 1)
        self.assertEqual(len(warnings[0]["fails"]), 2)

    def test_warning_multiple_students(self):
        """测试多个学生预警"""
        self.dm.add_subject("数学")
        self.dm.add_student("001", "张三", "一班")
        self.dm.set_score("001", "数学", 55)
        self.dm.add_student("002", "李四", "一班")
        self.dm.set_score("002", "数学", 45)
        self.dm.add_student("003", "王五", "一班")
        self.dm.set_score("003", "数学", 85)
        warnings = self.dm.get_warnings()
        self.assertEqual(len(warnings), 2)

    # ==================== 搜索功能测试 ====================

    def test_search_by_id(self):
        """测试按学号搜索"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        results = self.dm.search("001")
        self.assertIn("001", results)
        self.assertNotIn("002", results)

    def test_search_by_name(self):
        """测试按姓名搜索"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        results = self.dm.search("张")
        self.assertIn("001", results)

    def test_search_by_class(self):
        """测试按班级搜索"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "二班")
        results = self.dm.search("一班")
        self.assertIn("001", results)
        self.assertNotIn("002", results)

    def test_search_case_insensitive(self):
        """测试搜索大小写不敏感"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "ZHANGSAN", "一班")
        results = self.dm.search("zhangsan")
        self.assertIn("002", results)

    def test_search_no_results(self):
        """测试无搜索结果"""
        self.dm.add_student("001", "张三", "一班")
        results = self.dm.search("不存在的")
        self.assertEqual(len(results), 0)

    def test_search_empty_keyword(self):
        """测试空关键字搜索返回空列表"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        results = self.dm.search("")
        self.assertEqual(len(results), 0)

    def test_search_partial_id(self):
        """测试部分学号匹配"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        self.dm.add_student("101", "王五", "一班")
        results = self.dm.search("01")
        # 应匹配 001 和 101
        self.assertGreaterEqual(len(results), 2)

    def test_search_cross_field(self):
        """测试跨字段搜索"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_student("002", "李四", "一班")
        results = self.dm.search("一班")
        # 应匹配 class=一班的 001 和 002
        self.assertIn("001", results)
        self.assertIn("002", results)

    # ==================== 数据持久化测试 ====================

    def test_save_and_load(self):
        """测试数据保存和加载"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.save()

        new_dm = DataManager(self.test_file)
        self.assertIn("001", new_dm.students)
        self.assertEqual(new_dm.get_student("001")["name"], "张三")

    def test_backup_created(self):
        """测试备份文件创建"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.save()
        backup_file = self.test_file + ".bak"
        self.assertTrue(os.path.exists(backup_file))

    def test_history_persists(self):
        """测试历史记录保存和加载"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        self.dm.save()

        new_dm = DataManager(self.test_file)
        history = new_dm.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["sid"], "001")

    def test_load_from_backup(self):
        """测试损坏时从备份恢复"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.save()
        # 损坏主文件
        with open(self.test_file, "w") as f:
            f.write("{invalid json")
        # 应自动从备份恢复
        new_dm = DataManager(self.test_file)
        self.assertIn("001", new_dm.students)
        self.assertEqual(new_dm.get_student("001")["name"], "张三")

    def test_save_updates_data_integrity(self):
        """测试 save 时校验数据"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.save()
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("history", data)
        self.assertIn("students", data)

    # ==================== 数据完整性测试 ====================

    def test_data_integrity_corrupt_student(self):
        """测试损坏的学生数据被修复"""
        self.dm.add_student("001", "张三", "一班")
        # 手动破坏数据
        self.dm.data["students"]["001"] = "not a dict"
        self.dm._validate_data_integrity()
        self.assertNotIn("001", self.dm.students)

    def test_data_integrity_missing_name(self):
        """测试缺失姓名的学生被修复"""
        self.dm.add_student("001", "张三", "一班")
        del self.dm.data["students"]["001"]["name"]
        self.dm._validate_data_integrity()
        self.assertEqual(self.dm.get_student("001")["name"], "001")

    def test_data_integrity_missing_scores(self):
        """测试缺失成绩字典的学生被修复"""
        self.dm.add_student("001", "张三", "一班")
        del self.dm.data["students"]["001"]["scores"]
        self.dm._validate_data_integrity()
        self.assertEqual(self.dm.get_student("001")["scores"], {})

    def test_data_integrity_corrupt_root(self):
        """测试根数据不是字典时抛出异常"""
        self.dm.data = "corrupt"
        with self.assertRaises(DataIntegrityError):
            self.dm._validate_data_integrity()

    def test_data_integrity_corrupt_subjects(self):
        """测试 subjects 不是列表时抛出异常"""
        self.dm.data["subjects"] = "not a list"
        with self.assertRaises(DataIntegrityError):
            self.dm._validate_data_integrity()

    def test_data_integrity_corrupt_students(self):
        """测试 students 不是字典时抛出异常"""
        self.dm.data["students"] = "not a dict"
        with self.assertRaises(DataIntegrityError):
            self.dm._validate_data_integrity()

    def test_data_integrity_missing_history(self):
        """测试缺失 history 字段时自动创建"""
        del self.dm.data["history"]
        self.dm._validate_data_integrity()
        self.assertEqual(self.dm.data["history"], [])

    def test_data_integrity_preserves_valid(self):
        """测试正常数据不被修改"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 90)
        data_before = dict(self.dm.data)
        self.dm._validate_data_integrity()
        self.assertEqual(self.dm.data["subjects"], data_before["subjects"])
        self.assertEqual(self.dm.data["students"]["001"]["name"], "张三")

    # ==================== 边界条件测试 ====================

    def test_empty_database_stats(self):
        """测试空数据库统计"""
        stats = self.dm.stats("001")
        self.assertIsNone(stats)

    def test_student_with_no_scores(self):
        """测试无成绩学生统计"""
        self.dm.add_student("001", "张三", "一班")
        stats = self.dm.stats("001")
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["avg"], 0)

    def test_special_characters_in_name(self):
        """测试学生姓名含特殊字符"""
        self.dm.add_student("001", "张三·李", "一班")
        student = self.dm.get_student("001")
        self.assertEqual(student["name"], "张三·李")

    def test_long_student_id(self):
        """测试长学号（超出最大长度应抛出异常）"""
        long_id = "2024001" * 5  # 35 chars, exceeds 32 limit
        with self.assertRaises(InvalidInputError):
            self.dm.add_student(long_id, "张三", "一班")

    def test_very_long_name(self):
        """测试长姓名"""
        long_name = "张" * 100
        self.dm.add_student("001", long_name, "一班")
        student = self.dm.get_student("001")
        self.assertEqual(student["name"], long_name)

    def test_many_subjects(self):
        """测试大量科目"""
        subjects = [f"科目{i}" for i in range(50)]
        for sub in subjects:
            self.dm.add_subject(sub)
        self.assertEqual(len(self.dm.subjects), 50)

    def test_score_near_boundaries(self):
        """测试成绩边界值"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        boundaries = [0, 1, 59, 60, 61, 89, 90, 91, 99, 100]
        for score in boundaries:
            self.dm.set_score("001", "数学", score)
            student = self.dm.get_student("001")
            self.assertEqual(student["scores"]["数学"], score)


class TestDataManagerEdgeCases(unittest.TestCase):
    """边界条件测试类"""

    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_grades.json")
        self.dm = DataManager(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_float_score(self):
        """测试浮点数成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 85.5)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 85.5)

    def test_integer_score(self):
        """测试整数成绩"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 100)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 100)

    def test_zero_score(self):
        """测试零分"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 0)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 0)

    def test_boundary_score_60(self):
        """测试及格线边界 60 分"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 60)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 60)

    def test_boundary_score_100(self):
        """测试满分边界 100 分"""
        self.dm.add_student("001", "张三", "一班")
        self.dm.add_subject("数学")
        self.dm.set_score("001", "数学", 100)
        student = self.dm.get_student("001")
        self.assertEqual(student["scores"]["数学"], 100)

    def test_max_students(self):
        """测试大量学生数据"""
        for i in range(1000):
            sid = f"{i:04d}"
            self.dm.add_student(sid, f"学生{i}", "一班")
        self.assertEqual(len(self.dm.students), 1000)

    def test_many_scores_per_student(self):
        """测试单个学生大量科目"""
        self.dm.add_student("001", "张三", "一班")
        for i in range(30):
            sub = f"科目{i}"
            self.dm.add_subject(sub)
            self.dm.set_score("001", sub, i)
        student = self.dm.get_student("001")
        self.assertEqual(len(student["scores"]), 30)


if __name__ == "__main__":
    unittest.main()