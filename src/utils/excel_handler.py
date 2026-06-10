#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 处理模块 - Excel Handler Module

提供 Excel 文件的导入导出功能，支持 .xlsx 和 .xls 格式。
"""

import datetime
import logging
import os
from typing import Any, Optional, Tuple

# 配置模块级日志
logger = logging.getLogger("ExcelHandler")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(_handler)


# ------------------------------------------------------------------
# 自定义异常类
# ------------------------------------------------------------------

class ExcelHandlerError(Exception):
    """Excel 处理模块基础异常类。"""

    def __init__(self, message: str = "Excel 处理错误") -> None:
        super().__init__(message)
        self.message = message


class ExcelLibraryNotFoundError(ExcelHandlerError):
    """Excel 库未安装错误。"""

    def __init__(self) -> None:
        super().__init__("请执行：pip install openpyxl 安装 Excel 处理库")


class ExcelReadError(ExcelHandlerError):
    """Excel 文件读取错误。"""

    def __init__(self, filepath: str, reason: str = "") -> None:
        msg = f"无法读取 Excel 文件: {filepath}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class ExcelWriteError(ExcelHandlerError):
    """Excel 文件写入错误。"""

    def __init__(self, filepath: str, reason: str = "") -> None:
        msg = f"无法写入 Excel 文件: {filepath}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class ExcelFormatError(ExcelHandlerError):
    """Excel 文件格式错误。"""

    def __init__(self, filepath: str, reason: str = "") -> None:
        msg = f"Excel 文件格式不正确: {filepath}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class ExcelEmptyError(ExcelHandlerError):
    """Excel 文件内容为空错误。"""

    def __init__(self, filepath: str = "") -> None:
        base = f"文件内容为空: {filepath}" if filepath else "文件内容为空"
        super().__init__(base)


# ------------------------------------------------------------------
# Excel 库可用性检查
# ------------------------------------------------------------------

EX_OK: bool = False
try:
    import openpyxl  # noqa: F401

    EX_OK = True
    logger.debug("openpyxl 导入成功")
except ImportError:
    try:
        import xlrd  # noqa: F401

        EX_OK = True
        logger.debug("xlrd 导入成功")
    except ImportError:
        logger.warning("Excel 处理库未安装，请执行: pip install openpyxl")


def is_excel_available() -> bool:
    """检查 Excel 处理库是否可用。

    Returns:
        True 如果 openpyxl 或 xlrd 可用。
    """
    return EX_OK


def _validate_filepath(filepath: str) -> str:
    """校验文件路径的合法性。

    Args:
        filepath: 文件路径。

    Returns:
        规范化后的文件路径。

    Raises:
        ExcelHandlerError: 路径无效时抛出。
    """
    if not filepath or not isinstance(filepath, str):
        raise ExcelHandlerError("文件路径不能为空")
    filepath = filepath.strip()
    if not filepath:
        raise ExcelHandlerError("文件路径不能为空")
    return filepath


# ------------------------------------------------------------------
# 公共方法
# ------------------------------------------------------------------

def create_template(filepath: str, subjects: list[str]) -> bool:
    """创建 Excel 成绩导入模板。

    生成包含表头（学号、姓名、班级 + 科目）和一行示例数据的 .xlsx 文件。

    Args:
        filepath: 保存路径。
        subjects: 科目名称列表。

    Returns:
        True 表示创建成功，False 表示失败。
    """
    if not EX_OK:
        logger.error("创建模板失败: Excel 库未安装")
        return False

    try:
        filepath = _validate_filepath(filepath)
    except ExcelHandlerError as e:
        logger.error("创建模板失败: %s", e)
        return False

    if not subjects:
        logger.warning("创建模板时科目列表为空")

    try:
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        if ws is None:
            logger.error("创建模板失败: 无法获取活动工作表")
            return False
        ws.title = "模板"
        ws.append(["学号", "姓名", "班级"] + list(subjects))
        ws.append(["2024001", "张三", "一班"] + [""] * len(subjects))
        wb.save(filepath)
        logger.info("Excel 模板已创建: %s", filepath)
        return True

    except OSError as e:
        logger.error("创建模板写入失败: %s - %s", filepath, e)
        return False
    except Exception as e:
        logger.error("创建模板未知错误: %s", e)
        return False


def import_from_excel(
    filepath: str, data_manager: Any
) -> Tuple[int, Optional[str]]:
    """从 Excel 文件导入学生成绩数据。"""
    if not EX_OK:
        msg = "请执行：pip install openpyxl"
        logger.error(msg)
        return (0, msg)

    try:
        filepath = _validate_filepath(filepath)
    except ExcelHandlerError as e:
        return (0, str(e))

    if not os.path.exists(filepath):
        msg = f"文件不存在: {filepath}"
        logger.error(msg)
        return (0, msg)

    try:
        # 读取 Excel 文件
        if filepath.lower().endswith(".xlsx"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(filepath, data_only=True, read_only=True)
                ws = wb.active
                if ws is None:
                    return (0, "无法读取工作表")
                rows = list(ws.iter_rows(values_only=True))
                wb.close()
                logger.info("读取 .xlsx 文件: %s (%d 行)", filepath, len(rows))
            except OSError as e:
                logger.error("读取 .xlsx 文件失败: %s - %s", filepath, e)
                return (0, f"无法读取文件: {e}")
            except Exception as e:
                logger.error("解析 .xlsx 文件失败: %s - %s", filepath, e)
                return (0, f"文件格式不正确: {e}")
        else:
            try:
                import xlrd
                rb = xlrd.open_workbook(filepath)
                sh = rb.sheet_by_index(0)
                rows = [
                    [str(c).strip() if c else "" for c in sh.row_values(i)]
                    for i in range(sh.nrows)
                ]
                logger.info("读取 .xls 文件: %s (%d 行)", filepath, len(rows))
            except OSError as e:
                logger.error("读取 .xls 文件失败: %s - %s", filepath, e)
                return (0, f"无法读取文件: {e}")
            except Exception as e:
                logger.error("解析 .xls 文件失败: %s - %s", filepath, e)
                return (0, f"文件格式不正确: {e}")

        if len(rows) < 2:
            logger.warning("Excel 文件内容为空: %s", filepath)
            return (0, "文件内容为空，至少需要表头和数据行")

        # 解析表头
        header = [str(h).strip() if h is not None else "" for h in rows[0]]
        if not any(header):
            return (0, "表头为空，无法识别列")

        id_idx = next((i for i, h in enumerate(header) if "学号" in str(h)), 0)
        name_idx = next((i for i, h in enumerate(header) if "姓名" in str(h)), 1)

        # ========== 明确跳过列：只跳过学号和姓名 ==========
        skip_idxs = {id_idx, name_idx}

        # 处理班级列
        if "班级" in header:
            class_idx = next((i for i, h in enumerate(header) if "班级" in str(h)), 2)
            skip_idxs.add(class_idx)
            default_class_name = None
        else:
            # 没有班级列，使用默认班级
            default_class_name = "24计软技师"
            logger.info("未找到班级列，所有学生将自动归入: %s", default_class_name)
        # ==============================================

        # 解析科目列
        subject_idx: dict[str, int] = {}
        for i, h in enumerate(header):
            # 只要不是 skip_idxs 里包含的列，且不是总分/总学分，就作为科目列
            if i not in skip_idxs and h and h not in ["总分", "总学分"]:
                if h not in data_manager.subjects:
                    try:
                        data_manager.add_subject(h)
                        logger.info("自动添加科目: %s", h)
                    except Exception as e:
                        logger.warning("自动添加科目失败: %s - %s", h, e)
                        continue
                subject_idx[h] = i

        if not subject_idx:
            logger.warning("未找到科目列: %s", filepath)
            return (0, "未找到科目列，请检查表头是否包含科目名称")

        # 导入数据
        imported = 0
        import_errors: list[str] = []
        for row_idx, row in enumerate(rows[1:], start=2):
            try:
                values = [c for c in row]
                if all(not str(c).strip() if c is not None else True for c in values):
                    continue

                student_id = str(values[id_idx]).strip() if id_idx < len(values) and values[id_idx] is not None else ""
                if not student_id:
                    continue

                name = str(values[name_idx]).strip() if name_idx < len(values) and values[name_idx] is not None else ""

                # ========== 获取班级名称 ==========
                if default_class_name is not None:
                    class_name = default_class_name
                else:
                    class_name = str(values[class_idx]).strip() if class_idx < len(values) and values[class_idx] is not None else ""
                # ===================================

                scores: dict[str, float] = {}
                for subject, idx in subject_idx.items():
                    value = str(values[idx]).strip() if idx < len(values) and values[idx] is not None else ""
                    if value and value != "None":
                        try:
                            parsed = float(value)
                            if 0 <= parsed <= 100:
                                scores[subject] = parsed
                            else:
                                logger.warning("第 %d 行 %s 成绩超出范围: %s", row_idx, subject, parsed)
                        except ValueError:
                            logger.warning("第 %d 行 %s 成绩无效: %s", row_idx, subject, value)

                try:
                    if data_manager.exists(student_id):
                        data_manager.update_student(student_id, name, class_name)
                    else:
                        data_manager.add_student(student_id, name, class_name)
                    data_manager.batch_set(student_id, scores)
                    imported += 1
                except Exception as e:
                    msg = f"第 {row_idx} 行导入失败: {e}"
                    import_errors.append(msg)
                    logger.warning(msg)

            except Exception as e:
                msg = f"第 {row_idx} 行解析失败: {e}"
                import_errors.append(msg)
                logger.warning(msg)

        if import_errors:
            logger.warning("导入完成，共 %d 条成功，%d 条失败", imported, len(import_errors))

        return (imported, None)

    except Exception as e:
        logger.error("导入 Excel 文件异常: %s - %s", filepath, e)
        return (0, f"导入失败: {e}")


def export_to_excel(filepath: str, data_manager: Any) -> bool:
    """导出成绩数据到 Excel 文件。

    包含排名、学号、姓名、班级、各科成绩、总分、平均分和等级。

    Args:
        filepath: 保存路径。
        data_manager: DataManager 实例。

    Returns:
        True 表示导出成功，False 表示失败。
    """
    if not EX_OK:
        logger.error("导出 Excel 失败: Excel 库未安装")
        return False

    try:
        filepath = _validate_filepath(filepath)
    except ExcelHandlerError as e:
        logger.error("导出 Excel 失败: %s", e)
        return False

    try:
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        if ws is None:
            logger.error("导出 Excel 失败: 无法获取活动工作表")
            return False
        ws.title = "成绩表"

        subjects = (
            list(data_manager.subjects)
            if hasattr(data_manager, "subjects")
            else []
        )
        ws.append(
            ["排名", "学号", "姓名", "班级"]
            + subjects
            + ["总分", "平均分", "等级"]
        )

        ranking = (
            data_manager.ranking()
            if hasattr(data_manager, "ranking")
            else []
        )
        for rank_data in ranking:
            avg = rank_data.get("avg", 0)
            if avg >= 90:
                level = "优秀"
            elif avg >= 75:
                level = "良好"
            elif avg >= 60:
                level = "及格"
            else:
                level = "不及格"

            row_data = (
                [rank_data.get("rank", ""), rank_data.get("id", ""),
                 rank_data.get("name", ""), rank_data.get("class", "")]
                + [
                    rank_data.get("scores", {}).get(s, "-")
                    for s in subjects
                ]
                + [rank_data.get("total", 0), rank_data.get("avg", 0), level]
            )
            ws.append(row_data)

        wb.save(filepath)
        logger.info("Excel 导出成功: %s", filepath)
        return True

    except OSError as e:
        logger.error("导出 Excel 写入失败: %s - %s", filepath, e)
        return False
    except Exception as e:
        logger.error("导出 Excel 未知错误: %s", e)
        return False


def get_default_filename(extension: str = "xlsx") -> str:
    """获取默认导出文件名（含日期）。

    Args:
        extension: 文件扩展名，默认 "xlsx"。

    Returns:
        格式为 "成绩_YYYY-MM-DD.{extension}" 的文件名。
    """
    ext = extension.lstrip(".")
    return f"成绩_{datetime.date.today()}.{ext}"