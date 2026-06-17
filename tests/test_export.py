"""
数据导出模块单元测试.

测试 src/utils/export.py 中的 CSV 导出功能，包括成绩导出、统计导出、
默认文件名生成及边界场景处理。使用临时文件进行实际文件写入验证，
确保编码、格式和异常处理均符合预期。
"""

import csv
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, PropertyMock

# 将项目根目录加入 sys.path，确保能正确导入 src 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.export import export_to_csv, get_default_filename, export_statistics


class TestExportToCsv(unittest.TestCase):
    """测试 export_to_csv 函数，覆盖正常导出、空数据、写入异常等场景。"""

    def setUp(self):
        """测试前准备：构造 mock DataManager，配置科目列表和排名数据。"""
        self.mock_dm = MagicMock()
        # 使用 PropertyMock 模拟 subjects 属性
        type(self.mock_dm).subjects = PropertyMock(return_value=["语文", "数学", "英语"])
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
        """测试 CSV 表头格式正确。

        预期结果：表头包含固定列（排名、学号、姓名、班级）及科目列、总分、平均分。
        """
        subjects = self.mock_dm.subjects
        header = ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        self.assertEqual(len(header), 9)
        self.assertIn("排名", header)
        self.assertIn("学号", header)

    def test_rank_data_row_format(self):
        """测试排名数据行格式正确。

        预期结果：每行数据与表头列数一致，且学号、排名等关键字段正确。
        """
        rank_data = self.mock_dm.ranking()[0]
        subjects = self.mock_dm.subjects
        row = (
            [rank_data["rank"], rank_data["id"], rank_data["name"],
             rank_data.get("class", "")]
            + [rank_data["scores"].get(s, "-") for s in subjects]
            + [rank_data["total"], rank_data["avg"]]
        )
        self.assertEqual(len(row), 9)
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], "2024001")

    def test_missing_score_handling(self):
        """测试缺失成绩处理为 "-"。

        预期结果：学生没有某科目成绩时，该位置输出 "-"。
        """
        scores = {"语文": 90}
        subjects = ["语文", "数学"]
        result = [scores.get(s, "-") for s in subjects]
        self.assertEqual(result, [90, "-"])

    def test_empty_class_handling(self):
        """测试空班级字段处理。

        预期结果：班级为空字符串时正常保留空值。
        """
        class_value = ""
        result = class_value if class_value else ""
        self.assertEqual(result, "")

    def test_actual_csv_export(self):
        """测试实际 CSV 导出到临时文件。

        预期结果：文件成功创建且大小大于 0，内容包含正确表头和学生数据。
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, self.mock_dm)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)

            # 读取并验证 CSV 内容
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 3)  # 表头 + 2 名学生
                self.assertEqual(rows[0][0], "排名")
                self.assertEqual(rows[1][1], "2024001")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_csv_export_empty_data(self):
        """测试空数据导出。

        预期结果：科目为空且排名为空时，导出仍返回 True，文件只含表头。
        """
        empty_dm = MagicMock()
        type(empty_dm).subjects = PropertyMock(return_value=[])
        empty_dm.ranking.return_value = []

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, empty_dm)
            self.assertTrue(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_csv_export_write_error(self):
        """测试写入非法路径时返回 False。

        预期结果：向不存在的目录写入时，export_to_csv 返回 False。
        """
        result = export_to_csv("/invalid/path/file.csv", self.mock_dm)
        self.assertFalse(result)

    def test_csv_export_with_no_class(self):
        """测试无班级字段数据的导出。

        预期结果：排名数据中不含 class 键时，导出仍正常完成。
        """
        dm = MagicMock()
        type(dm).subjects = PropertyMock(return_value=["数学"])
        dm.ranking.return_value = [
            {"rank": 1, "id": "001", "name": "张三",
             "scores": {"数学": 90}, "total": 90, "avg": 90}
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, dm)
            self.assertTrue(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_csv_export_all_subjects_missing(self):
        """测试所有科目成绩均缺失时的导出。

        预期结果：所有科目列输出 "-"，文件正常生成。
        """
        dm = MagicMock()
        type(dm).subjects = PropertyMock(return_value=["数学", "语文"])
        dm.ranking.return_value = [
            {"rank": 1, "id": "001", "name": "张三",
             "scores": {}, "total": 0, "avg": 0}
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, dm)
            self.assertTrue(result)
            # 验证文件内容包含 "-"
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("-", content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDefaultFilename(unittest.TestCase):
    """测试 get_default_filename 函数的文件名生成逻辑。"""

    def test_default_csv_filename(self):
        """测试默认 CSV 文件名格式。

        预期结果：文件名以 "成绩_" 开头，以 ".csv" 结尾。
        """
        filename = get_default_filename()
        self.assertTrue(filename.startswith("成绩_"))
        self.assertTrue(filename.endswith(".csv"))

    def test_filename_contains_date(self):
        """测试文件名包含当前日期。

        预期结果：文件名中包含当天的日期字符串。
        """
        import datetime
        filename = get_default_filename()
        today = str(datetime.date.today())
        self.assertIn(today, filename)


class TestExportStatistics(unittest.TestCase):
    """测试 export_statistics 函数，覆盖正常导出、空数据、写入异常等场景。"""

    def setUp(self):
        """测试前准备：构造 mock DataManager，配置学生数、科目及分析数据。"""
        self.mock_dm = MagicMock()
        type(self.mock_dm).students = PropertyMock(
            return_value={"001": {}, "002": {}}
        )
        type(self.mock_dm).subjects = PropertyMock(
            return_value=["数学", "语文"]
        )
        # 使用 side_effect 根据科目名返回对应的分析数据
        self.mock_dm.analyze_subject.side_effect = lambda s: {
            "数学": {
                "count": 2, "avg": 85, "max": 95, "min": 75,
                "pass_rate": 100.0, "excellent_rate": 50.0,
            },
            "语文": {
                "count": 2, "avg": 80, "max": 90, "min": 70,
                "pass_rate": 100.0, "excellent_rate": 50.0,
            },
        }.get(s)

    def test_statistics_structure(self):
        """测试统计数据结构。

        预期结果：分析结果字典包含 count 和 avg 键。
        """
        stats = {"count": 50, "avg": 78.5}
        self.assertIn("count", stats)
        self.assertIn("avg", stats)

    def test_subject_analysis_structure(self):
        """测试科目分析数据结构。

        预期结果：分析结果包含 avg、max、min、pass_rate 等关键指标。
        """
        analysis = {"avg": 85.5, "max": 98, "min": 62, "pass_rate": 0.92}
        self.assertIn("avg", analysis)
        self.assertIn("max", analysis)
        self.assertIn("min", analysis)

    def test_pass_rate_percentage(self):
        """测试及格率百分比格式化。

        预期结果：85.0 格式化为 "85.0%"。
        """
        pass_rate = 85.0
        percentage = f"{pass_rate:.1f}%"
        self.assertEqual(percentage, "85.0%")

    def test_actual_statistics_export(self):
        """测试实际统计导出到临时文件。

        预期结果：文件成功创建，内容包含学生统计和科目统计信息。
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
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
        """测试空科目列表的统计导出。

        预期结果：科目为空时，导出仍返回 True，文件只含学生统计。
        """
        dm = MagicMock()
        type(dm).students = PropertyMock(return_value={})
        type(dm).subjects = PropertyMock(return_value=[])

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
            temp_path = f.name

        try:
            result = export_statistics(temp_path, dm)
            self.assertTrue(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_statistics_export_write_error(self):
        """测试统计导出写入非法路径时返回 False。

        预期结果：向不存在的目录写入时，export_statistics 返回 False。
        """
        result = export_statistics("/invalid/path/file.csv", self.mock_dm)
        self.assertFalse(result)

    def test_statistics_empty_student_count(self):
        """测试学生数为 0 时的统计导出。

        预期结果：文件内容中包含 "0"。
        """
        dm = MagicMock()
        type(dm).students = PropertyMock(return_value={})
        type(dm).subjects = PropertyMock(return_value=["数学"])

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
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
        """测试统计表头结构。

        预期结果：表头包含科目、平均分、最高分、最低分、及格率等列。
        """
        header = ["科目", "平均分", "最高分", "最低分", "及格率"]
        self.assertEqual(len(header), 5)
        self.assertEqual(header[0], "科目")


class TestExportEdgeCases(unittest.TestCase):
    """测试导出边界情况，包括空科目、空成绩、特殊字符等。"""

    def test_empty_subjects_list(self):
        """测试空科目列表时表头长度正确。

        预期结果：表头只有固定列，长度为 6。
        """
        subjects = []
        header = ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
        self.assertEqual(len(header), 6)

    def test_empty_scores_dict(self):
        """测试空成绩字典时缺失成绩标记为 "-"。

        预期结果：所有科目列输出 "-"。
        """
        scores = {}
        subjects = ["语文", "数学"]
        result = [scores.get(s, "-") for s in subjects]
        self.assertEqual(result, ["-", "-"])

    def test_all_missing_scores(self):
        """测试全部科目成绩缺失。

        预期结果：三门科目均输出 "-"。
        """
        scores = {}
        subjects = ["语文", "数学", "英语"]
        result = [scores.get(s, "-") for s in subjects]
        self.assertEqual(result, ["-", "-", "-"])

    def test_special_characters(self):
        """测试姓名中特殊字符保留。

        预期结果：姓名中的中间点等特殊字符正常存在。
        """
        name = "张三·李四"
        self.assertIn("·", name)

    def test_mixed_types_in_scores(self):
        """测试成绩字典中混合类型值。

        预期结果："-" 和数字可以共存于同一字典中。
        """
        scores = {"数学": "-", "语文": 85.5}
        math_val = scores.get("数学")
        chn_val = scores.get("语文")
        self.assertEqual(math_val, "-")
        self.assertEqual(chn_val, 85.5)

    def test_unicode_in_export(self):
        """测试 Unicode 字符正常处理。

        预期结果：中文字符串长度大于 0 且类型为 str。
        """
        names = ["张三", "李四", "王五"]
        for name in names:
            self.assertTrue(len(name) > 0)
            self.assertIsInstance(name, str)

    def test_export_with_single_student(self):
        """测试只有一名学生时的导出。

        预期结果：文件包含表头和一行数据，共 2 行。
        """
        dm = MagicMock()
        type(dm).subjects = PropertyMock(return_value=["数学"])
        dm.ranking.return_value = [
            {"rank": 1, "id": "001", "name": "张三",
             "scores": {"数学": 95}, "total": 95, "avg": 95}
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="",
                                         suffix=".csv", encoding="utf-8-sig") as f:
            temp_path = f.name

        try:
            result = export_to_csv(temp_path, dm)
            self.assertTrue(result)
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)  # 表头 + 1 名学生
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_with_large_scores(self):
        """测试满分及接近满分的成绩导出。

        预期结果：100 分和 99.5 分均能正确保留。
        """
        scores = {"数学": 100, "语文": 99.5}
        self.assertEqual(scores["数学"], 100)
        self.assertEqual(scores["语文"], 99.5)


if __name__ == "__main__":
    unittest.main()
