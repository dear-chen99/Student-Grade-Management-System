"""DataManager 单元测试."""

import json
import os
import pytest
from modules.data_manager import (
    DataManager,
    DuplicateStudentError,
    StudentNotFoundError,
    DuplicateTeacherError,
    TeacherNotFoundError,
    CourseNotFoundError,
    DuplicateCourseError,
    InvalidScoreError,
)


@pytest.fixture
def dm(tmp_path):
    """创建使用临时文件的 DataManager 实例."""
    fp = tmp_path / "grades.json"
    return DataManager(file_path=str(fp))


class TestStudent:
    """学生管理测试."""

    def test_add_student(self, dm):
        """添加学生."""
        dm.add_student("2024001", "张三", "24计软1班")
        assert dm.exists("2024001")
        stu = dm.get_student("2024001")
        assert stu["name"] == "张三"
        assert stu["class"] == "24计软1班"

    def test_add_duplicate_student(self, dm):
        """重复添加学生应抛出异常."""
        dm.add_student("2024001", "张三", "24计软1班")
        with pytest.raises(DuplicateStudentError):
            dm.add_student("2024001", "张三", "24计软1班")

    def test_update_student(self, dm):
        """更新学生信息."""
        dm.add_student("2024001", "张三", "24计软1班")
        dm.update_student("2024001", name="张三丰", phone="13800138000")
        stu = dm.get_student("2024001")
        assert stu["name"] == "张三丰"
        assert stu["phone"] == "13800138000"

    def test_update_student_not_found(self, dm):
        """更新不存在的学生应抛出异常."""
        with pytest.raises(StudentNotFoundError):
            dm.update_student("9999999", name="不存在")

    def test_delete_student(self, dm):
        """删除学生."""
        dm.add_student("2024001", "张三", "24计软1班")
        dm.delete_student("2024001")
        assert not dm.exists("2024001")

    def test_delete_student_not_found(self, dm):
        """删除不存在的学生应抛出异常."""
        with pytest.raises(StudentNotFoundError):
            dm.delete_student("9999999")

    def test_get_students_by_class(self, dm):
        """按班级获取学生."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_student("2024002", "李四", "A班")
        dm.add_student("2024003", "王五", "B班")
        result = dm.get_students_by_class("A班")
        assert len(result) == 2
        sids = [sid for sid, _ in result]
        assert "2024001" in sids
        assert "2024002" in sids


class TestScore:
    """成绩管理测试."""

    def test_set_score(self, dm):
        """设置成绩."""
        dm.add_student("2024001", "张三", "24计软1班")
        dm.add_subject("数学")
        dm.set_score("2024001", "数学", 85.5)
        stu = dm.get_student("2024001")
        assert stu["scores"]["数学"] == 85.5

    def test_set_score_invalid(self, dm):
        """设置无效成绩应抛出异常."""
        dm.add_student("2024001", "张三", "24计软1班")
        dm.add_subject("数学")
        with pytest.raises(InvalidScoreError):
            dm.set_score("2024001", "数学", 105)
        with pytest.raises(InvalidScoreError):
            dm.set_score("2024001", "数学", -5)

    def test_stats(self, dm):
        """统计学生成绩."""
        dm.add_student("2024001", "张三", "24计软1班")
        dm.add_subject("数学")
        dm.add_subject("英语")
        dm.set_score("2024001", "数学", 80)
        dm.set_score("2024001", "英语", 90)
        st = dm.stats("2024001")
        assert st["total"] == 170
        assert st["avg"] == 85.0

    def test_stats_no_scores(self, dm):
        """无成绩时统计总分和平均分应为 0."""
        dm.add_student("2024001", "张三", "24计软1班")
        st = dm.stats("2024001")
        assert st is not None
        assert st["total"] == 0.0
        assert st["avg"] == 0.0

    def test_batch_set(self, dm):
        """批量设置成绩."""
        dm.add_student("2024001", "张三", "24计软1班")
        dm.add_subject("数学")
        dm.add_subject("英语")
        dm.batch_set("2024001", {"数学": 75, "英语": 85})
        stu = dm.get_student("2024001")
        assert stu["scores"]["数学"] == 75
        assert stu["scores"]["英语"] == 85


class TestSubject:
    """科目管理测试."""

    def test_add_subject(self, dm):
        """添加科目."""
        dm.add_subject("物理")
        assert "物理" in dm.subjects

    def test_delete_subject(self, dm):
        """删除科目."""
        dm.add_subject("物理")
        dm.delete_subject("物理")
        assert "物理" not in dm.subjects


class TestClass:
    """班级管理测试."""

    def test_add_class(self, dm):
        """添加班级."""
        cid = dm.add_class("24计软1班")
        assert cid == "24计软1班"

    def test_get_class_stats(self, dm):
        """班级统计."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_student("2024002", "李四", "A班")
        dm.add_subject("数学")
        dm.set_score("2024001", "数学", 90)
        dm.set_score("2024002", "数学", 80)
        stats = dm.get_class_stats("A班")
        assert stats is not None
        assert stats["count"] == 2
        assert stats["total_avg"] == 85.0

    def test_get_class_stats_empty(self, dm):
        """空班级统计."""
        assert dm.get_class_stats("不存在的班") is None


