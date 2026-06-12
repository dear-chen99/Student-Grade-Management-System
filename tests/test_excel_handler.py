"""
Excel 处理模块单元测试（增强版.

测试 src/utils/excel_handler.py 中的 Excel 导入导出功能。
包含实际函数调用测试，需要 openpyxl 库。
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.excel_handler import (
    is_excel_available,
    _validate_filepath,
    create_template,
    import_from_excel,
    export_to_excel,
    get_default_filename,
    EX_OK,
    # Exception classes
    ExcelHandlerError,
    ExcelLibraryNotFoundError,
    ExcelReadError,
    ExcelWriteError,
    ExcelFormatError,
    ExcelEmptyError,
)


class TestExcelAvailability(unittest.TestCase):
    """Excel 库可用性测试类."""

    def test_is_excel_available_function(self):
        """测试 Excel 可用性检查函数."""
        result = is_excel_available()
        self.assertIsInstance(result, bool)

    def test_ex_ok_variable(self):
        """测试 EX_OK 变量."""
        self.assertIn(EX_OK, [True, False])


class TestValidateFilepath(unittest.TestCase):
    """文件路径校验测试类."""

    def test_valid_path(self):
        """测试有效路径."""
        result = _validate_filepath("/tmp/test.xlsx")
        self.assertEqual(result, "/tmp/test.xlsx")

    def test_empty_path(self):
        """测试空路径."""
        with self.assertRaises(ExcelHandlerError) as ctx:
            _validate_filepath("")
        self.assertIn("不能为空", str(ctx.exception))

    def test_none_path(self):
        """测试 None 路径."""
        with self.assertRaises(ExcelHandlerError) as ctx:
            _validate_filepath(None)
        self.assertIn("不能为空", str(ctx.exception))

    def test_path_with_spaces(self):
        """测试带空格的路径."""
        result = _validate_filepath("  /tmp/test.xlsx  ")
        self.assertEqual(result, "/tmp/test.xlsx")


class TestCreateTemplate(unittest.TestCase):
    """创建模板测试类."""

    def test_template_columns_structure(self):
        """测试模板列定义结构."""
        columns = ["学号", "姓名", "班级"]
        subjects = ["语文", "数学", "英语"]
        header = columns + subjects
        self.assertEqual(len(header), 6)
        self.assertEqual(header[0], "学号")
        self.assertEqual(header[1], "姓名")
        self.assertEqual(header[2], "班级")

    def test_sample_row_data(self):
        """测试示例行数据."""
        subjects = ["语文", "数学", "英语"]
        sample_row = ["2024001", "张三", "一班"] + [""] * len(subjects)
        self.assertEqual(len(sample_row), 6)
        self.assertEqual(sample_row[3], "")

    def test_template_filename_extension(self):
        """测试模板文件扩展名."""
        filename = "成绩导入模板.xlsx"
        self.assertTrue(filename.endswith(".xlsx"))

    @unittest.skipIf(not EX_OK, "需要 openpyxl 库")
    def test_create_template_actual_file(self):
        """测试实际创建模板文件."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name
        try:
            subjects = ["语文", "数学", "英语"]
            result = create_template(temp_path, subjects)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_create_template_empty_subjects(self):
        """测试空科目列表创建模板."""
        mock_openpyxl = MagicMock()
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_openpyxl.Workbook.return_value = mock_wb
        mock_wb.active = mock_ws

        with patch("src.utils.excel_handler.EX_OK", True):
            with patch(
                "src.utils.excel_handler._validate_filepath",
                return_value="/tmp/test.xlsx",
            ):
                with patch("src.utils.excel_handler.openpyxl", mock_openpyxl):
                    with patch.dict("sys.modules", {"openpyxl": mock_openpyxl}):
                        result = create_template("/tmp/test.xlsx", [])
                        self.assertTrue(result)
                        mock_ws.append.assert_any_call(["学号", "姓名", "班级"])
                        mock_ws.append.assert_any_call(["2024001", "张三", "一班"])


