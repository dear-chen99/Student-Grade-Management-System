"""
数据管理模块 - Student Grade Management System Data Manager.

负责学生成绩数据的持久化存储、读取和管理操作。
支持 JSON 格式的数据存储，包含数据备份和恢复功能。

本模块是系统的核心数据层，提供对以下实体和功能的完整管理：

**学生管理**：增删改查学生信息（姓名、班级、联系方式、头像等）。
**科目管理**：维护科目列表，支持动态增删。
**成绩管理**：单条/批量设置成绩，自动记录修改历史。
**教师管理**：教师账号的增删改查及课程分配。
**课程管理**：课程信息维护及任课教师关联。
**班级管理**：班级列表提取与班级级统计分析。
**考勤管理**：按日期、课程记录学生出勤状态（出勤/缺勤/迟到/请假）。
**公告管理**：发布公告并支持按角色筛选查看。
**课表管理**：课程表条目增删改及变更历史记录。
**统计分析**：学生排名、科目成绩分布、班级统计、成绩预警等。
**数据完整性**：加载时自动校验并修复缺失或损坏的数据字段。

数据以 JSON 格式持久化到磁盘，采用"临时文件 + 备份 + 原子替换"的安全写入策略，
最大限度避免写入过程中断导致的数据丢失。

Attributes:
    logger: 模块级日志记录器，用于记录数据操作和异常信息。
"""

import copy
import datetime
import json
import logging
import os
import shutil
import uuid
from typing import Any, Optional

# ------------------------------------------------------------------
# 模块级日志配置
# ------------------------------------------------------------------
# 配置独立的日志记录器，便于在数据操作过程中追踪异常和审计信息。
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
# 定义数据管理相关的异常体系，便于上层界面捕获并给出友好提示。


class DataManagerError(Exception):
    """数据管理模块基础异常类.

    所有本模块自定义异常的基类。

    Attributes:
        message: 错误描述信息。
    """

    def __init__(self, message: str = "数据管理错误") -> None:
        """初始化异常实例.

        Args:
            message: 错误描述信息。
        """
        super().__init__(message)
        self.message = message


class DataIntegrityError(DataManagerError):
    """数据完整性错误，如 JSON 格式损坏、缺失必要字段.

    当数据文件严重损坏且无法通过自动修复恢复时抛出。
    """

    def __init__(self, message: str = "数据文件损坏，无法读取") -> None:
        """初始化数据完整性错误.

        Args:
            message: 错误描述信息。
        """
        super().__init__(message)


class DataLoadError(DataManagerError):
    """数据加载失败错误.

    在尝试读取主数据文件和备份文件均失败时抛出。

    Attributes:
        message: 包含文件路径的错误描述。
    """

    def __init__(self, filepath: str, reason: str = "") -> None:
        """初始化数据加载错误，记录文件路径和原因.

        Args:
            filepath: 发生错误的文件路径。
            reason: 失败原因补充说明。
        """
        msg = f"无法加载数据文件: {filepath}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class DataSaveError(DataManagerError):
    """数据保存失败错误.

    在写入临时文件、备份原文件或原子替换过程中发生异常时抛出。
    """

    def __init__(self, filepath: str, reason: str = "") -> None:
        """初始化数据保存错误，记录文件路径和原因.

        Args:
            filepath: 发生错误的文件路径。
            reason: 失败原因补充说明。
        """
        msg = f"无法保存数据文件: {filepath}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class StudentNotFoundError(DataManagerError):
    """学生不存在错误.

    在尝试访问、修改或删除不存在的学生时抛出。
    """

    def __init__(self, student_id: str) -> None:
        """初始化学生不存在错误.

        Args:
            student_id: 不存在的学号。
        """
        super().__init__(f"学生 '{student_id}' 不存在")


class DuplicateStudentError(DataManagerError):
    """学号或标识重复错误.

    在添加学生或班级时，如果标识已存在则抛出。
    """

    def __init__(self, identifier: str, label: str = "学号") -> None:
        """初始化重复错误.

        Args:
            identifier: 已存在的标识（学号、班级名等）。
            label: 标识类型名称，默认为"学号"。
        """
        super().__init__(f"{label} '{identifier}' 已存在")


class SubjectNotFoundError(DataManagerError):
    """科目不存在错误.

    在尝试删除不存在的科目时抛出。
    """

    def __init__(self, subject: str) -> None:
        """初始化科目不存在错误.

        Args:
            subject: 不存在的科目名称。
        """
        super().__init__(f"科目 '{subject}' 不存在")


class DuplicateSubjectError(DataManagerError):
    """科目重复错误.

    在添加已存在的科目时抛出。
    """

    def __init__(self, subject: str) -> None:
        """初始化科目重复错误.

        Args:
            subject: 已存在的科目名称。
        """
        super().__init__(f"科目 '{subject}' 已存在")


class InvalidScoreError(DataManagerError):
    """成绩无效错误.

    在设置超出 0-100 范围的成绩时抛出。
    """

    def __init__(self, score: Any, subject: str = "") -> None:
        """初始化成绩无效错误，记录分数和科目.

        Args:
            score: 无效的成绩值。
            subject: 相关科目名称（可选）。
        """
        suffix = f"（科目: {subject}）" if subject else ""
        super().__init__(f"成绩 {score} 不在有效范围 0-100 内{suffix}")


class InvalidInputError(DataManagerError):
    """输入无效错误.

    在必填字段为空或超出长度限制时抛出。
    """

    def __init__(self, field: str) -> None:
        """初始化输入无效错误，记录字段名.

        Args:
            field: 验证失败的字段名称。
        """
        super().__init__(f"{field}不能为空")


class TeacherNotFoundError(DataManagerError):
    """教师不存在错误.

    在尝试访问、修改或删除不存在的教师时抛出。
    """

    def __init__(self, teacher_id: str) -> None:
        """初始化教师不存在错误.

        Args:
            teacher_id: 不存在的教师工号。
        """
        super().__init__(f"教师 '{teacher_id}' 不存在")


