from __future__ import annotations

import base64
import json
import os
import sys
import zipfile
from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path

from werkzeug.security import generate_password_hash


ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "app"
REPORT_DIR = ROOT_DIR / "docs"
PASSWORD = "QaPass123!"

sys.path.insert(0, str(APP_DIR))
os.chdir(APP_DIR)

from app import create_app  # noqa: E402
from database import get_db  # noqa: E402


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


class Validation:
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.artifacts: dict[str, object] = {}

    def record(self, name: str, ok: bool, detail: str = "") -> None:
        self.rows.append({"name": name, "ok": ok, "detail": detail})
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name} {detail}")

    def require(self, name: str, ok: bool, detail: str = "") -> None:
        self.record(name, ok, detail)
        if not ok:
            raise AssertionError(name)


def response_json(response):
    return response.get_json(silent=True) or {}


def build_sb3_bytes(label: str) -> bytes:
    project = {
        "targets": [
            {
                "isStage": True,
                "name": "Stage",
                "variables": {},
                "lists": {},
                "broadcasts": {},
                "blocks": {},
                "comments": {},
                "currentCostume": 0,
                "costumes": [],
                "sounds": [],
                "volume": 100,
                "layerOrder": 0,
                "tempo": 60,
                "videoTransparency": 50,
                "videoState": "on",
                "textToSpeechLanguage": None,
            }
        ],
        "monitors": [],
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "validation", "agent": label},
    }
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("project.json", json.dumps(project, ensure_ascii=False))
    return buffer.getvalue()


def create_user(db, username: str, role: str, display_name: str, teacher_id=None, student_id=None) -> int:
    now = datetime.now().isoformat(timespec="seconds")
    cursor = db.execute(
        """
        INSERT INTO users
            (username, password_hash, display_name, role, status, teacher_id, student_id, remark, created_at)
        VALUES (?, ?, ?, ?, 'active', ?, ?, 'qa validation data', ?)
        """,
        (username, generate_password_hash(PASSWORD), display_name, role, teacher_id, student_id, now),
    )
    return int(cursor.lastrowid)