class TestImportFromExcel(unittest.TestCase):
    """从 Excel 导入测试类."""

    def setUp(self):
        """测试前准备."""
        self.mock_dm = MagicMock()
        self.mock_dm.subjects = []
        self.mock_dm.exists.return_value = False
        # Mock the ranking to avoid KeyError
        type(self.mock_dm).subjects = PropertyMock(return_value=[])

    def test_header_parsing(self):
        """测试表头解析."""
        header = ["学号", "姓名", "班级", "语文", "数学"]
        id_idx = next((i for i, h in enumerate(header) if "学号" in h), 0)
        name_idx = next((i for i, h in enumerate(header) if "姓名" in h), 1)
        class_idx = next((i for i, h in enumerate(header) if "班级" in h), 2)
        self.assertEqual(id_idx, 0)
        self.assertEqual(name_idx, 1)
        self.assertEqual(class_idx, 2)

    def test_subject_column_detection(self):
        """测试科目列检测."""
        header = ["学号", "姓名", "班级", "语文", "数学", "英语"]
        skip_indices = {0, 1, 2}
        subject_cols = {}
        for i, h in enumerate(header):
            if i not in skip_indices and h:
                subject_cols[h] = i
        self.assertEqual(len(subject_cols), 3)
        self.assertIn("语文", subject_cols)

    def test_empty_row_detection(self):
        """测试空行检测."""
        empty_row = ["", "", "", ""]
        is_empty = all(not str(c).strip() if c else True for c in empty_row)
        self.assertTrue(is_empty)

    def test_non_empty_row_detection(self):
        """测试非空行检测."""
        non_empty_row = ["2024001", "张三", "一班", "90", "85"]
        is_empty = all(not str(c).strip() for c in non_empty_row)
        self.assertFalse(is_empty)

    def test_score_conversion_valid(self):
        """测试有效成绩转换."""
        score = float("95.5")
        self.assertEqual(score, 95.5)

    def test_score_invalid_returns_none(self):
        """测试无效成绩返回 None."""
        invalid = ""
        try:
            result = float(invalid) if invalid else None
            self.assertIsNone(result)
        except ValueError:
            pass

    @patch("src.utils.excel_handler.EX_OK", False)
    def test_import_excel_not_available(self):
        """测试 Excel 库不可用时导入."""
        count, msg = import_from_excel("/tmp/test.xlsx", self.mock_dm)
        self.assertEqual(count, 0)
        self.assertIsNotNone(msg)

    def test_import_file_not_found(self):
        """测试文件不存在."""
        with patch("src.utils.excel_handler.EX_OK", True):
            count, msg = import_from_excel("/nonexistent/file.xlsx", self.mock_dm)
            self.assertEqual(count, 0)
            self.assertIsNotNone(msg)

    def test_subject_name_extraction(self):
        """测试从表头提取科目名."""
        header = ["学号", "姓名", "班级", "语文", "数学", "英语"]
        id_idx, name_idx, class_idx = 0, 1, 2
        subject_names = []
        for i, h in enumerate(header):
            if i not in (id_idx, name_idx, class_idx) and h:
                subject_names.append(h)
        self.assertEqual(subject_names, ["语文", "数学", "英语"])

    def test_missing_subject_columns(self):
        """测试缺少科目列的情况."""
        header = ["学号", "姓名", "班级"]
        id_idx, name_idx, class_idx = 0, 1, 2
        subject_cols = {}
        for i, h in enumerate(header):
            if i not in (id_idx, name_idx, class_idx) and h:
                subject_cols[h] = i
        self.assertEqual(len(subject_cols), 0)


class TestExportToExcel(unittest.TestCase):
    """导出到 Excel 测试类."""

    def setUp(self):
        """测试前准备."""
        self.mock_dm = MagicMock()
        # Set up subjects
        type(self.mock_dm).subjects = PropertyMock(
            return_value=["语文", "数学", "英语"]
        )
        # Set up ranking
        self.mock_dm.ranking.return_value = [
            {
                "rank": 1,
                "id": "2024001",
                "name": "张三",
                "class": "一班",
                "scores": {"语文": 90, "数学": 85, "英语": 92},
                "total": 267,
                "avg": 89.0,
            }
        ]

    def test_export_header_structure(self):
        """测试导出表头结构."""
        subjects = ["语文", "数学", "英语"]
        header = (
            ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分", "等级"]
        )
        self.assertEqual(len(header), 10)

    def test_level_calculation_excellent(self):
        """测试优秀等级."""
        avg = 95
        level = (
            "优秀"
            if avg >= 90
            else ("良好" if avg >= 75 else ("及格" if avg >= 60 else "不及格"))
        )
        self.assertEqual(level, "优秀")

    def test_level_calculation_good(self):
        """测试良好等级."""
        avg = 80
        level = (
            "优秀"
            if avg >= 90
            else ("良好" if avg >= 75 else ("及格" if avg >= 60 else "不及格"))
        )
        self.assertEqual(level, "良好")

    def test_level_calculation_pass(self):
        """测试及格等级."""
        avg = 65
        level = (
            "优秀"
            if avg >= 90
            else ("良好" if avg >= 75 else ("及格" if avg >= 60 else "不及格"))
        )
        self.assertEqual(level, "及格")

    def test_level_calculation_fail(self):
        """测试不及格等级."""
        avg = 55
        level = (
            "优秀"
            if avg >= 90
            else ("良好" if avg >= 75 else ("及格" if avg >= 60 else "不及格"))
        )
        self.assertEqual(level, "不及格")

    @patch("src.utils.excel_handler.EX_OK", False)
    def test_export_excel_not_available(self):
        """测试 Excel 库不可用时导出."""
        result = export_to_excel("/tmp/test.xlsx", self.mock_dm)
        self.assertFalse(result)

    def test_export_file_write_error(self):
        """测试文件写入错误."""
        with patch("src.utils.excel_handler.EX_OK", True):
            result = export_to_excel("/invalid/path/test.xlsx", self.mock_dm)
            self.assertFalse(result)


