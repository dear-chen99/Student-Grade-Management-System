"""
数据导出模块单元测试.

测试 src/utils/export.py 中的 CSV 导出功能。
包含实际函数调用测试（使用临时文件）。
"""

import csv
import datetime
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, PropertyMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.export import export_to_csv, get_default_filename, export_statistics


class TestExportToCsv(unittest.TestCase):
    """导出到 CSV 测试类."""

    def setUp(self):
        """测试前准备."""
        # Create a proper mock DataManager
        self.mock_dm = MagicMock()
        type(self.mock_dm).subjects = PropertyMock(
            return_value=["语文", "数学", "英语"]
        )
        self.mock_dm.ranking.return_value = [
            {
                "rank": 1,
                "id": "2024001",
                "name": "张三",
                "class": "一班",
                "scores": {"语文": 90, "数学": 85, "英语": 92},
                "total": 267,
                "avg": 89.0,
            },
            {
                "rank": 2,
                "id": "2024002",
                "name": "李四",
                "class": "二班",
                "scores": {"语文": 85, "数学": 90, "英语": 88},
                "total": 263,
                "avg": 87.67,
            },
        ]

    def test_csv_header_format(self):
        """测试 CSV 表头格式."""
        subjects = self.mock_dm.subjects
        header = ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        self.assertEqual(len(header), 9)
        self.assertIn("排名", header)
        self.assertIn("学号", header)

    def test_rank_data_row_format(self):
        """测试排名数据行格式."""
        rank_data = self.mock_dm.ranking()[0]
        subjects = self.mock_dm.subjects
        row = (
            [
                rank_data["rank"],
                rank_data["id"],
                rank_data["name"],
                rank_data.get("class", ""),
            ]
            + [rank_data["scores"].get(s, "-") for s in subjects]
            + [rank_data["total"], rank_data["avg"]]
        )
        self.assertEqual(len(row), 9)
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], "2024001")

    def test_missing_score_handling(self):
        """测试缺失成绩处理."""
        scores = {"语文": 90}
        subjects = ["语文", "数学"]
        result = [scores.get(s, "-") for s in subjects]
        self.assertEqual(result, [90, "-"])

    def test_empty_class_handling(self):
        """测试空班级处理."""
        class_value = ""
        result = class_value if class_value else ""
        self.assertEqual(result, "")

    def test_actual_csv_export(self):
        """测试实际 CSV 导出."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, self.mock_dm)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)

            # Verify content
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 3)
                self.assertEqual(rows[0][0], "排名")
                self.assertEqual(rows[1][1], "2024001")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_csv_export_empty_data(self):
        """测试空数据导出."""
        empty_dm = MagicMock()
        type(empty_dm).subjects = PropertyMock(return_value=[])
        empty_dm.ranking.return_value = []

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, empty_dm)
            self.assertTrue(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_csv_export_write_error(self):
        """测试写入错误."""
        result = export_to_csv("/invalid/path/file.csv", self.mock_dm)
        self.assertFalse(result)

    def test_csv_export_with_no_class(self):
        """测试无班级数据导出."""
        dm = MagicMock()
        type(dm).subjects = PropertyMock(return_value=["数学"])
        dm.ranking.return_value = [
            {
                "rank": 1,
                "id": "001",
                "name": "张三",
                "scores": {"数学": 90},
                "total": 90,
                "avg": 90,
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, dm)
            self.assertTrue(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_csv_export_all_subjects_missing(self):
        """测试所有成绩缺失."""
        dm = MagicMock()
        type(dm).subjects = PropertyMock(return_value=["数学", "语文"])
        dm.ranking.return_value = [
            {
                "rank": 1,
                "id": "001",
                "name": "张三",
                "scores": {},
                "total": 0,
                "avg": 0,
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, dm)
            self.assertTrue(result)
            # Verify dashes for missing scores
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("-", content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDefaultFilename(unittest.TestCase):
    """默认文件名测试类."""

    def test_default_csv_filename(self):
        """测试默认 CSV 文件名."""
        filename = get_default_filename()
        self.assertTrue(filename.startswith("成绩_"))
        self.assertTrue(filename.endswith(".csv"))

    def test_filename_contains_date(self):
        """测试文件名包含日期."""
        filename = get_default_filename()
        today = str(datetime.date.today())
        self.assertIn(today, filename)


class TestExportStatistics(unittest.TestCase):
    """导出统计测试类."""

    def setUp(self):
        """测试前准备."""
        self.mock_dm = MagicMock()
        type(self.mock_dm).students = PropertyMock(return_value={"001": {}, "002": {}})
        type(self.mock_dm).subjects = PropertyMock(return_value=["数学", "语文"])
        self.mock_dm.analyze_subject.side_effect = lambda s: {
            "数学": {
                "count": 2,
                "avg": 85,
                "max": 95,
                "min": 75,
                "pass_rate": 100.0,
                "excellent_rate": 50.0,
            },
            "语文": {
                "count": 2,
                "avg": 80,
                "max": 90,
                "min": 70,
                "pass_rate": 100.0,
                "excellent_rate": 50.0,
            },
        }.get(s)

    def test_statistics_structure(self):
        """测试统计数据结构."""
        stats = {"count": 50, "avg": 78.5}
        self.assertIn("count", stats)
        self.assertIn("avg", stats)

    def test_subject_analysis_structure(self):
        """测试科目分析数据结构."""
        analysis = {"avg": 85.5, "max": 98, "min": 62, "pass_rate": 0.92}
        self.assertIn("avg", analysis)
        self.assertIn("max", analysis)
        self.assertIn("min", analysis)

    def test_pass_rate_percentage(self):
        """测试及格率百分比."""
        pass_rate = 85.0
        percentage = f"{pass_rate:.1f}%"
        self.assertEqual(percentage, "85.0%")

    def test_actual_statistics_export(self):
        """测试实际统计导出."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_statistics(temp_path, self.mock_dm)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))

            with open(temp_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("学生统计", content)
            self.assertIn("科目统计", content)
            self.assertIn("数学", content)
            self.assertIn("语文", content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_statistics_export_empty_subjects(self):
        """测试空科目统计导出."""
        dm = MagicMock()
        type(dm).students = PropertyMock(return_value={})
        type(dm).subjects = PropertyMock(return_value=[])

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_statistics(temp_path, dm)
            self.assertTrue(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_statistics_export_write_error(self):
        """测试统计导出写入错误."""
        result = export_statistics("/invalid/path/file.csv", self.mock_dm)
        self.assertFalse(result)

    def test_statistics_empty_student_count(self):
        """测试空学生数."""
        dm = MagicMock()
        type(dm).students = PropertyMock(return_value={})
        type(dm).subjects = PropertyMock(return_value=["数学"])

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_statistics(temp_path, dm)
            self.assertTrue(result)
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("0", content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_statistics_header(self):
        """测试统计表头."""
        header = ["科目", "平均分", "最高分", "最低分", "及格率"]
        self.assertEqual(len(header), 5)
        self.assertEqual(header[0], "科目")


class TestExportEdgeCases(unittest.TestCase):
    """导出边界情况测试类."""

    def test_empty_subjects_list(self):
        """测试空科目列表."""
        subjects = []
        header = ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        self.assertEqual(len(header), 6)

    def test_empty_scores_dict(self):
        """测试空成绩字典."""
        scores = {}
        subjects = ["语文", "数学"]
        result = [scores.get(s, "-") for s in subjects]
        self.assertEqual(result, ["-", "-"])

    def test_all_missing_scores(self):
        """测试全部缺失成绩."""
        scores = {}
        subjects = ["语文", "数学", "英语"]
        result = [scores.get(s, "-") for s in subjects]
        self.assertEqual(result, ["-", "-", "-"])

    def test_special_characters(self):
        """测试特殊字符."""
        name = "张三·李四"
        self.assertIn("·", name)

    def test_mixed_types_in_scores(self):
        """测试成绩混合类型."""
        scores = {"数学": "-", "语文": 85.5}
        math_val = scores.get("数学")
        chn_val = scores.get("语文")
        self.assertEqual(math_val, "-")
        self.assertEqual(chn_val, 85.5)

    def test_unicode_in_export(self):
        """测试 Unicode 字符."""
        names = ["张三", "李四", "王五"]
        for name in names:
            self.assertTrue(len(name) > 0)
            self.assertIsInstance(name, str)

    def test_export_with_single_student(self):
        """测试单学生导出."""
        dm = MagicMock()
        type(dm).subjects = PropertyMock(return_value=["数学"])
        dm.ranking.return_value = [
            {
                "rank": 1,
                "id": "001",
                "name": "张三",
                "scores": {"数学": 95},
                "total": 95,
                "avg": 95,
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", suffix=".csv", encoding="utf-8-sig"
        ) as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, dm)
            self.assertTrue(result)
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)  # header + 1 student
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_with_large_scores(self):
        """测试大数字成绩."""
        scores = {"数学": 100, "语文": 99.5}
        self.assertEqual(scores["数学"], 100)
        self.assertEqual(scores["语文"], 99.5)


if __name__ == "__main__":
    unittest.main()