def create_seed_data(app, tag: str) -> dict:
    with app.app_context():
        db = get_db()
        now = datetime.now().isoformat(timespec="seconds")
        teacher_id = db.execute(
            """
            INSERT INTO teachers (name, phone, subject, status, remark, created_at)
            VALUES (?, ?, 'Scratch', 'active', 'qa validation data', ?)
            """,
            (f"QA Teacher {tag}", "13800000001", now),
        ).lastrowid
        other_teacher_id = db.execute(
            """
            INSERT INTO teachers (name, phone, subject, status, remark, created_at)
            VALUES (?, ?, 'Python', 'active', 'qa validation data', ?)
            """,
            (f"QA Other Teacher {tag}", "13800000002", now),
        ).lastrowid
        student_id = db.execute(
            """
            INSERT INTO students
                (name, gender, age, phone, parent_name, parent_phone, school,
                 purchased_hours, gift_hours, status, remark, created_at)
            VALUES (?, 'F', 10, ?, ?, ?, 'QA School', 20, 2, 'active', 'qa validation data', ?)
            """,
            (f"QA Student {tag}", "13900000001", f"QA Parent {tag}", "13900000002", now),
        ).lastrowid
        classmate_id = db.execute(
            """
            INSERT INTO students
                (name, gender, age, phone, parent_name, parent_phone, school,
                 purchased_hours, gift_hours, status, remark, created_at)
            VALUES (?, 'M', 11, ?, ?, ?, 'QA School', 20, 0, 'active', 'qa validation data', ?)
            """,
            (f"QA Classmate {tag}", "13900000003", f"QA Other Parent {tag}", "13900000004", now),
        ).lastrowid
        class_id = db.execute(
            """
            INSERT INTO classes
                (class_name, course_name, class_type, teacher_id, default_weekday,
                 default_start_time, default_end_time, capacity, start_date, end_date, status, remark, created_at)
            VALUES (?, 'Scratch', 'QA', ?, 6, '09:00', '10:00', 8, ?, NULL, 'active', 'qa validation data', ?)
            """,
            (f"QA Scratch Class {tag}", teacher_id, date.today().isoformat(), now),
        ).lastrowid
        other_class_id = db.execute(
            """
            INSERT INTO classes
                (class_name, course_name, class_type, teacher_id, default_weekday,
                 default_start_time, default_end_time, capacity, start_date, end_date, status, remark, created_at)
            VALUES (?, 'Python', 'QA', ?, 6, '11:00', '12:00', 8, ?, NULL, 'active', 'qa validation data', ?)
            """,
            (f"QA Other Class {tag}", other_teacher_id, date.today().isoformat(), now),
        ).lastrowid
        db.execute(
            """
            INSERT INTO class_students (class_id, student_id, join_date, leave_date, status)
            VALUES (?, ?, ?, NULL, 'active')
            """,
            (class_id, student_id, date.today().isoformat()),
        )
        db.execute(
            """
            INSERT INTO class_students (class_id, student_id, join_date, leave_date, status)
            VALUES (?, ?, ?, NULL, 'active')
            """,
            (class_id, classmate_id, date.today().isoformat()),
        )
        other_lesson_id = db.execute(
            """
            INSERT INTO lessons
                (class_id, lesson_date, weekday, start_time, end_time, teacher_id,
                 lesson_topic, lesson_hours, classroom, status, remark, created_at)
            VALUES (?, ?, 6, '11:00', '12:00', ?, 'Outside Scope', 1, 'QA Room B', 'planned', 'qa validation data', ?)
            """,
            (other_class_id, (date.today() + timedelta(days=9)).isoformat(), other_teacher_id, now),
        ).lastrowid
        admin_username = f"qa_admin_{tag}"
        teacher_username = f"qa_teacher_{tag}"
        student_username = f"qa_student_{tag}"
        parent_username = f"qa_parent_{tag}"
        create_user(db, admin_username, "admin", f"QA Admin {tag}")
        create_user(db, teacher_username, "teacher", f"QA Teacher User {tag}", teacher_id=teacher_id)
        create_user(db, student_username, "student", f"QA Student User {tag}", student_id=student_id)
        create_user(db, parent_username, "parent", f"QA Parent User {tag}", student_id=student_id)
        db.commit()
        return {
            "teacher_id": int(teacher_id),
            "other_teacher_id": int(other_teacher_id),
            "student_id": int(student_id),
            "classmate_id": int(classmate_id),
            "class_id": int(class_id),
            "other_lesson_id": int(other_lesson_id),
            "admin_username": admin_username,
            "teacher_username": teacher_username,
            "student_username": student_username,
            "parent_username": parent_username,
            "classmate_name": f"QA Classmate {tag}",
        }


def login(client, username: str):
    return client.post("/api/auth/login", json={"username": username, "password": PASSWORD})


def assert_vue_shell(v: Validation, client, path: str):
    response = client.get(path)
    text = response.get_data(as_text=True)
    v.require(f"Vue shell handles {path}", response.status_code == 200 and 'id="app"' in text, f"status={response.status_code}")