class TestTeacher:
    """教师管理测试."""

    def test_add_teacher(self, dm):
        """添加教师."""
        dm.add_teacher("T001", "王老师", "123456")
        teacher = dm.get_teacher("T001")
        assert teacher["name"] == "王老师"

    def test_add_duplicate_teacher(self, dm):
        """重复添加教师应抛出异常."""
        dm.add_teacher("T001", "王老师", "123456")
        with pytest.raises(DuplicateTeacherError):
            dm.add_teacher("T001", "王老师", "123456")

    def test_update_teacher(self, dm):
        """更新教师信息."""
        dm.add_teacher("T001", "王老师", "123456")
        dm.update_teacher("T001", name="王教授", phone="13900139000")
        teacher = dm.get_teacher("T001")
        assert teacher["name"] == "王教授"
        assert teacher["phone"] == "13900139000"

    def test_delete_teacher(self, dm):
        """删除教师."""
        dm.add_teacher("T001", "王老师", "123456")
        dm.delete_teacher("T001")
        assert dm.get_teacher("T001") is None

    def test_delete_teacher_not_found(self, dm):
        """删除不存在的教师应抛出异常."""
        with pytest.raises(TeacherNotFoundError):
            dm.delete_teacher("T999")


class TestCourse:
    """课程管理测试."""

    def test_add_course(self, dm):
        """添加课程."""
        dm.add_teacher("T001", "王老师", "123456")
        dm.add_course("C001", "数学", "T001", "24计软1班")
        course = dm.get_course("C001")
        assert course["name"] == "数学"

    def test_add_duplicate_course(self, dm):
        """重复添加课程应抛出异常."""
        dm.add_teacher("T001", "王老师", "123456")
        dm.add_course("C001", "数学", "T001", "24计软1班")
        with pytest.raises(DuplicateCourseError):
            dm.add_course("C001", "数学", "T001", "24计软1班")

    def test_update_course(self, dm):
        """更新课程."""
        dm.add_teacher("T001", "王老师", "123456")
        dm.add_course("C001", "数学", "T001", "24计软1班")
        dm.update_course("C001", name="高等数学")
        course = dm.get_course("C001")
        assert course["name"] == "高等数学"

    def test_delete_course(self, dm):
        """删除课程."""
        dm.add_teacher("T001", "王老师", "123456")
        dm.add_course("C001", "数学", "T001", "24计软1班")
        dm.delete_course("C001")
        assert dm.get_course("C001") is None

    def test_get_course_not_found(self, dm):
        """获取不存在的课程."""
        assert dm.get_course("C999") is None


