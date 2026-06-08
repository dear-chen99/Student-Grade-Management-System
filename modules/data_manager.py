#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块 - Student Grade Management System Data Manager

负责学生成绩数据的持久化存储、读取和管理操作。
支持 JSON 格式的数据存储，包含数据备份和恢复功能。
"""

import json
import logging
import os
import shutil
from typing import Any, Optional

# 配置模块级日志
logger = logging.getLogger("DataManager")
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

class DataManagerError(Exception):
    """数据管理模块基础异常类。"""

    def __init__(self, message: str = "数据管理错误") -> None:
        super().__init__(message)
        self.message = message


class DataIntegrityError(DataManagerError):
    """数据完整性错误，如 JSON 格式损坏、缺失必要字段。"""

    def __init__(self, message: str = "数据文件损坏，无法读取") -> None:
        super().__init__(message)


class DataLoadError(DataManagerError):
    """数据加载失败错误。"""

    def __init__(self, filepath: str, reason: str = "") -> None:
        msg = f"无法加载数据文件: {filepath}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class DataSaveError(DataManagerError):
    """数据保存失败错误。"""

    def __init__(self, filepath: str, reason: str = "") -> None:
        msg = f"无法保存数据文件: {filepath}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class StudentNotFoundError(DataManagerError):
    """学生不存在错误。"""

    def __init__(self, student_id: str) -> None:
        super().__init__(f"学生 '{student_id}' 不存在")


class DuplicateStudentError(DataManagerError):
    """学号重复错误。"""

    def __init__(self, student_id: str) -> None:
        super().__init__(f"学号 '{student_id}' 已存在")


class SubjectNotFoundError(DataManagerError):
    """科目不存在错误。"""

    def __init__(self, subject: str) -> None:
        super().__init__(f"科目 '{subject}' 不存在")


class DuplicateSubjectError(DataManagerError):
    """科目重复错误。"""

    def __init__(self, subject: str) -> None:
        super().__init__(f"科目 '{subject}' 已存在")


class InvalidScoreError(DataManagerError):
    """成绩无效错误。"""

    def __init__(self, score: Any, subject: str = "") -> None:
        suffix = f"（科目: {subject}）" if subject else ""
        super().__init__(f"成绩 {score} 不在有效范围 0-100 内{suffix}")


class InvalidInputError(DataManagerError):
    """输入无效错误。"""

    def __init__(self, field: str) -> None:
        super().__init__(f"{field}不能为空")


# ------------------------------------------------------------------
# DataManager 类
# ------------------------------------------------------------------

class DataManager:
    """数据管理器类。

    提供学生成绩数据的增删改查操作，支持数据持久化和备份。

    Attributes:
        fp: 数据文件路径。
        bak: 备份文件路径。
        data: 内存中的数据字典。
    """

    # 成绩范围常量
    SCORE_MIN: float = 0.0
    SCORE_MAX: float = 100.0

    # 学号最大长度
    STUDENT_ID_MAX_LEN: int = 32

    def __init__(self, file_path: Optional[str] = None) -> None:
        """初始化数据管理器。

        Args:
            file_path: 数据文件路径，默认使用 data/grades.json。

        Raises:
            DataLoadError: 数据文件加载失败时抛出。
        """
        if file_path is None:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            self.fp: str = os.path.join(base_dir, "data", "grades.json")
        else:
            self.fp = file_path

        self.bak: str = self.fp + ".bak"
        self.data: dict[str, Any] = {}
        self.load()

    # ------------------------------------------------------------------
    # 数据校验工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_student_id(student_id: str) -> str:
        """校验并规范化学号。

        Args:
            student_id: 学号字符串。

        Returns:
            规范化后的学号。

        Raises:
            InvalidInputError: 学号为空时抛出。
        """
        student_id = str(student_id).strip()
        if not student_id:
            raise InvalidInputError("学号")
        if len(student_id) > DataManager.STUDENT_ID_MAX_LEN:
            raise InvalidInputError(
                f"学号长度不能超过 {DataManager.STUDENT_ID_MAX_LEN} 个字符"
            )
        return student_id

    @staticmethod
    def _validate_score(score: Any, subject: str = "") -> float:
        """校验并转换成绩值。

        Args:
            score: 成绩值。
            subject: 科目名称（用于错误提示）。

        Returns:
            转换后的 float 成绩。

        Raises:
            InvalidScoreError: 成绩不在 0-100 范围时抛出。
            ValueError: 无法转换为数字时抛出。
        """
        score = float(score)
        if not (DataManager.SCORE_MIN <= score <= DataManager.SCORE_MAX):
            raise InvalidScoreError(score, subject)
        return score

    @staticmethod
    def _validate_subject_name(name: str) -> str:
        """校验并规范化科目名称。

        Args:
            name: 科目名称。

        Returns:
            规范化后的科目名称。

        Raises:
            InvalidInputError: 名称为空时抛出。
        """
        name = str(name).strip()
        if not name:
            raise InvalidInputError("科目名称")
        return name

    @staticmethod
    def _validate_class_name(name: str) -> str:
        """校验并规范化班级名称。

        Args:
            name: 班级名称。

        Returns:
            规范化后的班级名称。

        Raises:
            InvalidInputError: 名称为空时抛出。
        """
        name = str(name).strip()
        if not name:
            raise InvalidInputError("班级名称")
        return name

    def _validate_data_integrity(self) -> None:
        """校验数据完整性，自动修复可修复的损坏。

        校验内容：
        1. 顶层结构：data 为 dict，包含 subjects (list) 和 students (dict)。
        2. 每个学生：name 为非空字符串，scores 为字典。
        3. 损坏数据：自动补全缺失字段，无法修复时移除并记录日志。

        Raises:
            DataIntegrityError: 数据严重损坏无法修复时抛出。
        """
        if not isinstance(self.data, dict):
            raise DataIntegrityError("数据根元素不是字典")
        if "subjects" not in self.data:
            self.data["subjects"] = []
        if "students" not in self.data:
            self.data["students"] = {}
        if "history" not in self.data:
            self.data["history"] = []
        if not isinstance(self.data["subjects"], list):
            raise DataIntegrityError("subjects 字段不是列表")
        if not isinstance(self.data["students"], dict):
            raise DataIntegrityError("students 字段不是字典")
        if not isinstance(self.data["history"], list):
            logger.warning("history 字段不是列表，已自动修复")
            self.data["history"] = []

        repaired = 0
        for sid, stu in list(self.data["students"].items()):
            if not isinstance(stu, dict):
                logger.warning("学生 %s 数据损坏（非字典），已移除", sid)
                del self.data["students"][sid]
                repaired += 1
                continue
            if not isinstance(stu.get("name"), str) or not stu["name"].strip():
                logger.warning("学生 %s 姓名为空，已自动修复", sid)
                stu["name"] = str(sid)
                repaired += 1
            if "scores" not in stu or not isinstance(stu["scores"], dict):
                logger.warning("学生 %s 成绩数据缺失，已自动修复", sid)
                stu["scores"] = {}
                repaired += 1
            if "class" not in stu:
                stu["class"] = ""

        if repaired:
            logger.info("数据完整性校验: 修复了 %d 处问题", repaired)

    # ------------------------------------------------------------------
    # 数据持久化
    # ------------------------------------------------------------------

    def load(self) -> None:
        """从文件加载数据。

        按优先级加载：
        1. 尝试加载主数据文件
        2. 主文件加载失败时，尝试从备份文件恢复
        3. 都失败时创建新的空数据结构

        Raises:
            DataLoadError: 所有加载方式均失败时抛出。
        """
        if os.path.exists(self.fp):
            try:
                with open(self.fp, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                logger.info("数据文件加载成功: %s", self.fp)
            except PermissionError as e:
                logger.error("数据文件权限不足: %s - %s", self.fp, e)
                raise DataLoadError(self.fp, f"权限不足: {e}") from e
            except FileNotFoundError as e:
                logger.error("数据文件被删除: %s - %s", self.fp, e)
                raise DataLoadError(self.fp, f"文件被删除: {e}") from e
            except json.JSONDecodeError as e:
                logger.warning("数据文件 JSON 解析失败: %s", e)
                if os.path.exists(self.bak):
                    logger.info("尝试从备份文件恢复...")
                    try:
                        with open(self.bak, "r", encoding="utf-8") as f:
                            self.data = json.load(f)
                        self.save()
                        logger.info("备份文件恢复成功")
                    except (json.JSONDecodeError, OSError) as e2:
                        logger.error("备份文件也无法加载: %s", e2)
                        self.data = self._create_empty_data()
                else:
                    logger.warning("无备份文件，创建空数据")
                    self.data = self._create_empty_data()
            except OSError as e:
                logger.error("读取数据文件失败: %s", e)
                raise DataLoadError(self.fp, str(e)) from e
        else:
            try:
                os.makedirs(os.path.dirname(self.fp), exist_ok=True)
            except OSError as e:
                logger.error("创建数据目录失败: %s", e)
                raise DataLoadError(self.fp, str(e)) from e
            self.data = self._create_empty_data()
            logger.info("数据目录不存在，创建空数据结构")

        self._validate_data_integrity()

    def save(self) -> None:
        """保存数据到文件。

        采用安全写入策略：
        1. 先写入临时文件
        2. 备份原文件
        3. 替换原文件

        Raises:
            DataSaveError: 保存失败时抛出。
        """
        self._validate_data_integrity()
        tmp_file = self.fp + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

            if os.path.exists(self.fp):
                shutil.copy2(self.fp, self.bak)

            os.replace(tmp_file, self.fp)
            logger.debug("数据保存成功: %s", self.fp)
        except PermissionError as e:
            logger.error("数据保存权限不足: %s - %s", self.fp, e)
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except OSError:
                    pass
            raise DataSaveError(self.fp, f"权限不足: {e}") from e
        except FileNotFoundError as e:
            logger.error("数据保存路径不存在: %s - %s", self.fp, e)
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except OSError:
                    pass
            raise DataSaveError(self.fp, f"路径不存在: {e}") from e
        except OSError as e:
            logger.error("数据保存失败: %s", e)
            # 清理临时文件
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except OSError:
                    pass
            raise DataSaveError(self.fp, str(e)) from e

    def _create_empty_data(self) -> dict[str, Any]:
        """创建空的数据结构。

        Returns:
            包含 subjects、students 和 history 的字典。
        """
        return {"subjects": [], "students": {}, "history": []}
    
    @property
    def subjects(self) -> list[str]:
        """获取科目列表（只读副本）。

        Returns:
            科目名称列表。
        """
        return list(self.data["subjects"])

    @property
    def students(self) -> dict[str, dict[str, Any]]:
        """获取学生字典（只读引用，注意修改会影响原始数据）。

        Returns:
            学生信息字典，key 为学号。
        """
        return self.data["students"]

    # ------------------------------------------------------------------
    # 科目管理
    # ------------------------------------------------------------------

    def add_sub(self, name: str) -> None:
        """添加科目（兼容旧接口）。

        Args:
            name: 科目名称。

        Raises:
            DuplicateSubjectError: 科目已存在时抛出。
            InvalidInputError: 科目名称为空时抛出。
        """
        return self.add_subject(name)

    def add_subject(self, name: str) -> None:
        """添加科目。

        Args:
            name: 科目名称。

        Raises:
            DuplicateSubjectError: 科目已存在时抛出。
            InvalidInputError: 科目名称为空时抛出。
        """
        name = self._validate_subject_name(name)
        if name in self.data["subjects"]:
            raise DuplicateSubjectError(name)
        self.data["subjects"].append(name)
        self.save()
        logger.info("科目已添加: %s", name)

    def del_sub(self, name: str) -> None:
        """删除科目（兼容旧接口）。

        Args:
            name: 科目名称。
        """
        return self.delete_subject(name)

    def delete_subject(self, name: str) -> None:
        """删除科目。

        删除科目时会同时删除所有学生该科目的成绩。

        Args:
            name: 科目名称。

        Raises:
            SubjectNotFoundError: 科目不存在时抛出。
        """
        name = name.strip()
        if name not in self.data["subjects"]:
            raise SubjectNotFoundError(name)
        self.data["subjects"].remove(name)
        for student in self.data["students"].values():
            student["scores"].pop(name, None)
        self.save()
        logger.info("科目已删除: %s", name)

    # ------------------------------------------------------------------
    # 学生管理
    # ------------------------------------------------------------------

    def add_stu(
        self, student_id: str, name: str, class_name: str = ""
    ) -> None:
        """添加学生（兼容旧接口）。

        Args:
            student_id: 学号。
            name: 学生姓名。
            class_name: 班级名称。

        Raises:
            DuplicateStudentError: 学号已存在时抛出。
            InvalidInputError: 学号为空时抛出。
        """
        return self.add_student(student_id, name, class_name)

    def add_student(
        self, student_id: str, name: str, class_name: str = ""
    ) -> None:
        """添加学生。

        Args:
            student_id: 学号。
            name: 学生姓名。
            class_name: 班级名称。

        Raises:
            DuplicateStudentError: 学号已存在时抛出。
            InvalidInputError: 学号为空时抛出。
        """
        student_id = self._validate_student_id(student_id)
        if student_id in self.data["students"]:
            raise DuplicateStudentError(student_id)
        name = str(name).strip()
        class_name = str(class_name).strip() if class_name else ""

        self.data["students"][student_id] = {
            "name": name,
            "class": class_name,
            "scores": {},
        }
        self.save()
        logger.info("学生已添加: %s (%s, %s)", student_id, name, class_name)

    def upd_stu(
        self, student_id: str, name: str, class_name: str = ""
    ) -> None:
        """更新学生信息（兼容旧接口）。

        Args:
            student_id: 学号。
            name: 学生姓名。
            class_name: 班级名称。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        return self.update_student(student_id, name, class_name)

    def update_student(
        self, student_id: str, name: str, class_name: str = ""
    ) -> None:
        """更新学生信息。

        Args:
            student_id: 学号。
            name: 学生姓名。
            class_name: 班级名称。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        student_id = self._validate_student_id(student_id)
        if student_id not in self.data["students"]:
            raise StudentNotFoundError(student_id)
        self.data["students"][student_id]["name"] = str(name).strip()
        self.data["students"][student_id]["class"] = (
            str(class_name).strip() if class_name else ""
        )
        self.save()
        logger.info("学生信息已更新: %s", student_id)

    def del_stu(self, student_id: str) -> None:
        """删除学生（兼容旧接口）。

        Args:
            student_id: 学号。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        return self.delete_student(student_id)

    def delete_student(self, student_id: str) -> None:
        """删除学生。

        Args:
            student_id: 学号。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        student_id = str(student_id).strip()
        if student_id not in self.data["students"]:
            raise StudentNotFoundError(student_id)
        del self.data["students"][student_id]
        self.save()
        logger.info("学生已删除: %s", student_id)

    def get_stu(self, student_id: str) -> Optional[dict[str, Any]]:
        """获取学生信息（兼容旧接口）。

        Args:
            student_id: 学号。

        Returns:
            学生信息字典，不存在时返回 None。
        """
        return self.get_student(student_id)

    def get_student(self, student_id: str) -> Optional[dict[str, Any]]:
        """获取学生信息。

        Args:
            student_id: 学号。

        Returns:
            学生信息字典，包含姓名、班级和成绩；不存在时返回 None。
        """
        return self.data["students"].get(str(student_id).strip())

    def exists(self, student_id: str) -> bool:
        """检查学生是否存在。

        Args:
            student_id: 学号。

        Returns:
            True 表示学生存在。
        """
        return str(student_id).strip() in self.data["students"]

    # ------------------------------------------------------------------
    # 成绩管理
    # ------------------------------------------------------------------

    def _add_history(
        self,
        student_id: str,
        subject: str,
        old: Any,
        new: Any,
        operator: str = "system",
    ) -> None:
        """添加一条成绩修改历史记录。

        Args:
            student_id: 学号。
            subject: 科目名称。
            old: 修改前的成绩。
            new: 修改后的成绩。
            operator: 操作者标识。
        """
        import datetime
        record = {
            "sid": str(student_id),
            "subject": str(subject),
            "old": old,
            "new": new,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "operator": operator,
        }
        self.data["history"].append(record)

    def get_history(
        self,
        student_id: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """获取成绩修改历史记录。

        Args:
            student_id: 按学号过滤，可选。
            subject: 按科目过滤，可选。

        Returns:
            符合条件的历史记录列表，按时间倒序排列。
        """
        history = self.data.get("history", [])
        result = list(history)
        if student_id is not None:
            sid = str(student_id).strip()
            result = [r for r in result if r.get("sid") == sid]
        if subject is not None:
            subj = str(subject).strip()
            result = [r for r in result if r.get("subject") == subj]
        return list(reversed(result))

    def set_score(
        self, student_id: str, subject: str, score: Any
    ) -> None:
        """设置学生成绩。

        Args:
            student_id: 学号。
            subject: 科目名称。
            score: 成绩值（None 表示清除成绩）。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
            InvalidScoreError: 成绩不在 0-100 范围时抛出。
            InvalidInputError: 学号为空时抛出。
        """
        student_id = self._validate_student_id(student_id)
        if student_id not in self.data["students"]:
            raise StudentNotFoundError(student_id)

        old_score = self.data["students"][student_id]["scores"].get(subject)

        if score is not None:
            score = self._validate_score(score, subject)

        # 成绩发生变化时记录历史
        if old_score != score:
            self._add_history(student_id, subject, old_score, score)

        self.data["students"][student_id]["scores"][subject] = score
        self.save()
        logger.debug("成绩已设置: %s - %s = %s", student_id, subject, score)

    def batch_set(
        self, student_id: str, scores_dict: dict[str, Any]
    ) -> None:
        """批量设置学生成绩。

        自动跳过无效成绩值（None、空字符串、无法转换的值）。

        Args:
            student_id: 学号。
            scores_dict: 成绩字典，key 为科目名，value 为成绩。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        student_id = str(student_id).strip()
        if student_id not in self.data["students"]:
            raise StudentNotFoundError(student_id)

        student = self.data["students"][student_id]
        for subject, score in scores_dict.items():
            if score is None or score == "":
                continue
            try:
                validated = self._validate_score(score, subject)
                old_score = student["scores"].get(subject)
                if old_score != validated:
                    self._add_history(student_id, subject, old_score, validated)
                student["scores"][subject] = validated
            except (InvalidScoreError, ValueError, TypeError) as e:
                logger.warning(
                    "批量设置成绩跳过无效值: %s - %s = %s (%s)",
                    student_id, subject, score, e,
                )
        self.save()

    # ------------------------------------------------------------------
    # 统计分析
    # ------------------------------------------------------------------

    def stats(self, student_id: str) -> Optional[dict[str, Any]]:
        """获取学生统计信息。

        Args:
            student_id: 学号。

        Returns:
            包含学号、姓名、班级、成绩、总分、平均分的字典；
            学生不存在或无成绩时返回 None。
        """
        student = self.get_student(student_id)
        if not student:
            return None

        scores = [
            v for v in student["scores"].values()
            if v is not None
        ]
        total = round(sum(scores), 2) if scores else 0.0
        avg = round(total / len(scores), 2) if scores else 0.0

        return {
            "id": student_id,
            "name": student["name"],
            "class": student.get("class", ""),
            "scores": dict(student["scores"]),
            "total": total,
            "avg": avg,
        }

    def ranking(
        self,
        by: str = "total",
        subject: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """获取学生排名。

        Args:
            by: 排序依据，可选 "total"(总分) / "avg"(平均分) / "subject"(科目)。
            subject: 当 by="subject" 时指定科目名称。

        Returns:
            排序后的学生列表，包含排名信息。无数据时返回空列表。
        """
        result: list[dict[str, Any]] = []
        for sid in self.data["students"]:
            student_stats = self.stats(sid)
            if student_stats is None:
                continue
            if by == "subject" and subject:
                sort_key = student_stats["scores"].get(subject, 0) or 0
            elif by == "avg":
                sort_key = student_stats["avg"]
            else:
                sort_key = student_stats["total"]
            result.append({**student_stats, "sort_key": sort_key})

        result.sort(key=lambda x: x["sort_key"], reverse=True)
        for i, item in enumerate(result, 1):
            item["rank"] = i

        return result

    def ana_sub(self, subject: str) -> Optional[dict[str, Any]]:
        """分析科目成绩统计（兼容旧接口）。

        Args:
            subject: 科目名称。

        Returns:
            包含统计数据和分析结果的字典，无数据时返回 None。
        """
        return self.analyze_subject(subject)

    def analyze_subject(self, subject: str) -> Optional[dict[str, Any]]:
        """分析科目成绩统计。

        Args:
            subject: 科目名称。

        Returns:
            包含平均分、最高分、最低分、及格率、分布等统计数据的字典；
            无有效成绩时返回 None。
        """
        subject = subject.strip() if subject else ""
        if not subject:
            return None

        scores: list[float] = []
        for student in self.data["students"].values():
            score = student["scores"].get(subject)
            if score is not None:
                try:
                    scores.append(float(score))
                except (ValueError, TypeError):
                    logger.warning(
                        "科目分析跳过无效成绩: %s = %s", subject, score
                    )

        if not scores:
            return None

        n = len(scores)
        distribution = {
            "0-59": sum(1 for s in scores if s < 60),
            "60-69": sum(1 for s in scores if 60 <= s < 70),
            "70-79": sum(1 for s in scores if 70 <= s < 80),
            "80-89": sum(1 for s in scores if 80 <= s < 90),
            "90-100": sum(1 for s in scores if s >= 90),
        }

        return {
            "subject": subject,
            "count": n,
            "max": round(max(scores), 2),
            "min": round(min(scores), 2),
            "avg": round(sum(scores) / n, 2),
            "pass_rate": round(
                sum(1 for s in scores if s >= 60) / n * 100, 1
            ),
            "excellent_rate": round(
                sum(1 for s in scores if s >= 90) / n * 100, 1
            ),
            "distribution": distribution,
            "scores": [round(s, 2) for s in scores],
        }

    def search(self, keyword: str) -> list[str]:
        """搜索学生。

        支持按学号、姓名、班级进行模糊匹配。

        Args:
            keyword: 搜索关键词。

        Returns:
            匹配的学生学号列表。关键词为空时返回空列表。
        """
        keyword = keyword.strip().lower()
        if not keyword:
            return []
        return [
            sid
            for sid, stu in self.data["students"].items()
            if (
                keyword in sid.lower()
                or keyword in stu["name"].lower()
                or keyword in stu.get("class", "").lower()
            )
        ]

    # ------------------------------------------------------------------
    # 班级管理
    # ------------------------------------------------------------------

    @property
    def classes(self) -> list[str]:
        """获取所有班级列表（排序后）。

        Returns:
            班级名称列表。
        """
        class_set: set[str] = set()
        for student in self.data["students"].values():
            cls = student.get("class", "")
            if cls:
                class_set.add(cls)
        return sorted(class_set)

    def add_class(self, class_name: str) -> str:
        """添加班级（兼容旧接口）。

        Args:
            class_name: 班级名称。

        Returns:
            规范化后的班级名称。

        Raises:
            InvalidInputError: 班级名称为空时抛出。
            DuplicateStudentError: 班级已存在时抛出。
        """
        class_name = self._validate_class_name(class_name)

        for student in self.data["students"].values():
            if student.get("class") == class_name:
                raise DuplicateStudentError(
                    f"班级 '{class_name}' 已存在"
                )

        return class_name

    def get_class_stats(
        self, class_name: str
    ) -> Optional[dict[str, Any]]:
        """获取班级统计信息。

        Args:
            class_name: 班级名称。

        Returns:
            班级统计信息字典，班级不存在或无学生时返回 None。
        """
        class_name = class_name.strip()
        if not class_name:
            return None

        students = [
            (sid, s)
            for sid, s in self.data["students"].items()
            if s.get("class") == class_name
        ]

        if not students:
            return None

        totals: list[dict[str, Any]] = []
        for sid, student in students:
            scores = [
                v for v in student["scores"].values() if v is not None
            ]
            total = round(sum(scores), 2) if scores else 0.0
            avg = round(total / len(scores), 2) if scores else 0.0
            totals.append(
                {"sid": sid, "name": student["name"], "total": total, "avg": avg}
            )

        totals.sort(key=lambda x: x["total"], reverse=True)
        for i, t in enumerate(totals, 1):
            t["rank"] = i

        overall = [t["total"] for t in totals]

        return {
            "class": class_name,
            "count": len(students),
            "total_avg": (
                round(sum(overall) / len(overall), 2) if overall else 0.0
            ),
            "students": totals,
            "max_total": max(overall) if overall else 0.0,
            "min_total": min(overall) if overall else 0.0,
        }

    def get_warnings(self) -> list[dict[str, Any]]:
        """获取成绩预警学生列表。

        Returns:
            包含不及格学生信息和不及格科目的列表。
        """
        warnings: list[dict[str, Any]] = []
        for sid, student in self.data["students"].items():
            fails: list[tuple[str, float]] = []
            for subj, score in student["scores"].items():
                if score is not None and score < 60:
                    fails.append((subj, score))

            if fails:
                total_scores = [
                    v
                    for v in student["scores"].values()
                    if v is not None
                ]
                avg = (
                    round(sum(total_scores) / len(total_scores), 2)
                    if total_scores
                    else 0.0
                )
                warnings.append(
                    {
                        "sid": sid,
                        "name": student["name"],
                        "class": student.get("class", ""),
                        "fails": fails,
                        "avg": avg,
                    }
                )

        return warnings


# ------------------------------------------------------------------
# 模块测试
# ------------------------------------------------------------------
if __name__ == "__main__":
    dm = DataManager()
    print("科目列表:", dm.subjects)
    print("学生数量:", len(dm.students))
    print("班级列表:", dm.classes)

    if dm.subjects:
        print(f"\n{dm.subjects[0]} 科目分析:")
        analysis = dm.analyze_subject(dm.subjects[0])
        if analysis:
            print(f"  均分: {analysis['avg']}, 及格率: {analysis['pass_rate']}%")

    warnings = dm.get_warnings()
    print(f"\n预警学生数量: {len(warnings)}")