class DuplicateTeacherError(DataManagerError):
    """教师工号重复错误.

    在添加已存在的教师工号时抛出。
    """

    def __init__(self, teacher_id: str) -> None:
        """初始化教师工号重复错误.

        Args:
            teacher_id: 已存在的教师工号。
        """
        super().__init__(f"教师工号 '{teacher_id}' 已存在")


class CourseNotFoundError(DataManagerError):
    """课程不存在错误.

    在尝试访问、修改或删除不存在的课程时抛出。
    """

    def __init__(self, course_id: str) -> None:
        """初始化课程不存在错误.

        Args:
            course_id: 不存在的课程编号。
        """
        super().__init__(f"课程 '{course_id}' 不存在")


class DuplicateCourseError(DataManagerError):
    """课程重复错误.

    在添加已存在的课程编号时抛出。
    """

    def __init__(self, course_id: str) -> None:
        """初始化课程重复错误.

        Args:
            course_id: 已存在的课程编号。
        """
        super().__init__(f"课程 '{course_id}' 已存在")


# ------------------------------------------------------------------
# DataManager 类
# ------------------------------------------------------------------


class DataManager:
    """数据管理器类.

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
        """初始化数据管理器.

        Args:
            file_path: 数据文件路径，默认使用 data/grades.json。

        Raises:
            DataLoadError: 数据文件加载失败时抛出。
        """
        if file_path is None:
            import sys

            # PyInstaller 打包后，数据文件放在 exe 同级目录（持久化保存）
            if hasattr(sys, "_MEIPASS"):
                base_dir = os.path.dirname(sys.executable)
                # 首次运行：从临时解压目录拷贝默认数据到 exe 目录
                data_dir = os.path.join(base_dir, "data")
                if not os.path.exists(data_dir):
                    src_data = os.path.join(sys._MEIPASS, "data")
                    if os.path.exists(src_data):
                        try:
                            shutil.copytree(src_data, data_dir)
                        except OSError:
                            pass
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        """校验并规范化学号.

        将旧格式 001-999 自动转换为 2024001-2024999.

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
        # 旧格式 1-3 位纯数字 → 2024xxxx
        if student_id.isdigit() and 1 <= len(student_id) <= 3:
            student_id = f"2024{student_id.zfill(3)}"
        if len(student_id) > DataManager.STUDENT_ID_MAX_LEN:
            raise InvalidInputError(
                f"学号长度不能超过 {DataManager.STUDENT_ID_MAX_LEN} 个字符"
            )
        return student_id

    def _migrate_student_ids(self) -> None:
        """将旧格式学号（如 001）迁移为新格式（2024001）.

        迁移范围包括 students 字典键、attendance 记录、
        history 日志中的 sid 字段，以及默认密码。

        Args:
            无（仅操作实例内部数据）。

        Returns:
            None
        """
        import re

        pattern = re.compile(r"^\d{1,3}$")
        mapping = {}
        for sid in list(self.data["students"].keys()):
            if pattern.match(sid):
                new_sid = f"2024{sid.zfill(3)}"
                mapping[sid] = new_sid

        if not mapping:
            return

        for old_sid, new_sid in mapping.items():
            self.data["students"][new_sid] = self.data["students"].pop(old_sid)
            stu = self.data["students"][new_sid]
            if stu.get("password") == old_sid:
                stu["password"] = new_sid

        for date in self.data.get("attendance", {}):
            for cid in list(self.data["attendance"][date].keys()):
                records = self.data["attendance"][date][cid]
                if not isinstance(records, dict):
                    continue
                for old_sid, new_sid in mapping.items():
                    if old_sid in records:
                        records[new_sid] = records.pop(old_sid)

        for record in self.data.get("history", []):
            sid = record.get("sid", "")
            if sid in mapping:
                record["sid"] = mapping[sid]

        logger.info("已迁移 %d 条旧格式学号", len(mapping))

    @staticmethod
    def _validate_score(score: Any, subject: str = "") -> float:
        """校验并转换成绩值.

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
        """校验并规范化科目名称.

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
        """校验并规范化班级名称.

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
        """校验数据完整性，自动修复可修复的损坏.

        校验内容：
        1. 顶层结构：data 为 dict，包含 subjects (list) 和 students (dict)。
        2. 每个学生：name 为非空字符串，scores 为字典。
        3. 损坏数据：自动补全缺失字段，无法修复时移除并记录日志。

        Args:
            无（仅操作实例内部数据）。

        Returns:
            None

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
        if "teachers" not in self.data:
            self.data["teachers"] = {}
        if "courses" not in self.data:
            self.data["courses"] = {}
        if "attendance" not in self.data:
            self.data["attendance"] = {}
        if not isinstance(self.data["subjects"], list):
            raise DataIntegrityError("subjects 字段不是列表")
        if not isinstance(self.data["students"], dict):
            raise DataIntegrityError("students 字段不是字典")
        if not isinstance(self.data["history"], list):
            logger.warning("history 字段不是列表，已自动修复")
            self.data["history"] = []
        if not isinstance(self.data["teachers"], dict):
            logger.warning("teachers 字段不是字典，已自动修复")
            self.data["teachers"] = {}
        if not isinstance(self.data["courses"], dict):
            logger.warning("courses 字段不是字典，已自动修复")
            self.data["courses"] = {}
        if not isinstance(self.data["attendance"], dict):
            logger.warning("attendance 字段不是字典，已自动修复")
            self.data["attendance"] = {}
        if "notices" not in self.data:
            self.data["notices"] = []
        if not isinstance(self.data["notices"], list):
            logger.warning("notices 字段不是列表，已自动修复")
            self.data["notices"] = []
        if "schedules" not in self.data:
            self.data["schedules"] = []
        if not isinstance(self.data["schedules"], list):
            logger.warning("schedules 字段不是列表，已自动修复")
            self.data["schedules"] = []
        if "schedule_history" not in self.data:
            self.data["schedule_history"] = []
        if not isinstance(self.data["schedule_history"], list):
            logger.warning("schedule_history 字段不是列表，已自动修复")
            self.data["schedule_history"] = []
        if "classes" not in self.data:
            self.data["classes"] = []
        if not isinstance(self.data["classes"], list):
            logger.warning("classes 字段不是列表，已自动修复")
            self.data["classes"] = []

        self._migrate_student_ids()

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
            for field in ("phone", "email", "gender", "birth", "avatar"):
                if field not in stu:
                    stu[field] = ""

        for tid, tea in list(self.data.get("teachers", {}).items()):
            if not isinstance(tea, dict):
                continue
            for field in ("phone", "email", "gender", "birth", "avatar"):
                if field not in tea:
                    tea[field] = ""

        admin = self.data.get("admin")
        if not isinstance(admin, dict):
            self.data["admin"] = {
                "username": "admin",
                "password": "123456",
                "avatar": "",
                "name": "管理员",
                "phone": "",
                "email": "",
                "gender": "",
                "birth": "",
            }
        else:
            for field, default in (
                ("username", "admin"),
                ("password", "123456"),
                ("avatar", ""),
                ("name", "管理员"),
                ("phone", ""),
                ("email", ""),
                ("gender", ""),
                ("birth", ""),
            ):
                if field not in admin:
                    admin[field] = default

        if repaired:
            logger.info("数据完整性校验: 修复了 %d 处问题", repaired)

    # ------------------------------------------------------------------
    # 数据持久化
    # ------------------------------------------------------------------

    def load(self) -> None:
        """从文件加载数据.

        按优先级加载：
        1. 尝试加载主数据文件
        2. 主文件加载失败时，尝试从备份文件恢复
        3. 都失败时创建新的空数据结构

        Args:
            无（仅操作实例内部数据）。

        Returns:
            None

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
        """保存数据到文件.

        采用安全写入策略：
        1. 先写入临时文件
        2. 备份原文件
        3. 替换原文件

        Args:
            无（仅操作实例内部数据）。

        Returns:
            None

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
        """创建空的数据结构.

        Returns:
            包含 subjects、students、history、teachers 和 courses 的字典。
        """
        return {
            "subjects": [],
            "students": {},
            "history": [],
            "teachers": {},
            "courses": {},
            "attendance": {},
            "classes": [],
            "notices": [],
            "schedules": [],
            "schedule_history": [],
            "admin": {
                "username": "admin",
                "password": "123456",
                "avatar": "",
                "name": "管理员",
                "phone": "",
                "email": "",
                "gender": "",
                "birth": "",
            },
        }

    @property
    def subjects(self) -> list[str]:
        """获取科目列表（只读副本）.

        Returns:
            科目名称列表。
        """
        return list(self.data["subjects"])

    @property
    def students(self) -> dict[str, dict[str, Any]]:
        """获取学生字典（深拷贝副本）.

        Returns:
            学生信息字典的深拷贝，修改不会影响原始数据。
        """
        return copy.deepcopy(self.data["students"])

    # ------------------------------------------------------------------
    # 科目管理
    # ------------------------------------------------------------------

    def add_sub(self, name: str) -> None:
        """添加科目（兼容旧接口）.

        Args:
            name: 科目名称。

        Returns:
            None

        Raises:
            DuplicateSubjectError: 科目已存在时抛出。
            InvalidInputError: 科目名称为空时抛出。
        """
        return self.add_subject(name)

    def add_subject(self, name: str) -> None:
        """添加科目.

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
        """删除科目（兼容旧接口）.

        Args:
            name: 科目名称。

        Returns:
            None
        """
        return self.delete_subject(name)

    def delete_subject(self, name: str) -> None:
        """删除科目.

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

    def add_stu(self, student_id: str, name: str, class_name: str = "") -> None:
        """添加学生（兼容旧接口）.

        Args:
            student_id: 学号。
            name: 学生姓名。
            class_name: 班级名称。

        Returns:
            None

        Raises:
            DuplicateStudentError: 学号已存在时抛出。
            InvalidInputError: 学号为空时抛出。
        """
        return self.add_student(student_id, name, class_name)

    def add_student(self, student_id: str, name: str, class_name: str = "") -> None:
        """添加学生.

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
            "password": student_id,
            "phone": "",
            "email": "",
            "gender": "",
            "birth": "",
            "avatar": "",
        }
        self.save()
        logger.info("学生已添加: %s (%s, %s)", student_id, name, class_name)

    def upd_stu(self, student_id: str, name: str, class_name: str = "") -> None:
        """更新学生信息（兼容旧接口）.

        Args:
            student_id: 学号。
            name: 学生姓名。
            class_name: 班级名称。

        Returns:
            None

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        return self.update_student(student_id, name, class_name)

    def update_student(
        self,
        student_id: str,
        name: str = "",
        class_name: str = "",
        phone: str = "",
        email: str = "",
        gender: str = "",
        birth: str = "",
        avatar: str = "",
        password: str = "",
    ) -> None:
        """更新学生信息.

        Args:
            student_id: 学号。
            name: 学生姓名，为空时不修改。
            class_name: 班级名称，为空时不修改。
            phone: 手机号，为空时不修改。
            email: 邮箱，为空时不修改。
            gender: 性别，为空时不修改。
            birth: 生日，为空时不修改。
            avatar: 头像路径，为空时不修改。
            password: 密码，为空时不修改。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        student_id = self._validate_student_id(student_id)
        if student_id not in self.data["students"]:
            raise StudentNotFoundError(student_id)
        student = self.data["students"][student_id]
        if name:
            student["name"] = str(name).strip()
        if class_name:
            student["class"] = str(class_name).strip()
        if phone is not None:
            student["phone"] = str(phone).strip()
        if email is not None:
            student["email"] = str(email).strip()
        if gender:
            student["gender"] = str(gender).strip()
        if birth is not None:
            student["birth"] = str(birth).strip()
        if avatar:
            student["avatar"] = str(avatar).strip()
        if password:
            student["password"] = str(password).strip()
        self.save()
        logger.info("学生信息已更新: %s", student_id)

    def del_stu(self, student_id: str) -> None:
        """删除学生（兼容旧接口）.

        Args:
            student_id: 学号。

        Returns:
            None

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
        """
        return self.delete_student(student_id)

    def delete_student(self, student_id: str) -> None:
        """删除学生.

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
        """获取学生信息（兼容旧接口）.

        Args:
            student_id: 学号。

        Returns:
            学生信息字典，不存在时返回 None。
        """
        return self.get_student(student_id)

    def get_student(self, student_id: str) -> Optional[dict[str, Any]]:
        """获取学生信息.

        Args:
            student_id: 学号。

        Returns:
            学生信息字典，包含姓名、班级和成绩；不存在时返回 None。
        """
        return self.data["students"].get(str(student_id).strip())

    def get_students_by_class(
        self, class_name: str
    ) -> list[tuple[str, dict[str, Any]]]:
        """获取指定班级的所有学生.

        Args:
            class_name: 班级名称。

        Returns:
            学生元组列表，每个元组为 (学号, 学生信息字典)。
        """
        return [
            (sid, stu)
            for sid, stu in self.data["students"].items()
            if stu.get("class") == class_name
        ]

    def exists(self, student_id: str) -> bool:
        """检查学生是否存在.

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
        """添加一条成绩修改历史记录.

        Args:
            student_id: 学号。
            subject: 科目名称。
            old: 修改前的成绩。
            new: 修改后的成绩。
            operator: 操作者标识。
        """
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
        self, student_id: Optional[str] = None, subject: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """获取成绩修改历史记录.

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

    def set_score(self, student_id: str, subject: str, score: Any) -> None:
        """设置学生成绩.

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

    def batch_set(self, student_id: str, scores_dict: dict[str, Any]) -> None:
        """批量设置学生成绩.

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
                # 成绩发生变化时记录历史
                if old_score != validated:
                    self._add_history(student_id, subject, old_score, validated)
                student["scores"][subject] = validated
            except (InvalidScoreError, ValueError, TypeError) as e:
                logger.warning(
                    "批量设置成绩跳过无效值: %s - %s = %s (%s)",
                    student_id,
                    subject,
                    score,
                    str(e),
                )
        self.save()

    # ------------------------------------------------------------------
    # 统计分析
    # ------------------------------------------------------------------

    def stats(self, student_id: str) -> Optional[dict[str, Any]]:
        """获取学生统计信息.

        Args:
            student_id: 学号。

        Returns:
            包含学号、姓名、班级、成绩、总分、平均分的字典；
            学生不存在或无成绩时返回 None。
        """
        student = self.get_student(student_id)
        if not student:
            return None

        scores = [v for v in student["scores"].values() if v is not None]
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
        student_ids: Optional[set[str]] = None,
    ) -> list[dict[str, Any]]:
        """获取学生排名.

        Args:
            by: 排序依据，可选 "total"(总分) / "avg"(平均分) / "subject"(科目)。
            subject: 当 by="subject" 时指定科目名称。
            student_ids: 可选的学生学号集合，仅统计该集合内的学生。

        Returns:
            排序后的学生列表，包含排名信息。无数据时返回空列表。
        """
        result: list[dict[str, Any]] = []
        students = self.data["students"]
        if student_ids is not None:
            students = {sid: students[sid] for sid in student_ids if sid in students}
        for sid in students:
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
        """分析科目成绩统计（兼容旧接口）.

        Args:
            subject: 科目名称。

        Returns:
            包含统计数据和分析结果的字典，无数据时返回 None。
        """
        return self.analyze_subject(subject)

    def analyze_subject(
        self, subject: str, student_ids: Optional[set[str]] = None
    ) -> Optional[dict[str, Any]]:
        """分析科目成绩统计.

        Args:
            subject: 科目名称。
            student_ids: 可选的学生学号集合，仅统计该集合内的学生。

        Returns:
            包含平均分、最高分、最低分、及格率、分布等统计数据的字典；
            无有效成绩时返回 None。
        """
        subject = subject.strip() if subject else ""
        if not subject:
            return None

        scores: list[float] = []
        students = self.data["students"]
        if student_ids is not None:
            students = {sid: students[sid] for sid in student_ids if sid in students}
        for student in students.values():
            score = student["scores"].get(subject)
            if score is not None:
                try:
                    scores.append(float(score))
                except (ValueError, TypeError):
                    logger.warning("科目分析跳过无效成绩: %s = %s", subject, score)

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
            "pass_rate": round(sum(1 for s in scores if s >= 60) / n * 100, 1),
            "excellent_rate": round(sum(1 for s in scores if s >= 90) / n * 100, 1),
            "distribution": distribution,
            "scores": [round(s, 2) for s in scores],
        }

    def search(self, keyword: str) -> list[str]:
        """搜索学生.

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
        """获取所有班级列表（排序后）. 同时包含有学生的班级和无学生的空班级."""
        # 1. 从学生信息中提取的班级（存在学生的）
        class_set: set[str] = set()
        for student in self.data["students"].values():
            cls = student.get("class", "")
            if cls:
                class_set.add(cls)

        # 2. 加入独立创建的班级列表（即使是空班级，列表里也会保留）
        if "classes" in self.data:
            class_set.update(self.data["classes"])

        return sorted(class_set)

    def add_class(self, class_name: str) -> str:
        """添加班级（会真正保存到独立班级列表）."""
        class_name = self._validate_class_name(class_name)

        # 确保 classes 列表在字典中存在
        if "classes" not in self.data:
            self.data["classes"] = []

        # 检查是否已经存在同名班级（无论是否有学生）
        if class_name in self.data["classes"]:
            raise DuplicateStudentError(class_name, label="班级")

        # 真正写入列表
        self.data["classes"].append(class_name)
        return class_name

    def get_class_stats(self, class_name: str) -> Optional[dict[str, Any]]:
        """获取班级统计信息.

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
            scores = [v for v in student["scores"].values() if v is not None]
            total = round(sum(scores), 2) if scores else 0.0
            avg = round(total / len(scores), 2) if scores else 0.0
            totals.append(
                {
                    "sid": sid,
                    "name": student["name"],
                    "total": total,
                    "avg": avg,
                }
            )

        totals.sort(key=lambda x: x["total"], reverse=True)
        for i, t in enumerate(totals, 1):
            t["rank"] = i

        overall = [t["total"] for t in totals]

        return {
            "class": class_name,
            "count": len(students),
            "total_avg": (round(sum(overall) / len(overall), 2) if overall else 0.0),
            "students": totals,
            "max_total": max(overall) if overall else 0.0,
            "min_total": min(overall) if overall else 0.0,
        }

    def get_warnings(self) -> list[dict[str, Any]]:
        """获取成绩预警学生列表.

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
                total_scores = [v for v in student["scores"].values() if v is not None]
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
    # 教师管理
    # ------------------------------------------------------------------

    @property
    def teachers(self) -> dict[str, dict[str, Any]]:
        """获取教师字典（深拷贝副本）.

        Returns:
            教师信息字典的深拷贝。
        """
        return copy.deepcopy(self.data["teachers"])

    def add_teacher(self, teacher_id: str, name: str, password: str = "") -> None:
        """添加教师账号.

        Args:
            teacher_id: 教师工号。
            name: 教师姓名。
            password: 登录密码，为空时默认为工号。

        Raises:
            DuplicateTeacherError: 工号已存在时抛出。
            InvalidInputError: 工号或姓名为空时抛出。
        """
        teacher_id = str(teacher_id).strip()
        name = str(name).strip()
        if not teacher_id:
            raise InvalidInputError("教师工号")
        if not name:
            raise InvalidInputError("教师姓名")
        if teacher_id in self.data["teachers"]:
            raise DuplicateTeacherError(teacher_id)
        self.data["teachers"][teacher_id] = {
            "name": name,
            "password": password if password else teacher_id,
            "course_ids": [],
        }
        self.save()
        logger.info("教师已添加: %s (%s)", teacher_id, name)

    def delete_teacher(self, teacher_id: str) -> None:
        """删除教师账号.

        Args:
            teacher_id: 教师工号。

        Raises:
            TeacherNotFoundError: 教师不存在时抛出。
        """
        teacher_id = str(teacher_id).strip()
        if teacher_id not in self.data["teachers"]:
            raise TeacherNotFoundError(teacher_id)
        del self.data["teachers"][teacher_id]
        self.save()
        logger.info("教师已删除: %s", teacher_id)

    def update_teacher(
        self,
        teacher_id: str,
        name: str = "",
        password: str = "",
        phone: str = "",
        email: str = "",
        gender: str = "",
        birth: str = "",
        avatar: str = "",
    ) -> None:
        """更新教师信息.

        Args:
            teacher_id: 教师工号。
            name: 新姓名，为空时不修改。
            password: 新密码，为空时不修改。
            phone: 手机号，为空时不修改。
            email: 邮箱，为空时不修改。
            gender: 性别，为空时不修改。
            birth: 生日，为空时不修改。
            avatar: 头像路径，为空时不修改。

        Raises:
            TeacherNotFoundError: 教师不存在时抛出。
        """
        teacher_id = str(teacher_id).strip()
        if teacher_id not in self.data["teachers"]:
            raise TeacherNotFoundError(teacher_id)
        teacher = self.data["teachers"][teacher_id]
        if name:
            teacher["name"] = str(name).strip()
        if password:
            teacher["password"] = str(password).strip()
        if phone is not None:
            teacher["phone"] = str(phone).strip()
        if email is not None:
            teacher["email"] = str(email).strip()
        if gender:
            teacher["gender"] = str(gender).strip()
        if birth is not None:
            teacher["birth"] = str(birth).strip()
        if avatar:
            teacher["avatar"] = str(avatar).strip()
        self.save()
        logger.info("教师信息已更新: %s", teacher_id)

    def get_teacher(self, teacher_id: str) -> Optional[dict[str, Any]]:
        """获取教师信息.

        Args:
            teacher_id: 教师工号。

        Returns:
            教师信息字典，不存在时返回 None。
        """
        return self.data["teachers"].get(str(teacher_id).strip())

    def reset_teacher_password(self, teacher_id: str) -> str:
        """重置教师密码为默认密码（工号）.

        Args:
            teacher_id: 教师工号。

        Returns:
            重置后的默认密码。

        Raises:
            TeacherNotFoundError: 教师不存在时抛出。
        """
        teacher_id = str(teacher_id).strip()
        if teacher_id not in self.data["teachers"]:
            raise TeacherNotFoundError(teacher_id)
        self.data["teachers"][teacher_id]["password"] = teacher_id
        self.save()
        logger.info("教师密码已重置: %s", teacher_id)
        return teacher_id

    def assign_course_to_teacher(self, teacher_id: str, course_id: str) -> None:
        """为教师分配课程.

        Args:
            teacher_id: 教师工号。
            course_id: 课程编号。

        Raises:
            TeacherNotFoundError: 教师不存在时抛出。
        """
        teacher_id = str(teacher_id).strip()
        if teacher_id not in self.data["teachers"]:
            raise TeacherNotFoundError(teacher_id)
        course_ids = self.data["teachers"][teacher_id].get("course_ids", [])
        if course_id not in course_ids:
            course_ids.append(course_id)
            self.data["teachers"][teacher_id]["course_ids"] = course_ids
            self.save()

    def remove_course_from_teacher(self, teacher_id: str, course_id: str) -> None:
        """移除教师的课程分配.

        Args:
            teacher_id: 教师工号。
            course_id: 课程编号。

        Raises:
            TeacherNotFoundError: 教师不存在时抛出。
        """
        teacher_id = str(teacher_id).strip()
        if teacher_id not in self.data["teachers"]:
            raise TeacherNotFoundError(teacher_id)
        course_ids = self.data["teachers"][teacher_id].get("course_ids", [])
        if course_id in course_ids:
            course_ids.remove(course_id)
            self.data["teachers"][teacher_id]["course_ids"] = course_ids
            self.save()

    # ------------------------------------------------------------------
    # 课程管理
    # ------------------------------------------------------------------

    @property
    def courses(self) -> dict[str, dict[str, Any]]:
        """获取课程字典（深拷贝副本）.

        Returns:
            课程信息字典的深拷贝。
        """
        return copy.deepcopy(self.data["courses"])

    def add_course(
        self,
        course_id: str,
        name: str,
        teacher_id: str = "",
        class_name: str = "",
    ) -> None:
        """添加课程.

        Args:
            course_id: 课程编号。
            name: 课程名称。
            teacher_id: 任课教师工号，可选。
            class_name: 所属班级，可选。

        Raises:
            DuplicateCourseError: 课程编号已存在时抛出。
            InvalidInputError: 课程编号或名称为空时抛出。
        """
        course_id = str(course_id).strip()
        name = str(name).strip()
        if not course_id:
            raise InvalidInputError("课程编号")
        if not name:
            raise InvalidInputError("课程名称")
        if course_id in self.data["courses"]:
            raise DuplicateCourseError(course_id)
        self.data["courses"][course_id] = {
            "name": name,
            "teacher_id": str(teacher_id).strip() if teacher_id else "",
            "class_name": str(class_name).strip() if class_name else "",
        }
        if teacher_id:
            self.assign_course_to_teacher(teacher_id, course_id)
        self.save()
        logger.info("课程已添加: %s (%s)", course_id, name)

    def delete_course(self, course_id: str) -> None:
        """删除课程.

        Args:
            course_id: 课程编号。

        Raises:
            CourseNotFoundError: 课程不存在时抛出。
        """
        course_id = str(course_id).strip()
        if course_id not in self.data["courses"]:
            raise CourseNotFoundError(course_id)
        teacher_id = self.data["courses"][course_id].get("teacher_id", "")
        if teacher_id:
            self.remove_course_from_teacher(teacher_id, course_id)
        del self.data["courses"][course_id]
        self.save()
        logger.info("课程已删除: %s", course_id)

    def update_course(
        self,
        course_id: str,
        name: str = "",
        teacher_id: str = "",
        class_name: str = "",
    ) -> None:
        """更新课程信息.

        Args:
            course_id: 课程编号。
            name: 新课程名称，为空时不修改。
            teacher_id: 新任课教师工号，为空时不修改。
            class_name: 新所属班级，为空时不修改。

        Raises:
            CourseNotFoundError: 课程不存在时抛出。
        """
        course_id = str(course_id).strip()
        if course_id not in self.data["courses"]:
            raise CourseNotFoundError(course_id)
        course = self.data["courses"][course_id]
        old_teacher = course.get("teacher_id", "")
        if name:
            course["name"] = str(name).strip()
        if teacher_id is not None:
            new_teacher = str(teacher_id).strip()
            if old_teacher and old_teacher != new_teacher:
                self.remove_course_from_teacher(old_teacher, course_id)
            if new_teacher:
                self.assign_course_to_teacher(new_teacher, course_id)
            course["teacher_id"] = new_teacher
        if class_name is not None:
            course["class_name"] = str(class_name).strip()
        self.save()
        logger.info("课程信息已更新: %s", course_id)

    def get_course(self, course_id: str) -> Optional[dict[str, Any]]:
        """获取课程信息.

        Args:
            course_id: 课程编号。

        Returns:
            课程信息字典，不存在时返回 None。
        """
        return self.data["courses"].get(str(course_id).strip())

    # ------------------------------------------------------------------
    # 认证方法
    # ------------------------------------------------------------------

    def authenticate_admin(self, username: str, password: str) -> bool:
        """验证管理员账号密码.

        Args:
            username: 管理员用户名。
            password: 密码。

        Returns:
            验证成功返回 True。
        """
        return str(username).strip() == "admin" and str(password).strip() == "123456"

    def authenticate_teacher(
        self, teacher_id: str, password: str
    ) -> Optional[dict[str, Any]]:
        """验证教师账号密码.

        Args:
            teacher_id: 教师工号。
            password: 密码。

        Returns:
            验证成功返回教师信息字典，失败返回 None。
        """
        teacher = self.data["teachers"].get(str(teacher_id).strip())
        if teacher and teacher.get("password") == str(password).strip():
            return {"teacher_id": teacher_id, "name": teacher["name"]}
        return None

    def authenticate_student(
        self, student_id: str, password: str
    ) -> Optional[dict[str, Any]]:
        """验证学生账号密码.

        Args:
            student_id: 学号。
            password: 密码。

        Returns:
            验证成功返回学生信息字典，失败返回 None。
        """
        student = self.data["students"].get(str(student_id).strip())
        if student and student.get("password") == str(password).strip():
            return {
                "student_id": student_id,
                "name": student["name"],
                "class": student.get("class", ""),
            }
        return None

    # ------------------------------------------------------------------
    # 考勤管理
    # ------------------------------------------------------------------

    def record_attendance(
        self,
        date: str,
        course_id: str,
        student_id: str,
        status: str,
    ) -> None:
        """记录学生考勤.

        Args:
            date: 考勤日期，格式 "YYYY-MM-DD"。
            course_id: 课程标识。
            student_id: 学号。
            status: 考勤状态，可选 present/absent/late/leave。

        Raises:
            StudentNotFoundError: 学生不存在时抛出。
            InvalidInputError: 日期或状态为空时抛出。
        """
        date = str(date).strip()
        course_id = str(course_id).strip()
        student_id = str(student_id).strip()
        status = str(status).strip().lower()
        if not date:
            raise InvalidInputError("date")
        if not course_id:
            raise InvalidInputError("course_id")
        if not student_id:
            raise InvalidInputError("student_id")
        if status not in ("present", "absent", "late", "leave"):
            status = "present"
        if student_id not in self.data["students"]:
            raise StudentNotFoundError(student_id)

        if date not in self.data["attendance"]:
            self.data["attendance"][date] = {}
        if course_id not in self.data["attendance"][date]:
            self.data["attendance"][date][course_id] = {}
        self.data["attendance"][date][course_id][student_id] = status
        self.save()

    def batch_record_attendance(
        self,
        date: str,
        course_id: str,
        records: dict[str, str],
    ) -> None:
        """批量记录考勤.

        Args:
            date: 考勤日期，格式 "YYYY-MM-DD"。
            course_id: 课程标识。
            records: 考勤字典，key 为学号，value 为状态。
        """
        date = str(date).strip()
        course_id = str(course_id).strip()
        if date not in self.data["attendance"]:
            self.data["attendance"][date] = {}
        if course_id not in self.data["attendance"][date]:
            self.data["attendance"][date][course_id] = {}
        for sid, status in records.items():
            sid = str(sid).strip()
            st = str(status).strip().lower()
            if st not in ("present", "absent", "late", "leave"):
                st = "present"
            if sid in self.data["students"]:
                self.data["attendance"][date][course_id][sid] = st
        self.save()

    def get_attendance(self, date: str, course_id: str) -> dict[str, str]:
        """获取指定日期和课程的考勤记录.

        Args:
            date: 考勤日期。
            course_id: 课程标识。

        Returns:
            学号到考勤状态的字典，无记录时返回空字典。
        """
        date = str(date).strip()
        course_id = str(course_id).strip()
        return copy.deepcopy(
            self.data.get("attendance", {}).get(date, {}).get(course_id, {})
        )

    def get_student_attendance(
        self,
        student_id: str,
        course_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """获取学生的考勤记录.

        Args:
            student_id: 学号。
            course_id: 课程标识，可选。
            start_date: 起始日期，可选。
            end_date: 结束日期，可选。

        Returns:
            考勤记录列表，每项包含 date、course_id、status。
        """
        student_id = str(student_id).strip()
        result: list[dict[str, Any]] = []
        for date, courses in self.data.get("attendance", {}).items():
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            for cid, records in courses.items():
                if course_id and cid != course_id:
                    continue
                if student_id in records:
                    result.append(
                        {
                            "date": date,
                            "course_id": cid,
                            "status": records[student_id],
                        }
                    )
        return sorted(result, key=lambda x: x["date"])

    def get_attendance_stats(self, date: str, course_id: str) -> dict[str, Any]:
        """获取指定日期和课程的考勤统计.

        Args:
            date: 考勤日期。
            course_id: 课程标识。

        Returns:
            包含总人数、出勤、缺勤、迟到、请假人数及出勤率的字典。
        """
        records = self.get_attendance(date, course_id)
        total = len(records)
        present = sum(1 for s in records.values() if s == "present")
        absent = sum(1 for s in records.values() if s == "absent")
        late = sum(1 for s in records.values() if s == "late")
        leave = sum(1 for s in records.values() if s == "leave")
        rate = round(present / total * 100, 1) if total else 0.0
        return {
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "leave": leave,
            "rate": rate,
        }

    def get_attendance_dates(self, course_id: str) -> list[str]:
        """获取课程的所有考勤日期.

        Args:
            course_id: 课程标识。

        Returns:
            日期字符串列表，按升序排列。
        """
        course_id = str(course_id).strip()
        dates: set[str] = set()
        for date, courses in self.data.get("attendance", {}).items():
            if course_id in courses:
                dates.add(date)
        return sorted(dates)

    def delete_attendance(self, date: str, course_id: str) -> None:
        """删除指定日期和课程的考勤记录.

        Args:
            date: 考勤日期。
            course_id: 课程标识。
        """
        date = str(date).strip()
        course_id = str(course_id).strip()
        if date in self.data.get("attendance", {}):
            self.data["attendance"][date].pop(course_id, None)
            if not self.data["attendance"][date]:
                del self.data["attendance"][date]
            self.save()

    def update_admin_profile(
        self,
        name: str = "",
        phone: str = "",
        email: str = "",
        gender: str = "",
        birth: str = "",
        avatar: str = "",
    ) -> None:
        """更新管理员个人信息.

        Args:
            name: 姓名，为空时不修改。
            phone: 手机号，为空时不修改。
            email: 邮箱，为空时不修改。
            gender: 性别，为空时不修改。
            birth: 生日，为空时不修改。
            avatar: 头像路径，为空时不修改。
        """
        admin = self.data.setdefault(
            "admin",
            {
                "username": "admin",
                "password": "123456",
                "avatar": "",
                "name": "管理员",
                "phone": "",
                "email": "",
                "gender": "",
                "birth": "",
            },
        )
        if name:
            admin["name"] = str(name).strip()
        if phone is not None:
            admin["phone"] = str(phone).strip()
        if email is not None:
            admin["email"] = str(email).strip()
        if gender:
            admin["gender"] = str(gender).strip()
        if birth is not None:
            admin["birth"] = str(birth).strip()
        if avatar:
            admin["avatar"] = str(avatar).strip()
        self.save()

    def get_admin(self) -> dict[str, Any]:
        """获取管理员信息.

        Returns:
            管理员信息字典。
        """
        return copy.deepcopy(
            self.data.get(
                "admin",
                {
                    "username": "admin",
                    "password": "123456",
                    "avatar": "",
                    "name": "管理员",
                    "phone": "",
                    "email": "",
                    "gender": "",
                    "birth": "",
                },
            )
        )

    # ------------------------------------------------------------------
    # 公告管理
    # ------------------------------------------------------------------

    def get_notices(self, role: Optional[str] = None) -> list[dict[str, Any]]:
        """获取公告列表.

        Args:
            role: 查看角色（admin/teacher/student），为 None 时返回全部。

        Returns:
            公告列表，按发布时间倒序排列。
        """
        notices = list(self.data.get("notices", []))
        if role is not None:
            role = str(role).strip()
            notices = [
                n
                for n in notices
                if n.get("target", "all") == "all" or n.get("target") == role
            ]
        return list(reversed(notices))

    def add_notice(
        self,
        title: str,
        content: str,
        publisher: str = "",
        publisher_role: str = "admin",
        target: str = "all",
    ) -> str:
        """添加公告.

        Args:
            title: 公告标题。
            content: 公告内容。
            publisher: 发布人姓名。
            publisher_role: 发布人角色（admin/teacher）。
            target: 目标角色（all/teacher/student）。

        Returns:
            新公告的 ID。
        """
        notice_id = str(uuid.uuid4())[:8]
        notice = {
            "id": notice_id,
            "title": str(title).strip(),
            "content": str(content).strip(),
            "publisher": str(publisher).strip(),
            "publisher_role": str(publisher_role).strip(),
            "target": str(target).strip(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.data.setdefault("notices", []).append(notice)
        self.save()
        logger.info("公告已添加: %s (%s)", notice_id, title)
        return notice_id

    def delete_notice(self, notice_id: str) -> None:
        """删除公告.

        Args:
            notice_id: 公告 ID。
        """
        notice_id = str(notice_id).strip()
        notices = self.data.get("notices", [])
        self.data["notices"] = [n for n in notices if n.get("id") != notice_id]
        self.save()
        logger.info("公告已删除: %s", notice_id)

    # ------------------------------------------------------------------
    # 课表管理
    # ------------------------------------------------------------------

    def get_schedules(self) -> list[dict[str, Any]]:
        """获取课表列表，按星期、时段和节次排序.

        Returns:
            课表列表，每个元素包含 id, weekday, session, period,
            course, teacher, room, updated_at。
        """
        schedules = list(self.data.get("schedules", []))
        weekday_order = {
            "周一": 1,
            "周二": 2,
            "周三": 3,
            "周四": 4,
            "周五": 5,
            "周六": 6,
            "周日": 7,
        }
        session_order = {"上午": 1, "下午": 2}
        schedules.sort(
            key=lambda s: (
                weekday_order.get(s.get("weekday", ""), 99),
                session_order.get(s.get("session", ""), 99),
                s.get("period", 0),
            )
        )
        return schedules

    def add_schedule(
        self,
        weekday: str,
        session: str,
        period: int,
        course: str,
        teacher: str,
        room: str,
        operator: str = "admin",
    ) -> str:
        """添加课表条目.

        Args:
            weekday: 星期（如"周一"）。
            session: 时段（"上午"或"下午"）。
            period: 节次。
            course: 课程名。
            teacher: 教师。
            room: 教室。
            operator: 操作者。

        Returns:
            新课表条目的 ID。
        """
        schedule_id = (
            f"sch_{len(self.data.get('schedules', [])) + 1}_"
            f"{int(datetime.datetime.now().timestamp())}"
        )
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {
            "id": schedule_id,
            "weekday": weekday.strip(),
            "session": session.strip(),
            "period": int(period),
            "course": course.strip(),
            "teacher": teacher.strip(),
            "room": room.strip(),
            "updated_at": now,
        }
        self.data.setdefault("schedules", []).append(entry)
        history_entry = {
            "time": now,
            "action": "新增",
            "old_summary": "",
            "new_summary": (
                f"{weekday} {session}第{period}节 " f"{course}({teacher}) {room}"
            ),
            "operator": operator,
        }
        self.data.setdefault("schedule_history", []).append(history_entry)
        self.save()
        logger.info(
            "课表已添加: %s %s%s第%s节 %s",
            schedule_id,
            weekday,
            session,
            period,
            course,
        )
        return schedule_id

    def update_schedule(
        self,
        schedule_id: str,
        weekday: str,
        session: str,
        period: int,
        course: str,
        teacher: str,
        room: str,
        operator: str = "admin",
    ) -> None:
        """更新课表条目.

        Args:
            schedule_id: 课表条目 ID。
            weekday: 星期。
            session: 时段（"上午"或"下午"）。
            period: 节次。
            course: 课程名。
            teacher: 教师。
            room: 教室。
            operator: 操作者。
        """
        schedule_id = str(schedule_id).strip()
        schedules = self.data.get("schedules", [])
        old_summary = ""
        for s in schedules:
            if s.get("id") == schedule_id:
                old_session = s.get("session", "")
                old_summary = (
                    f"{s.get('weekday', '')} {old_session}"
                    f"第{s.get('period', '')}节 "
                    f"{s.get('course', '')}({s.get('teacher', '')}) "
                    f"{s.get('room', '')}"
                )
                s["weekday"] = weekday.strip()
                s["session"] = session.strip()
                s["period"] = int(period)
                s["course"] = course.strip()
                s["teacher"] = teacher.strip()
                s["room"] = room.strip()
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                s["updated_at"] = now
                new_summary = (
                    f"{weekday.strip()} {session.strip()}"
                    f"第{period}节 "
                    f"{course.strip()}({teacher.strip()}) "
                    f"{room.strip()}"
                )
                history_entry = {
                    "time": now,
                    "action": "修改",
                    "old_summary": old_summary,
                    "new_summary": new_summary,
                    "operator": operator,
                }
                self.data.setdefault("schedule_history", []).append(history_entry)
                break
        self.save()
        logger.info("课表已更新: %s", schedule_id)

    def delete_schedule(self, schedule_id: str, operator: str = "admin") -> None:
        """删除课表条目.

        Args:
            schedule_id: 课表条目 ID。
            operator: 操作者。
        """
        schedule_id = str(schedule_id).strip()
        schedules = self.data.get("schedules", [])
        old_summary = ""
        for s in schedules:
            if s.get("id") == schedule_id:
                old_summary = (
                    f"{s.get('weekday', '')} "
                    f"{s.get('session', '')}"
                    f"第{s.get('period', '')}节 "
                    f"{s.get('course', '')}({s.get('teacher', '')}) "
                    f"{s.get('room', '')}"
                )
                break
        self.data["schedules"] = [s for s in schedules if s.get("id") != schedule_id]
        if old_summary:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            history_entry = {
                "time": now,
                "action": "删除",
                "old_summary": old_summary,
                "new_summary": "",
                "operator": operator,
            }
            self.data.setdefault("schedule_history", []).append(history_entry)
        self.save()
        logger.info("课表已删除: %s", schedule_id)

    def get_schedule_history(self) -> list[dict[str, Any]]:
        """获取课表变更历史，按时间倒序.

        Returns:
            历史记录列表，每个元素包含 time, action, old_summary, new_summary, operator。
        """
        history = list(self.data.get("schedule_history", []))
        return list(reversed(history))

    def clear_schedule_history(self) -> None:
        """清空课表变更历史记录."""
        self.data["schedule_history"] = []
        self.save()
        logger.info("课表变更历史已清空")


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