class TestAttendance:
    """考勤管理测试."""

    def test_record_attendance(self, dm):
        """记录考勤."""
        dm.add_student("2024001", "张三", "A班")
        dm.record_attendance("2026-06-15", "C001", "2024001", "出勤")
        records = dm.get_attendance("2026-06-15", "C001")
        assert records["2024001"] == "present"

    def test_batch_record_attendance(self, dm):
        """批量记录考勤."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_student("2024002", "李四", "A班")
        dm.batch_record_attendance(
            "2026-06-15",
            "C001",
            {"2024001": "present", "2024002": "absent"},
        )
        records = dm.get_attendance("2026-06-15", "C001")
        assert records["2024001"] == "present"
        assert records["2024002"] == "absent"

    def test_get_attendance_stats(self, dm):
        """考勤统计."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_student("2024002", "李四", "A班")
        dm.add_student("2024003", "王五", "A班")
        dm.batch_record_attendance(
            "2026-06-15",
            "C001",
            {
                "2024001": "present",
                "2024002": "absent",
                "2024003": "late",
            },
        )
        stats = dm.get_attendance_stats("2026-06-15", "C001")
        assert stats["total"] == 3
        assert stats["present"] == 1
        assert stats["absent"] == 1
        assert stats["late"] == 1

    def test_delete_attendance(self, dm):
        """删除考勤记录."""
        dm.add_student("2024001", "张三", "A班")
        dm.record_attendance("2026-06-15", "C001", "2024001", "出勤")
        dm.delete_attendance("2026-06-15", "C001")
        assert dm.get_attendance("2026-06-15", "C001") == {}


class TestNotice:
    """通知管理测试."""

    def test_add_notice(self, dm):
        """添加通知."""
        dm.add_notice("考试通知", "下周一考试", "admin", "all")
        notices = dm.get_notices()
        assert len(notices) == 1
        assert notices[0]["title"] == "考试通知"

    def test_get_notices_by_role(self, dm):
        """按角色获取通知."""
        dm.add_notice("全员通知", "内容1", "admin", target="all")
        dm.add_notice("教师通知", "内容2", "admin", target="teacher")
        dm.add_notice("学生通知", "内容3", "admin", target="student")
        teacher_notices = dm.get_notices("teacher")
        assert len(teacher_notices) == 2
        student_notices = dm.get_notices("student")
        assert len(student_notices) == 2

    def test_delete_notice(self, dm):
        """删除通知."""
        dm.add_notice("考试通知", "下周一考试", "admin", "all")
        nid = dm.get_notices()[0]["id"]
        dm.delete_notice(nid)
        assert len(dm.get_notices()) == 0


class TestAdmin:
    """管理员测试."""

    def test_update_admin_profile(self, dm):
        """更新管理员信息."""
        dm.update_admin_profile(name="超级管理员", phone="10086")
        admin = dm.get_admin()
        assert admin["name"] == "超级管理员"
        assert admin["phone"] == "10086"

    def test_get_admin_default(self, dm):
        """获取默认管理员."""
        admin = dm.get_admin()
        assert admin["username"] == "admin"


class TestSchedule:
    """课表管理测试."""

    def test_add_schedule(self, dm):
        """添加课表."""
        dm.add_schedule("周一", "上午", 1, "数学", "T001", "王老师")
        schedules = dm.get_schedules()
        assert len(schedules) == 1
        assert schedules[0]["weekday"] == "周一"

    def test_delete_schedule(self, dm):
        """删除课表."""
        dm.add_schedule("周一", "上午", 1, "数学", "T001", "王老师")
        sid = dm.get_schedules()[0]["id"]
        dm.delete_schedule(sid)
        assert len(dm.get_schedules()) == 0

    def test_get_schedule_history(self, dm):
        """课表历史记录."""
        dm.add_schedule("周一", "上午", 1, "数学", "T001", "王老师")
        sid = dm.get_schedules()[0]["id"]
        dm.delete_schedule(sid)
        history = dm.get_schedule_history()
        assert len(history) == 2


class TestPersistence:
    """数据持久化测试."""

    def test_save_and_load(self, tmp_path):
        """保存后重新加载数据."""
        fp = tmp_path / "grades.json"
        dm1 = DataManager(file_path=str(fp))
        dm1.add_student("2024001", "张三", "A班")
        dm1.add_subject("数学")
        dm1.set_score("2024001", "数学", 88)
        dm1.save()

        dm2 = DataManager(file_path=str(fp))
        assert dm2.exists("2024001")
        stu = dm2.get_student("2024001")
        assert stu["scores"]["数学"] == 88

    def test_load_corrupted_json(self, tmp_path):
        """加载损坏的 JSON 文件应创建空数据."""
        fp = tmp_path / "grades.json"
        fp.write_text("not valid json", encoding="utf-8")
        dm = DataManager(file_path=str(fp))
        assert dm.data is not None
        assert "students" in dm.data


