"""
数据导出模块 - Data Export Module.

提供 CSV 格式的数据导出功能，包括成绩数据和统计数据。

本模块独立于 Excel 处理库，仅依赖 Python 标准库中的 ``csv`` 模块，
确保在任意环境下都能完成基础的数据导出操作。

主要功能::

    - export_to_csv: 将学生成绩排名导出为 CSV 文件。
    - export_statistics: 将科目统计分析导出为 CSV 文件。
    - get_default_filename: 生成带日期的默认文件名。

"""

import csv
import datetime
import logging
from typing import Any

logger = logging.getLogger(__name__)


def export_to_csv(filepath: str, data_manager: Any) -> bool:
    """导出成绩数据到 CSV 文件.

    包含排名、学号、姓名、班级、各科成绩、总分、平均分。
    使用 ``utf-8-sig`` 编码，确保 Excel 打开时中文不会出现乱码。

    Args:
        filepath: 保存路径。
        data_manager: DataManager 实例，需提供 ``subjects`` 属性和 ``ranking()`` 方法。

    Returns:
        True 表示导出成功，False 表示失败。
    """
    try:
        # 使用 utf-8-sig 编码写入 BOM，使 Excel 默认以 UTF-8 打开
        with open(filepath, "w", newline="", encoding="utf-8-sig", errors="replace") as f:
            writer = csv.writer(f)

            subjects = data_manager.subjects
            header = ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
            writer.writerow(header)

            # 逐行写入每个学生的成绩与排名数据
            for rank_data in data_manager.ranking():
                row_data = (
                    [
                        rank_data["rank"],
                        rank_data["id"],
                        rank_data["name"],
                        rank_data.get("class", ""),
                    ]
                    + [rank_data["scores"].get(s, "-") for s in subjects]
                    + [rank_data["total"], rank_data["avg"]]
                )
                writer.writerow(row_data)

        return True

    except Exception as e:
        logger.warning("CSV导出失败: %s", e, exc_info=True)
        return False


def get_default_filename() -> str:
    """获取默认 CSV 导出文件名（含日期和时间）.

    Returns:
        格式为 "成绩_YYYY-MM-DD_HHMMSS.csv" 的文件名。
    """
    return f"成绩_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"


def export_statistics(filepath: str, data_manager: Any) -> bool:
    """导出科目统计数据到 CSV 文件.

    包含各科目的平均分、最高分、最低分、及格率等。
    文件内容分为"学生统计"和"科目统计"两大部分。

    Args:
        filepath: 保存路径。
        data_manager: DataManager 实例，需提供 ``subjects`` 属性和 ``analyze_subject()`` 方法。

    Returns:
        True 表示导出成功，False 表示失败。
    """
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig", errors="replace") as f:
            writer = csv.writer(f)

            # 总体统计
            writer.writerow(["学生统计"])
            writer.writerow(["总人数", len(data_manager.students)])
            writer.writerow([])  # 空行分隔

            # 科目统计
            writer.writerow(["科目统计"])
            writer.writerow(
                ["科目", "人数", "平均分", "最高分", "最低分", "及格率", "优秀率"]
            )

            # 遍历所有科目，获取分析数据并写入
            for subject in data_manager.subjects:
                analysis = data_manager.analyze_subject(subject)
                if analysis:
                    writer.writerow(
                        [
                            subject,
                            analysis.get("count", 0),
                            analysis.get("avg", 0),
                            analysis.get("max", 0),
                            analysis.get("min", 0),
                            f"{analysis.get('pass_rate', 0)}%",
                            f"{analysis.get('excellent_rate', 0)}%",
                        ]
                    )

        return True

    except Exception as e:
        logger.warning("统计数据CSV导出失败: %s", e, exc_info=True)
        return False