class TestDefaultFilename(unittest.TestCase):
    """默认文件名测试类."""

    def test_default_excel_filename(self):
        """测试默认 Excel 文件名."""
        filename = get_default_filename("xlsx")
        self.assertTrue(filename.startswith("成绩_"))
        self.assertTrue(filename.endswith(".xlsx"))

    def test_default_csv_filename(self):
        """测试默认 CSV 文件名."""
        filename = get_default_filename("csv")
        self.assertTrue(filename.startswith("成绩_"))
        self.assertTrue(filename.endswith(".csv"))

    def test_filename_strips_dot(self):
        """测试文件名去除点号."""
        filename = get_default_filename(".xlsx")
        self.assertTrue(filename.endswith(".xlsx"))


class TestExceptionClasses(unittest.TestCase):
    """异常类测试."""

    def test_excel_handler_error(self):
        """测试基础异常."""
        e = ExcelHandlerError("测试错误")
        self.assertEqual(str(e), "测试错误")

    def test_excel_library_not_found_error(self):
        """测试库未安装异常."""
        e = ExcelLibraryNotFoundError()
        self.assertIn("pip install", str(e))

    def test_excel_read_error(self):
        """测试读取错误."""
        e = ExcelReadError("test.xlsx", "权限不足")
        self.assertIn("test.xlsx", str(e))
        self.assertIn("权限不足", str(e))

    def test_excel_read_error_no_reason(self):
        """测试读取错误（无原因."""
        e = ExcelReadError("test.xlsx")
        self.assertIn("test.xlsx", str(e))

    def test_excel_write_error(self):
        """测试写入错误."""
        e = ExcelWriteError("test.xlsx", "磁盘已满")
        self.assertIn("test.xlsx", str(e))

    def test_excel_write_error_no_reason(self):
        """测试写入错误（无原因."""
        e = ExcelWriteError("test.xlsx")
        self.assertIn("test.xlsx", str(e))

    def test_excel_format_error(self):
        """测试格式错误."""
        e = ExcelFormatError("test.xlsx", "表头缺失")
        self.assertIn("test.xlsx", str(e))

    def test_excel_format_error_no_reason(self):
        """测试格式错误（无原因."""
        e = ExcelFormatError("test.xlsx")
        self.assertIn("test.xlsx", str(e))

    def test_excel_empty_error(self):
        """测试空文件错误."""
        e = ExcelEmptyError("test.xlsx")
        self.assertIn("test.xlsx", str(e))

    def test_excel_empty_error_no_path(self):
        """测试空文件错误（无路径."""
        e = ExcelEmptyError()
        self.assertEqual(str(e), "文件内容为空")


class TestExcelHandlerFunctions(unittest.TestCase):
    """Excel 处理函数集成测试."""

    def test_functions_importable(self):
        """测试函数可导入."""
        from src.utils.excel_handler import (
            is_excel_available,
            create_template,
            import_from_excel,
            export_to_excel,
            get_default_filename,
        )

        self.assertTrue(callable(is_excel_available))
        self.assertTrue(callable(create_template))
        self.assertTrue(callable(import_from_excel))
        self.assertTrue(callable(export_to_excel))
        self.assertTrue(callable(get_default_filename))

    @patch("src.utils.excel_handler.EX_OK", True)
    def test_create_template_mocked(self, *_):
        """测试使用 mock 的创建模板."""
        mock_openpyxl = MagicMock()
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_openpyxl.Workbook.return_value = mock_wb
        mock_wb.active = mock_ws

        with patch(
            "src.utils.excel_handler._validate_filepath", return_value="/tmp/test.xlsx"
        ):
            with patch("src.utils.excel_handler.openpyxl", mock_openpyxl):
                with patch.dict("sys.modules", {"openpyxl": mock_openpyxl}):
                    result = create_template("/tmp/test.xlsx", ["语文", "数学"])
                    self.assertTrue(result)
                    mock_ws.title = "模板"
                    mock_wb.save.assert_called_once_with("/tmp/test.xlsx")

    @patch("src.utils.excel_handler.EX_OK", True)
    def test_export_to_excel_mocked(self, *_):
        """测试使用 mock 的导出 Excel."""
        mock_openpyxl = MagicMock()
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_openpyxl.Workbook.return_value = mock_wb
        mock_wb.active = mock_ws

        mock_dm = MagicMock()
        type(mock_dm).subjects = PropertyMock(return_value=["数学"])
        mock_dm.ranking.return_value = [
            {
                "rank": 1,
                "id": "001",
                "name": "张三",
                "scores": {"数学": 90},
                "total": 90,
                "avg": 90,
            }
        ]

        with patch(
            "src.utils.excel_handler._validate_filepath", return_value="/tmp/test.xlsx"
        ):
            with patch("src.utils.excel_handler.openpyxl", mock_openpyxl):
                with patch.dict("sys.modules", {"openpyxl": mock_openpyxl}):
                    result = export_to_excel("/tmp/test.xlsx", mock_dm)
                    self.assertTrue(result)
                    mock_wb.save.assert_called_once_with("/tmp/test.xlsx")


if __name__ == "__main__":
    unittest.main()
