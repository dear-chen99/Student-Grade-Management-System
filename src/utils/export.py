"""
数据导出模块 - Data Export Module.

提供 CSV 格式的数据导出功能，包括成绩数据和统计数据。
"""

import csv
import datetime
from typing import Any


def export_to_csv(filepath: str, data_manager: Any) -> bool:
    """导出成绩数据到 CSV 文件.

    包含排名、学号、姓名、班级、各科成绩、总分、平均分。

    Args:
        filepath: 保存路径。
        data_manager: DataManager 实例。

    Returns:
        True 表示导出成功，False 表示失败。
    """
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            subjects = data_manager.subjects
            header = ["排名", "学号", "姓名", "班级"] + subjects + ["总分", "平均分"]
            writer.writerow(header)

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

    except Exception:
        return False


def get_default_filename() -> str:
    """获取默认 CSV 导出文件名（含日期）.

    Returns:
        格式为 "成绩_YYYY-MM-DD.csv" 的文件名。
    """
    return f"成绩_{datetime.date.today()}.csv"


def export_statistics(filepath: str, data_manager: Any) -> bool:
    """导出科目统计数据到 CSV 文件.

    包含各科目的平均分、最高分、最低分、及格率等。

    Args:
        filepath: 保存路径。
        data_manager: DataManager 实例。

    Returns:
        True 表示导出成功，False 表示失败。
    """
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            # 总体统计
            writer.writerow(["学生统计"])
            writer.writerow(["总人数", len(data_manager.students)])
            writer.writerow([])

            # 科目统计
            writer.writerow(["科目统计"])
            writer.writerow(
                ["科目", "人数", "平均分", "最高分", "最低分", "及格率", "优秀率"]
            )

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

    except Exception:
        return False