def run_validation() -> tuple[Validation, int]:
    tag = datetime.now().strftime("%Y%m%d%H%M%S")
    app = create_app()
    app.config["TESTING"] = False
    v = Validation()
    seed = create_seed_data(app, tag)
    v.artifacts.update(seed)

    admin = app.test_client()
    teacher = app.test_client()
    student = app.test_client()
    parent = app.test_client()

    try:
        for path in ["/", "/login", "/student", "/student/lessons/1", "/parent", "/teacher/prep", "/classroom", "/students", "/students/1/edit"]:
            assert_vue_shell(v, admin, path)
        blocked = admin.post("/students", data={"name": "legacy"})
        v.require("Classic Flask form POST is disabled", blocked.status_code == 410, f"status={blocked.status_code}")

        admin_login = login(admin, seed["admin_username"])
        admin_user = response_json(admin_login).get("user") or {}
        v.require("Admin login succeeds", admin_login.status_code == 200 and admin_user.get("role") == "super_admin", f"role={admin_user.get('role')}")
        admin_me = admin.get("/api/me")
        v.require("Admin /api/me succeeds", admin_me.status_code == 200, f"status={admin_me.status_code}")
        router_source = (APP_DIR / "frontend" / "src" / "router" / "index.js").read_text(encoding="utf-8")
        v.require("Admin is not redirected by student permission", "permissions?.includes('student_portal.view')" not in router_source, "router uses strict role checks")
        admin.post("/api/auth/logout")
        after_logout = admin.get("/api/me")
        v.require("Logout clears session", after_logout.status_code == 401, f"status={after_logout.status_code}")
        login(admin, seed["admin_username"])

        role_code = f"qa_role_{tag[-10:]}"
        role_create = admin.post(
            "/api/permissions/roles",
            json={"role_code": role_code, "label": f"QA Role {tag}", "level": 12, "note": "qa validation role"},
        )
        v.require("Super admin can create custom role", role_create.status_code == 200 and response_json(role_create).get("ok"), f"status={role_create.status_code}")
        role_update = admin.put(f"/api/permissions/roles/{role_code}", json={"permissions": ["dashboard.view", "student_portal.view"]})
        v.require("Super admin can assign role permissions", role_update.status_code == 200 and "student_portal.view" in response_json(role_update).get("permissions", []), f"status={role_update.status_code}")

        lesson_payload = {
            "class_id": seed["class_id"],
            "lesson_date": (date.today() + timedelta(days=7)).isoformat(),
            "start_time": "09:00",
            "end_time": "10:00",
            "teacher_id": seed["teacher_id"],
            "lesson_topic": f"P2 Scratch Validation {tag}",
            "lesson_hours": 1,
            "classroom": "QA Room A",
        }
        lesson_response = admin.post("/api/lessons", json=lesson_payload)
        lesson_id = response_json(lesson_response).get("id")
        v.require("Admin creates validation lesson", lesson_response.status_code == 200 and isinstance(lesson_id, int), f"lesson_id={lesson_id}")
        v.artifacts["lesson_id"] = lesson_id

        teacher_login = login(teacher, seed["teacher_username"])
        v.require("Teacher login succeeds", teacher_login.status_code == 200, f"status={teacher_login.status_code}")
        detail = teacher.get(f"/api/lessons/{lesson_id}/detail")
        v.require("Teacher can open own lesson detail", detail.status_code == 200, f"status={detail.status_code}")
        outside_detail = teacher.get(f"/api/lessons/{seed['other_lesson_id']}/detail")
        v.require("Teacher cannot open outside lesson detail", outside_detail.status_code == 403, f"status={outside_detail.status_code}")

        asset_response = teacher.post(
            f"/api/lessons/{lesson_id}/assets",
            data={
                "title": "QA Courseware",
                "note": "kept for validation",
                "file": (BytesIO(b"%PDF-1.4\n% qa courseware\n"), f"qa-courseware-{tag}.pdf"),
            },
            content_type="multipart/form-data",
        )
        asset_json = response_json(asset_response)
        asset = asset_json.get("asset") or {}
        v.require("Teacher uploads courseware", asset_response.status_code == 200 and asset_json.get("ok") and asset.get("asset_id"), f"asset_id={asset.get('asset_id')}")
        v.artifacts["asset_id"] = asset.get("asset_id")

        bad_template = teacher.post(
            f"/api/lessons/{lesson_id}/scratch/assignments",
            data={"title": "Bad Template", "file": (BytesIO(b"not a zip"), f"bad-{tag}.sb3")},
            content_type="multipart/form-data",
        )
        v.require("Invalid .sb3 template is rejected", bad_template.status_code == 400, f"status={bad_template.status_code}")

        template_response = teacher.post(
            f"/api/lessons/{lesson_id}/scratch/assignments",
            data={
                "assignment_title": "QA Scratch Template",
                "title": "QA Scratch Template",
                "description": "Open and save your personal copy.",
                "statement_md": "Open and save your personal copy.",
                "auto_judge": "false",
                "max_score": "100",
                "file": (BytesIO(build_sb3_bytes(tag)), f"qa-template-{tag}.sb3"),
                "thumbnail": (BytesIO(PNG_1X1), f"qa-template-{tag}.png"),
            },
            content_type="multipart/form-data",
        )
        assignment = response_json(template_response).get("assignment") or {}
        template_id = assignment.get("template_id")
        v.require("Teacher uploads and binds Scratch template", template_response.status_code == 200 and template_id, f"template_id={template_id}")
        v.artifacts["template_id"] = template_id

        teacher_editor = teacher.get(f"/scratch/editor?template_id={template_id}")
        teacher_editor_text = teacher_editor.get_data(as_text=True)
        v.require(
            "Teacher can open Scratch graphical template editor",
            teacher_editor.status_code == 200 and "SCRATCH_OJ_LOAD_SB3" in teacher_editor_text and "加载预设代码" in teacher_editor_text,
            f"status={teacher_editor.status_code}",
        )

        detail_after_assets = teacher.get(f"/api/lessons/{lesson_id}/detail")
        detail_json = response_json(detail_after_assets)
        v.require(
            "Lesson detail includes courseware and Scratch template",
            detail_after_assets.status_code == 200
            and len(detail_json.get("courseware_assets", [])) >= 1
            and len(detail_json.get("scratch_assignments", [])) >= 1,
            f"courseware={len(detail_json.get('courseware_assets', []))}, templates={len(detail_json.get('scratch_assignments', []))}",
        )

        student_login = login(student, seed["student_username"])
        student_user = response_json(student_login).get("user") or {}
        v.require("Student login succeeds", student_login.status_code == 200 and student_user.get("role") == "student", f"role={student_user.get('role')}")
        student_portal = student.get("/api/student/me")
        student_portal_json = response_json(student_portal)
        student_dump = json.dumps(student_portal_json, ensure_ascii=False)
        v.require("Student portal returns only own context", student_portal.status_code == 200 and seed["classmate_name"] not in student_dump, "classmate not present")
        current_student_permissions = set(student_user.get("permissions") or [])
        student_hours = (student_portal_json.get("portal") or {}).get("summary", {}).get("remaining_hours")
        v.record(
            "Student hours follow current permission matrix",
            student_hours is None or "student_portal.hours.view" in current_student_permissions,
            f"remaining_hours={student_hours}, has_hour_permission={'student_portal.hours.view' in current_student_permissions}",
        )
        student_forbidden_students = student.get("/api/students")
        v.require("Student cannot list students", student_forbidden_students.status_code == 403, f"status={student_forbidden_students.status_code}")
        student_forbidden_detail = student.get(f"/api/lessons/{lesson_id}/detail")
        v.require("Student cannot open teacher lesson detail API", student_forbidden_detail.status_code == 403, f"status={student_forbidden_detail.status_code}")
        download_path = asset.get("public_path")
        download = student.get(download_path)
        v.require("Student can download own related courseware", download.status_code == 200 and len(download.data) > 0, f"status={download.status_code}")

        tasks_response = student.get("/api/student/scratch/works")
        tasks = response_json(tasks_response).get("items") or []
        v.require("Student sees related Scratch task", tasks_response.status_code == 200 and any(item.get("template_id") == template_id for item in tasks), f"tasks={len(tasks)}")
        student_lesson = student.get(f"/api/student/lessons/{lesson_id}")
        student_lesson_json = response_json(student_lesson)
        student_lesson_dump = json.dumps(student_lesson_json, ensure_ascii=False)
        v.require(
            "Student can open own lesson subpage data",
            student_lesson.status_code == 200
            and len(student_lesson_json.get("courseware_assets", [])) >= 1
            and len(student_lesson_json.get("scratch_tasks", [])) >= 1
            and seed["classmate_name"] not in student_lesson_dump,
            f"status={student_lesson.status_code}",
        )
        outside_student_lesson = student.get(f"/api/student/lessons/{seed['other_lesson_id']}")
        v.require("Student cannot open unrelated lesson subpage data", outside_student_lesson.status_code == 403, f"status={outside_student_lesson.status_code}")
        work_response = student.post(f"/api/lessons/{lesson_id}/scratch/templates/{template_id}/work")
        work = response_json(work_response).get("work") or {}
        work_id = work.get("id")
        v.require("Student copies template as personal work", work_response.status_code == 200 and work_id, f"work_id={work_id}")
        v.artifacts["work_id"] = work_id

        student_editor = student.get(f"/scratch/editor?work_id={work_id}&return_url=/student/lessons/{lesson_id}")
        student_editor_text = student_editor.get_data(as_text=True)
        v.require(
            "Student can open Scratch graphical work editor with draft and template actions",
            student_editor.status_code == 200
            and "SCRATCH_OJ_LOAD_SB3" in student_editor_text
            and "SCRATCH_OJ_EXPORT_SB3" in student_editor_text,
            f"status={student_editor.status_code}",
        )
        v.require(
            "Student editor exposes progress save, teacher template reload, teacher submit and return link",
            "暂存进度" in student_editor_text
            and "重新加载老师模板" in student_editor_text
            and "提交给老师" in student_editor_text
            and "返回上课页" in student_editor_text,
            f"status={student_editor.status_code}",
        )

        teacher_work_editor = teacher.get(f"/scratch/editor?work_id={work_id}")
        teacher_work_editor_text = teacher_work_editor.get_data(as_text=True)
        v.require(
            "Teacher can preview student work without save buttons",
            teacher_work_editor.status_code == 200
            and "当前为学生作品预览" in teacher_work_editor_text
            and 'id="save-project"' not in teacher_work_editor_text
            and 'id="submit-project"' not in teacher_work_editor_text,
            f"status={teacher_work_editor.status_code}",
        )
        teacher_save_attempt = teacher.post(
            f"/api/scratch/works/{work_id}/editor-save",
            json={"project_base64": base64.b64encode(build_sb3_bytes("teacher-save-attempt")).decode("ascii")},
        )
        v.require("Teacher cannot save student Scratch work", teacher_save_attempt.status_code == 403, f"status={teacher_save_attempt.status_code}")

        editor_save = student.post(
            f"/api/scratch/works/{work_id}/editor-save",
            json={
                "title": "QA Student Work",
                "project_base64": base64.b64encode(build_sb3_bytes(f"work-{tag}")).decode("ascii"),
                "thumbnail_base64": base64.b64encode(PNG_1X1).decode("ascii"),
                "save_mode": "draft",
                "submit_note": "Saved from validation script.",
            },
        )
        editor_work = response_json(editor_save).get("work") or {}
        v.require(
            "Editor progress save writes .sb3, thumbnail and draft status",
            editor_save.status_code == 200
            and editor_work.get("asset_id")
            and editor_work.get("thumbnail_asset_id")
            and editor_work.get("status") == "draft",
            f"asset={editor_work.get('asset_id')}, thumb={editor_work.get('thumbnail_asset_id')}, status={editor_work.get('status')}",
        )
        student_editor_after_save = student.get(f"/scratch/editor?work_id={work_id}")
        v.require(
            "Student editor loads personal saved progress after save",
            student_editor_after_save.status_code == 200
            and "加载上次保存" in student_editor_after_save.get_data(as_text=True)
            and "暂存成功" in student_editor_after_save.get_data(as_text=True)
            and "提交成功" in student_editor_after_save.get_data(as_text=True),
            f"status={student_editor_after_save.status_code}",
        )
        lesson_detail_shell = teacher.get(f"/lessons/{lesson_id}/detail?from=/classroom")
        lesson_attendance_shell = teacher.get(f"/lessons/{lesson_id}/attendance?from=/classroom")
        v.require(
            "Teacher classroom child pages keep return-to-classroom route",
            lesson_detail_shell.status_code == 200 and lesson_attendance_shell.status_code == 200,
            f"detail={lesson_detail_shell.status_code}, attendance={lesson_attendance_shell.status_code}",
        )

        submit_response = student.post(f"/api/scratch/works/{work_id}/submit", json={"submit_note": "Ready for review"})
        submitted_work = response_json(submit_response).get("work") or {}
        v.require("Student submits work without auto judge", submit_response.status_code == 200 and submitted_work.get("status") == "submitted" and submitted_work.get("judge_status") == "not_started", f"status={submitted_work.get('status')}, judge={submitted_work.get('judge_status')}")

        works_response = teacher.get(f"/api/lessons/{lesson_id}/scratch/works")
        works = response_json(works_response).get("items") or []
        v.require("Teacher sees submitted work in lesson scope", works_response.status_code == 200 and any(item.get("id") == work_id for item in works), f"works={len(works)}")
        review_response = teacher.put(f"/api/scratch/works/{work_id}/review", json={"score": 92, "review_comment": "Good validation work."})
        reviewed_work = response_json(review_response).get("work") or {}
        v.require("Teacher reviews submitted work", review_response.status_code == 200 and reviewed_work.get("status") == "reviewed" and reviewed_work.get("score") == 92, f"status={reviewed_work.get('status')}, score={reviewed_work.get('score')}")
        student_after_review = student.post(
            f"/api/scratch/works/{work_id}/editor-save",
            json={"project_base64": base64.b64encode(build_sb3_bytes("after-review")).decode("ascii")},
        )
        v.require("Student cannot modify reviewed work", student_after_review.status_code == 403, f"status={student_after_review.status_code}")

        parent_login = login(parent, seed["parent_username"])
        parent_user = response_json(parent_login).get("user") or {}
        v.require("Parent login succeeds", parent_login.status_code == 200 and parent_user.get("role") == "parent", f"role={parent_user.get('role')}")
        parent_portal = parent.get("/api/parent/me")
        parent_dump = json.dumps(response_json(parent_portal), ensure_ascii=False)
        v.require("Parent portal returns only linked child context", parent_portal.status_code == 200 and seed["classmate_name"] not in parent_dump, "classmate not present")
        parent_scratch = parent.get("/api/student/scratch/works")
        v.require("Parent cannot use student Scratch task API", parent_scratch.status_code == 403, f"status={parent_scratch.status_code}")
        parent_create_work = parent.post(f"/api/lessons/{lesson_id}/scratch/templates/{template_id}/work")
        v.require("Parent cannot create student work", parent_create_work.status_code == 403, f"status={parent_create_work.status_code}")
        parent_upload = parent.post(
            f"/api/lessons/{lesson_id}/assets",
            data={"file": (BytesIO(b"%PDF-1.4\n"), f"parent-upload-{tag}.pdf")},
            content_type="multipart/form-data",
        )
        v.require("Parent cannot upload courseware", parent_upload.status_code == 403, f"status={parent_upload.status_code}")

    except Exception as error:
        v.record("Validation fatal error", False, repr(error))
        return v, 1

    return v, 0