class TestWarnings:
    """预警功能测试."""

    def test_get_warnings(self, dm):
        """获取成绩预警学生."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_student("2024002", "李四", "A班")
        dm.add_subject("数学")
        dm.set_score("2024001", "数学", 55)
        dm.set_score("2024002", "数学", 90)
        warnings = dm.get_warnings()
        assert len(warnings) == 1
        assert warnings[0]["sid"] == "2024001"


class TestTeacherPasswordReset:
    """教师密码重置测试."""

    def test_reset_teacher_password(self, dm):
        """重置教师密码."""
        dm.add_teacher("T001", "王老师", "oldpass")
        new_pwd = dm.reset_teacher_password("T001")
        assert new_pwd == "T001"
        teacher = dm.get_teacher("T001")
        assert teacher["password"] == "T001"


class TestSearch:
    """搜索功能测试."""

    def test_search_by_name(self, dm):
        """按姓名搜索学生."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_student("2024002", "李四", "B班")
        results = dm.search("张三")
        assert "2024001" in results

    def test_search_by_id(self, dm):
        """按学号搜索学生."""
        dm.add_student("2024001", "张三", "A班")
        results = dm.search("2024001")
        assert "2024001" in results

    def test_search_no_match(self, dm):
        """搜索无结果."""
        dm.add_student("2024001", "张三", "A班")
        results = dm.search("王五")
        assert len(results) == 0


class TestRanking:
    """排名功能测试."""

    def test_ranking(self, dm):
        """学生排名."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_student("2024002", "李四", "A班")
        dm.add_subject("数学")
        dm.set_score("2024001", "数学", 90)
        dm.set_score("2024002", "数学", 80)
        ranks = dm.ranking()
        assert len(ranks) == 2
        assert ranks[0]["rank"] == 1


class TestScheduleUpdate:
    """课表更新测试."""

    def test_update_schedule(self, dm):
        """更新课表信息."""
        dm.add_schedule("周一", "上午", 1, "数学", "T001", "王老师")
        sid = dm.get_schedules()[0]["id"]
        dm.update_schedule(sid, "周二", "下午", 2, "英语", "T002", "李老师")
        sched = dm.get_schedules()[0]
        assert sched["weekday"] == "周二"
        assert sched["period"] == 2
        assert sched["course"] == "英语"

    def test_clear_schedule_history(self, dm):
        """清空课表历史."""
        dm.add_schedule("周一", "上午", 1, "数学", "T001", "王老师")
        sid = dm.get_schedules()[0]["id"]
        dm.delete_schedule(sid)
        assert len(dm.get_schedule_history()) > 0
        dm.clear_schedule_history()
        assert len(dm.get_schedule_history()) == 0


class TestAttendanceQuery:
    """考勤查询测试."""

    def test_get_student_attendance(self, dm):
        """获取单个学生考勤记录."""
        dm.add_student("2024001", "张三", "A班")
        dm.record_attendance("2026-06-15", "C001", "2024001", "出勤")
        records = dm.get_student_attendance("2024001")
        assert len(records) == 1

    def test_get_attendance_dates(self, dm):
        """获取课程的所有考勤日期."""
        dm.add_student("2024001", "张三", "A班")
        dm.record_attendance("2026-06-15", "C001", "2024001", "出勤")
        dm.record_attendance("2026-06-16", "C001", "2024001", "出勤")
        dates = dm.get_attendance_dates("C001")
        assert "2026-06-15" in dates
        assert "2026-06-16" in dates


class TestHistory:
    """历史记录测试."""

    def test_get_history(self, dm):
        """获取成绩修改历史."""
        dm.add_student("2024001", "张三", "A班")
        dm.add_subject("数学")
        dm.set_score("2024001", "数学", 80)
        history = dm.get_history("2024001")
        assert len(history) == 1
        assert history[0]["subject"] == "数学"