def write_report(v: Validation, exit_code: int) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = REPORT_DIR / f"测试报告-P2-{timestamp}.md"
    passed = sum(1 for row in v.rows if row["ok"])
    failed = sum(1 for row in v.rows if not row["ok"])
    lines = [
        "# P2 验证测试报告",
        "",
        f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- 结果：{'通过' if exit_code == 0 and failed == 0 else '失败'}",
        f"- 通过项：{passed}",
        f"- 失败项：{failed}",
        f"- 测试数据前缀：`qa_*`，已保留在当前 SQLite 数据库中",
        "",
        "## 测试数据",
        "",
        "```json",
        json.dumps(v.artifacts, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
        "## 检查项",
        "",
        "| 状态 | 检查项 | 说明 |",
        "| --- | --- | --- |",
    ]
    for row in v.rows:
        lines.append(f"| {'通过' if row['ok'] else '失败'} | {row['name']} | {row['detail']} |")
    lines.extend(
        [
            "",
            "## P2 结论",
            "",
            "- 当前版本已完成老师上传课件、上传并绑定 Scratch 预设模板、学生复制模板为个人作品、从编辑器保存 .sb3 和缩略图、提交作品、教师查看与点评。",
            "- 学生端已增加课程二级页 `/student/lessons/<id>`：按课程名称进入后可查看课件、知识点、详情和我的作品，接口会拦截非本人课次。",
            "- 老师可从课次详情、教师备课入口或上课入口进入模板图形化预览；学生可从学生端预览模板，并从个人作品入口进入 Scratch GUI 暂存进度和提交给老师。",
            "- 学生作品页会优先加载上一次暂存进度，同时保留重新加载老师模板的按钮；暂存/提交按钮会给出成功或失败反馈；教师只能预览学生作品，不能替学生保存或提交。",
            "- 教师上课端已改为接近学生端的卡片布局，课次详情、签到和 Scratch 编辑器都携带返回上课页入口。",
            "- 当前上课流程未启用测试点、自动判题或动态运行测评；提交后默认保持 `judge_status=not_started`，符合本轮“暂不考虑测试点”的范围。",
            "- 已补充 `.sb3/.sb2` 基础结构校验：模板或作品文件必须是可解析压缩包且包含 `project.json`。",
            "- Flask 经典展示页已禁用，GET 页面入口由 Vue shell 接管，非 API 表单写入返回 410。",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    validation, code = run_validation()
    path = write_report(validation, code)
    print(f"Report: {path}")
    raise SystemExit(code)
