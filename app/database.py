import re
import sqlite3
from datetime import datetime

from flask import current_app, g
from werkzeug.security import generate_password_hash

from permissions import PERMISSION_CATALOG, ROLE_LEVELS, ROLE_NOTES, ROLE_PERMISSIONS, role_label, normalize_role

try:
    import mysql.connector
    from mysql.connector import errorcode
except ImportError:  # pragma: no cover - optional dependency for SQLite mode.
    mysql = None
    errorcode = None
else:
    mysql = mysql.connector

DatabaseIntegrityError = (sqlite3.IntegrityError,)
if mysql is not None:
    DatabaseIntegrityError = (sqlite3.IntegrityError, mysql.errors.IntegrityError)


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    phone TEXT,
    parent_name TEXT,
    parent_phone TEXT,
    school TEXT,
    purchased_hours REAL NOT NULL DEFAULT 0,
    gift_hours REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    remark TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    subject TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    remark TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lesson_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    default_hours REAL NOT NULL DEFAULT 1,
    count_in_statistics INTEGER NOT NULL DEFAULT 1,
    remark TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS course_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    stage TEXT NOT NULL,
    lesson_no INTEGER NOT NULL,
    course_name TEXT NOT NULL,
    lesson_type_id INTEGER,
    default_hours REAL NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'active',
    remark TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (category, stage, lesson_no, course_name),
    FOREIGN KEY (lesson_type_id) REFERENCES lesson_types(id)
);

CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    course_name TEXT,
    class_type TEXT,
    teacher_id INTEGER,
    default_weekday INTEGER,
    default_start_time TEXT,
    default_end_time TEXT,
    capacity INTEGER,
    start_date TEXT,
    end_date TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    remark TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);

CREATE TABLE IF NOT EXISTS class_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    join_date TEXT,
    leave_date TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    UNIQUE (class_id, student_id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    lesson_date TEXT NOT NULL,
    weekday INTEGER,
    start_time TEXT,
    end_time TEXT,
    teacher_id INTEGER,
    lesson_type_id INTEGER,
    course_preset_id INTEGER,
    lesson_topic TEXT,
    lesson_hours REAL NOT NULL DEFAULT 1,
    classroom TEXT,
    status TEXT NOT NULL DEFAULT 'planned',
    remark TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
    FOREIGN KEY (lesson_type_id) REFERENCES lesson_types(id),
    FOREIGN KEY (course_preset_id) REFERENCES course_presets(id)
);

CREATE TABLE IF NOT EXISTS lesson_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL UNIQUE,
    teaching_content TEXT,
    learning_goal TEXT,
    class_performance TEXT,
    homework TEXT,
    next_plan TEXT,
    materials TEXT,
    updated_by TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT '未确认',
    checkin_time TEXT,
    deduct_hours REAL NOT NULL DEFAULT 0,
    operator TEXT,
    remark TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (lesson_id, student_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);
CREATE INDEX IF NOT EXISTS idx_teachers_status ON teachers(status);
CREATE INDEX IF NOT EXISTS idx_course_presets_lookup ON course_presets(category, stage, lesson_no);
CREATE INDEX IF NOT EXISTS idx_course_presets_status ON course_presets(status);
CREATE INDEX IF NOT EXISTS idx_classes_status ON classes(status);
CREATE INDEX IF NOT EXISTS idx_lessons_date ON lessons(lesson_date);
CREATE INDEX IF NOT EXISTS idx_lessons_class ON lessons(class_id);
CREATE INDEX IF NOT EXISTS idx_lessons_teacher_date ON lessons(teacher_id, lesson_date);
CREATE INDEX IF NOT EXISTS idx_lessons_type ON lessons(lesson_type_id);
CREATE INDEX IF NOT EXISTS idx_lessons_status_date ON lessons(status, lesson_date);
CREATE INDEX IF NOT EXISTS idx_lesson_details_lesson ON lesson_details(lesson_id);
CREATE INDEX IF NOT EXISTS idx_attendance_lesson ON attendance(lesson_id);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);
CREATE INDEX IF NOT EXISTS idx_class_students_class_status ON class_students(class_id, status);
CREATE INDEX IF NOT EXISTS idx_class_students_student_status ON class_students(student_id, status);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'staff',
    status TEXT NOT NULL DEFAULT 'active',
    teacher_id INTEGER,
    student_id INTEGER,
    remark TEXT,
    last_login_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    role TEXT,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id INTEGER,
    detail TEXT,
    ip_address TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role_status ON users(role, status);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at);

CREATE TABLE IF NOT EXISTS permission_definitions (
    permission_key TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT '未分类',
    is_system INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS role_definitions (
    role_code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 10,
    note TEXT,
    is_system INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permission_assignments (
    role_code TEXT NOT NULL,
    permission_key TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (role_code, permission_key),
    FOREIGN KEY (permission_key) REFERENCES permission_definitions(permission_key)
);

CREATE TABLE IF NOT EXISTS system_migrations (
    migration_key TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS external_account_bindings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    external_user_id TEXT NOT NULL,
    external_username TEXT,
    display_name TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (provider, external_user_id),
    UNIQUE (user_id, provider),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS uploaded_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER,
    asset_type TEXT NOT NULL,
    usage_scope TEXT NOT NULL DEFAULT 'courseware',
    original_filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    public_path TEXT,
    mime_type TEXT,
    file_size INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'uploaded',
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (owner_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS lesson_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    title TEXT,
    note TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_by INTEGER,
    created_at TEXT NOT NULL,
    UNIQUE (lesson_id, asset_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES uploaded_assets(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS scratch_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    asset_id INTEGER,
    thumbnail_asset_id INTEGER,
    source_type TEXT NOT NULL DEFAULT 'uploaded',
    editor_url TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_by INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES uploaded_assets(id),
    FOREIGN KEY (thumbnail_asset_id) REFERENCES uploaded_assets(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS lesson_scratch_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    assignment_title TEXT,
    statement_md TEXT,
    bind_note TEXT,
    due_at TEXT,
    judge_config_json TEXT,
    test_point_spec_json TEXT,
    auto_judge INTEGER NOT NULL DEFAULT 0,
    max_score REAL NOT NULL DEFAULT 100,
    published_at TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_by INTEGER,
    created_at TEXT NOT NULL,
    UNIQUE (lesson_id, template_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES scratch_templates(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS scratch_works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER,
    template_id INTEGER,
    student_id INTEGER NOT NULL,
    owner_user_id INTEGER,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    asset_id INTEGER,
    thumbnail_asset_id INTEGER,
    editor_url TEXT,
    submit_note TEXT,
    review_comment TEXT,
    score REAL,
    judge_status TEXT NOT NULL DEFAULT 'not_started',
    judge_score REAL,
    judge_detail_json TEXT,
    visibility TEXT NOT NULL DEFAULT 'private',
    is_featured INTEGER NOT NULL DEFAULT 0,
    published_at TEXT,
    like_count INTEGER NOT NULL DEFAULT 0,
    favorite_count INTEGER NOT NULL DEFAULT 0,
    reviewed_by INTEGER,
    submitted_at TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (lesson_id, template_id, student_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
    FOREIGN KEY (template_id) REFERENCES scratch_templates(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (owner_user_id) REFERENCES users(id),
    FOREIGN KEY (asset_id) REFERENCES uploaded_assets(id),
    FOREIGN KEY (thumbnail_asset_id) REFERENCES uploaded_assets(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS scratch_judge_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER NOT NULL,
    lesson_id INTEGER,
    template_id INTEGER,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    total_score REAL NOT NULL DEFAULT 0,
    max_score REAL NOT NULL DEFAULT 100,
    passed INTEGER NOT NULL DEFAULT 0,
    detail_json TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (work_id) REFERENCES scratch_works(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
    FOREIGN KEY (template_id) REFERENCES scratch_templates(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS student_points_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    points INTEGER NOT NULL DEFAULT 0,
    reason TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (student_id, source_type, source_id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS scratch_material_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scratch_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    asset_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    material_type TEXT NOT NULL DEFAULT 'asset',
    audit_status TEXT NOT NULL DEFAULT 'pending',
    status TEXT NOT NULL DEFAULT 'active',
    created_by INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES scratch_material_categories(id),
    FOREIGN KEY (asset_id) REFERENCES uploaded_assets(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_permission_definitions_status ON permission_definitions(status);
CREATE INDEX IF NOT EXISTS idx_role_definitions_status ON role_definitions(status);
CREATE INDEX IF NOT EXISTS idx_role_permission_role ON role_permission_assignments(role_code);
CREATE INDEX IF NOT EXISTS idx_external_bindings_user ON external_account_bindings(user_id);
CREATE INDEX IF NOT EXISTS idx_external_bindings_provider ON external_account_bindings(provider, external_user_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_assets_scope ON uploaded_assets(usage_scope, asset_type, status);
CREATE INDEX IF NOT EXISTS idx_lesson_assets_lesson ON lesson_assets(lesson_id, status);
CREATE INDEX IF NOT EXISTS idx_scratch_templates_status ON scratch_templates(status);
CREATE INDEX IF NOT EXISTS idx_lesson_scratch_templates_lesson ON lesson_scratch_templates(lesson_id, status);
CREATE INDEX IF NOT EXISTS idx_scratch_works_student ON scratch_works(student_id, status);
CREATE INDEX IF NOT EXISTS idx_scratch_works_lesson ON scratch_works(lesson_id, status);
CREATE INDEX IF NOT EXISTS idx_scratch_judge_runs_work ON scratch_judge_runs(work_id, created_at);
CREATE INDEX IF NOT EXISTS idx_student_points_student ON student_points_ledger(student_id, created_at);
CREATE INDEX IF NOT EXISTS idx_scratch_materials_category ON scratch_materials(category_id, status);
"""


VIEWS_SCHEMA = """
PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS v_student_monthly_attendance;
DROP VIEW IF EXISTS v_class_lesson_summary;
DROP VIEW IF EXISTS v_teacher_lesson_summary;
DROP VIEW IF EXISTS v_attendance_detail;
DROP VIEW IF EXISTS v_lesson_details;
DROP VIEW IF EXISTS v_lessons_detail;
DROP VIEW IF EXISTS v_class_roster;
DROP VIEW IF EXISTS v_students_summary;

CREATE VIEW v_students_summary AS
SELECT
    s.id AS student_id,
    s.name AS student_name,
    s.gender,
    s.age,
    s.phone,
    s.parent_name,
    s.parent_phone,
    s.school,
    s.status,
    s.purchased_hours,
    s.gift_hours,
    (s.purchased_hours + s.gift_hours) AS total_hours,
    COALESCE(att.consumed_hours, 0) AS consumed_hours,
    (s.purchased_hours + s.gift_hours - COALESCE(att.consumed_hours, 0)) AS remaining_hours,
    COALESCE(att.attendance_count, 0) AS attendance_count,
    COALESCE(att.arrived_count, 0) AS arrived_count,
    COALESCE(att.leave_count, 0) AS leave_count,
    COALESCE(att.absent_count, 0) AS absent_count,
    att.last_lesson_date,
    COALESCE(cls.class_names, '') AS class_names,
    s.remark,
    s.created_at
FROM students s
LEFT JOIN (
    SELECT
        a.student_id,
        SUM(a.deduct_hours) AS consumed_hours,
        COUNT(*) AS attendance_count,
        SUM(CASE WHEN a.status IN ('已到', '迟到', '补签', '试听') THEN 1 ELSE 0 END) AS arrived_count,
        SUM(CASE WHEN a.status = '请假' THEN 1 ELSE 0 END) AS leave_count,
        SUM(CASE WHEN a.status = '缺勤' THEN 1 ELSE 0 END) AS absent_count,
        MAX(l.lesson_date) AS last_lesson_date
    FROM attendance a
    JOIN lessons l ON l.id = a.lesson_id
    GROUP BY a.student_id
) att ON att.student_id = s.id
LEFT JOIN (
    SELECT
        cs.student_id,
        GROUP_CONCAT(c.class_name, '、') AS class_names
    FROM class_students cs
    JOIN classes c ON c.id = cs.class_id
    WHERE cs.status = 'active'
    GROUP BY cs.student_id
) cls ON cls.student_id = s.id;

CREATE VIEW v_class_roster AS
SELECT
    cs.id AS roster_id,
    cs.class_id,
    c.class_name,
    c.course_name,
    c.class_type,
    c.teacher_id AS default_teacher_id,
    t.name AS default_teacher_name,
    cs.student_id,
    s.name AS student_name,
    s.phone AS student_phone,
    s.parent_name,
    s.parent_phone,
    s.school,
    cs.join_date,
    cs.leave_date,
    cs.status AS roster_status,
    s.status AS student_status
FROM class_students cs
JOIN classes c ON c.id = cs.class_id
JOIN students s ON s.id = cs.student_id
LEFT JOIN teachers t ON t.id = c.teacher_id;

CREATE VIEW v_lessons_detail AS
SELECT
    l.id AS lesson_id,
    l.class_id,
    c.class_name,
    c.course_name,
    c.class_type,
    l.lesson_date,
    l.weekday,
    l.start_time,
    l.end_time,
    l.teacher_id,
    t.name AS teacher_name,
    l.lesson_type_id,
    lt.type_name AS lesson_type_name,
    lt.count_in_statistics,
    l.course_preset_id,
    cp.category AS course_category,
    cp.stage AS course_stage,
    cp.lesson_no AS course_lesson_no,
    cp.course_name AS preset_course_name,
    l.lesson_topic,
    l.lesson_hours,
    l.classroom,
    l.status AS lesson_status,
    l.remark,
    l.created_at,
    CASE WHEN ld.id IS NULL THEN 0 ELSE 1 END AS has_lesson_detail,
    ld.teaching_content,
    ld.learning_goal,
    ld.class_performance,
    ld.homework,
    ld.next_plan,
    ld.materials,
    ld.updated_by AS detail_updated_by,
    ld.updated_at AS detail_updated_at,
    COALESCE(roster.expected_count, 0) AS expected_count,
    COALESCE(att.arrived_count, 0) AS arrived_count,
    COALESCE(att.late_count, 0) AS late_count,
    COALESCE(att.leave_count, 0) AS leave_count,
    COALESCE(att.absent_count, 0) AS absent_count,
    COALESCE(att.trial_count, 0) AS trial_count,
    COALESCE(att.confirmed_count, 0) AS confirmed_count,
    COALESCE(att.deduct_hours, 0) AS deduct_hours,
    CASE
        WHEN COALESCE(roster.expected_count, 0) = 0 THEN 0
        ELSE ROUND(COALESCE(att.arrived_count, 0) * 100.0 / roster.expected_count, 1)
    END AS attendance_rate
FROM lessons l
JOIN classes c ON c.id = l.class_id
LEFT JOIN teachers t ON t.id = l.teacher_id
LEFT JOIN lesson_types lt ON lt.id = l.lesson_type_id
LEFT JOIN course_presets cp ON cp.id = l.course_preset_id
LEFT JOIN lesson_details ld ON ld.lesson_id = l.id
LEFT JOIN (
    SELECT
        cs.class_id,
        COUNT(*) AS expected_count
    FROM class_students cs
    JOIN students s ON s.id = cs.student_id
    WHERE cs.status = 'active' AND s.status = 'active'
    GROUP BY cs.class_id
) roster ON roster.class_id = l.class_id
LEFT JOIN (
    SELECT
        a.lesson_id,
        COUNT(*) AS confirmed_count,
        SUM(CASE WHEN a.status IN ('已到', '迟到', '补签', '试听') THEN 1 ELSE 0 END) AS arrived_count,
        SUM(CASE WHEN a.status = '迟到' THEN 1 ELSE 0 END) AS late_count,
        SUM(CASE WHEN a.status = '请假' THEN 1 ELSE 0 END) AS leave_count,
        SUM(CASE WHEN a.status = '缺勤' THEN 1 ELSE 0 END) AS absent_count,
        SUM(CASE WHEN a.status = '试听' THEN 1 ELSE 0 END) AS trial_count,
        SUM(a.deduct_hours) AS deduct_hours
    FROM attendance a
    GROUP BY a.lesson_id
) att ON att.lesson_id = l.id;

CREATE VIEW v_lesson_details AS
SELECT
    ld.id AS detail_id,
    ld.lesson_id,
    l.lesson_date,
    l.weekday,
    l.start_time,
    l.end_time,
    l.class_id,
    c.class_name,
    c.course_name,
    l.teacher_id,
    t.name AS teacher_name,
    l.lesson_type_id,
    lt.type_name AS lesson_type_name,
    l.course_preset_id,
    cp.category AS course_category,
    cp.stage AS course_stage,
    cp.lesson_no AS course_lesson_no,
    cp.course_name AS preset_course_name,
    l.lesson_topic,
    l.lesson_hours,
    l.classroom,
    l.status AS lesson_status,
    ld.teaching_content,
    ld.learning_goal,
    ld.class_performance,
    ld.homework,
    ld.next_plan,
    ld.materials,
    ld.updated_by,
    ld.created_at,
    ld.updated_at
FROM lesson_details ld
JOIN lessons l ON l.id = ld.lesson_id
JOIN classes c ON c.id = l.class_id
LEFT JOIN teachers t ON t.id = l.teacher_id
LEFT JOIN lesson_types lt ON lt.id = l.lesson_type_id
LEFT JOIN course_presets cp ON cp.id = l.course_preset_id;

CREATE VIEW v_attendance_detail AS
SELECT
    a.id AS attendance_id,
    a.lesson_id,
    l.lesson_date,
    l.weekday,
    l.start_time,
    l.end_time,
    l.class_id,
    c.class_name,
    c.course_name,
    l.teacher_id,
    t.name AS teacher_name,
    l.lesson_type_id,
    lt.type_name AS lesson_type_name,
    l.course_preset_id,
    cp.category AS course_category,
    cp.stage AS course_stage,
    cp.lesson_no AS course_lesson_no,
    cp.course_name AS preset_course_name,
    l.lesson_topic,
    l.lesson_hours,
    l.classroom,
    l.status AS lesson_status,
    a.student_id,
    s.name AS student_name,
    s.phone AS student_phone,
    s.parent_name,
    s.parent_phone,
    s.school,
    a.status AS attendance_status,
    a.checkin_time,
    a.deduct_hours,
    a.operator,
    a.remark AS attendance_remark,
    a.created_at,
    a.updated_at
FROM attendance a
JOIN lessons l ON l.id = a.lesson_id
JOIN classes c ON c.id = l.class_id
JOIN students s ON s.id = a.student_id
LEFT JOIN teachers t ON t.id = l.teacher_id
LEFT JOIN lesson_types lt ON lt.id = l.lesson_type_id
LEFT JOIN course_presets cp ON cp.id = l.course_preset_id;

CREATE VIEW v_teacher_lesson_summary AS
SELECT
    t.id AS teacher_id,
    t.name AS teacher_name,
    t.phone,
    t.subject,
    t.status,
    COUNT(DISTINCT l.id) AS lesson_count,
    COALESCE(SUM(CASE WHEN l.status != 'cancelled' THEN l.lesson_hours ELSE 0 END), 0) AS lesson_hours,
    COALESCE(SUM(ld.expected_count), 0) AS expected_students,
    COALESCE(SUM(ld.arrived_count), 0) AS arrived_students,
    COALESCE(SUM(ld.deduct_hours), 0) AS deduct_hours
FROM teachers t
LEFT JOIN lessons l ON l.teacher_id = t.id
LEFT JOIN v_lessons_detail ld ON ld.lesson_id = l.id
GROUP BY t.id;

CREATE VIEW v_class_lesson_summary AS
SELECT
    c.id AS class_id,
    c.class_name,
    c.course_name,
    c.class_type,
    c.status,
    c.teacher_id AS default_teacher_id,
    t.name AS default_teacher_name,
    COUNT(DISTINCT CASE WHEN cs.status = 'active' THEN cs.student_id END) AS active_student_count,
    COUNT(DISTINCT l.id) AS lesson_count,
    COALESCE(SUM(CASE WHEN l.status != 'cancelled' THEN l.lesson_hours ELSE 0 END), 0) AS lesson_hours,
    COALESCE(SUM(ld.arrived_count), 0) AS arrived_students,
    COALESCE(SUM(ld.leave_count), 0) AS leave_students,
    COALESCE(SUM(ld.absent_count), 0) AS absent_students,
    COALESCE(SUM(ld.deduct_hours), 0) AS deduct_hours
FROM classes c
LEFT JOIN teachers t ON t.id = c.teacher_id
LEFT JOIN class_students cs ON cs.class_id = c.id
LEFT JOIN lessons l ON l.class_id = c.id
LEFT JOIN v_lessons_detail ld ON ld.lesson_id = l.id
GROUP BY c.id;

CREATE VIEW v_student_monthly_attendance AS
SELECT
    a.student_id,
    s.name AS student_name,
    SUBSTR(l.lesson_date, 1, 7) AS month,
    COUNT(*) AS attendance_records,
    SUM(CASE WHEN a.status IN ('已到', '迟到', '补签', '试听') THEN 1 ELSE 0 END) AS arrived_count,
    SUM(CASE WHEN a.status = '请假' THEN 1 ELSE 0 END) AS leave_count,
    SUM(CASE WHEN a.status = '缺勤' THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN a.status = '迟到' THEN 1 ELSE 0 END) AS late_count,
    SUM(CASE WHEN a.status = '试听' THEN 1 ELSE 0 END) AS trial_count,
    SUM(a.deduct_hours) AS deduct_hours
FROM attendance a
JOIN students s ON s.id = a.student_id
JOIN lessons l ON l.id = a.lesson_id
GROUP BY a.student_id, SUBSTR(l.lesson_date, 1, 7);
"""


DEFAULT_LESSON_TYPES = [
    ("常规课", 1, 1, "默认正式课程"),
    ("补课", 1, 1, "补课默认计入课时"),
    ("试听课", 0, 0, "试听默认不计入正式课时"),
    ("公开课", 0, 0, "公开课默认不计入课时"),
    ("一对一", 1, 1, "一对一课程可单独调整课时"),
    ("集训课", 1, 1, "集训课程"),
    ("比赛辅导课", 1, 1, "竞赛辅导"),
    ("机器人课", 1, 1, "机器人课程"),
    ("AI 启蒙课", 1, 1, "AI 启蒙课程"),
    ("测评课", 0, 0, "测评默认不计入课时"),
]

DEFAULT_COURSE_PRESETS = [
    ("Scratch", "入门阶段", 1, "角色移动与坐标", "常规课", 1, "认识舞台、角色和坐标移动"),
    ("Scratch", "入门阶段", 2, "循环与重复执行", "常规课", 1, "使用循环完成重复动作"),
    ("Scratch", "入门阶段", 3, "条件判断与互动", "常规课", 1, "使用如果/否则制作互动逻辑"),
    ("Scratch", "进阶阶段", 1, "变量与计分系统", "常规课", 1, "使用变量记录分数和状态"),
    ("Python", "入门阶段", 1, "输入输出与变量", "常规课", 1, "认识 print、input 和变量"),
    ("Python", "入门阶段", 2, "条件判断", "常规课", 1, "使用 if/elif/else 处理分支"),
    ("Python", "入门阶段", 3, "循环基础", "常规课", 1, "使用 for 和 while 处理重复任务"),
    ("C++", "入门阶段", 1, "变量与输入输出", "常规课", 1, "认识 cin、cout 和基础变量"),
    ("C++", "入门阶段", 2, "分支结构", "常规课", 1, "使用 if 和 switch 处理条件"),
    ("机器人", "基础阶段", 1, "电机控制", "常规课", 1, "认识电机和基础运动控制"),
]

DEFAULT_DEMO_TEACHERS = [
    ("teacher01", "张老师", "13810000001", "Scratch / Python"),
    ("teacher02", "李老师", "13810000002", "Python / C++"),
    ("teacher03", "王老师", "13810000003", "机器人 / AI"),
    ("teacher04", "赵老师", "13810000004", "Scratch / 机器人"),
]

DEFAULT_DEMO_CLASSES = [
    ("Scratch 启蒙 A 班", "Scratch", "小班课", "teacher01", 6, "09:00", "10:00", 10),
    ("Python 基础 B 班", "Python", "小班课", "teacher02", 7, "10:30", "11:30", 10),
    ("机器人创客 C 班", "机器人", "小班课", "teacher03", 6, "14:00", "15:00", 10),
    ("AI 编程 D 班", "AI 编程", "小班课", "teacher04", 7, "15:30", "16:30", 10),
]


MYSQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_$]+$")
SQLITE_UPSERT_RE = re.compile(
    r"\s+ON\s+CONFLICT\s*\((?P<columns>[^)]*)\)\s+DO\s+UPDATE\s+SET\s+(?P<updates>.*)\s*$",
    re.IGNORECASE | re.DOTALL,
)
SQLITE_DO_NOTHING_RE = re.compile(
    r"\s+ON\s+CONFLICT\s*\((?P<columns>[^)]*)\)\s+DO\s+NOTHING\s*$",
    re.IGNORECASE | re.DOTALL,
)
LONG_TEXT_COLUMNS = {
    "remark",
    "teaching_content",
    "learning_goal",
    "class_performance",
    "homework",
    "next_plan",
    "materials",
    "detail",
    "description",
    "statement_md",
    "judge_config_json",
    "test_point_spec_json",
    "judge_detail_json",
    "detail_json",
    "metadata_json",
    "storage_path",
    "public_path",
}


def database_engine() -> str:
    return str(current_app.config.get("DATABASE_ENGINE", "sqlite")).lower()


def is_mysql_enabled() -> bool:
    return database_engine() == "mysql"


def quote_mysql_identifier(identifier: str) -> str:
    if not MYSQL_IDENTIFIER_RE.match(identifier or ""):
        raise ValueError(f"Invalid MySQL identifier: {identifier!r}")
    return f"`{identifier}`"


def replace_qmark_placeholders(sql: str) -> str:
    output = []
    in_single = False
    in_double = False
    index = 0
    while index < len(sql):
        char = sql[index]
        if char == "'" and not in_double:
            output.append(char)
            if in_single and index + 1 < len(sql) and sql[index + 1] == "'":
                output.append(sql[index + 1])
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            output.append(char)
            if in_double and index + 1 < len(sql) and sql[index + 1] == '"':
                output.append(sql[index + 1])
                index += 2
                continue
            in_double = not in_double
        elif char == "?" and not in_single and not in_double:
            output.append("%s")
        else:
            output.append(char)
        index += 1
    return "".join(output)


def split_sql_script(script: str) -> list[str]:
    statements = []
    output = []
    in_single = False
    in_double = False
    index = 0
    while index < len(script):
        char = script[index]
        if char == "'" and not in_double:
            output.append(char)
            if in_single and index + 1 < len(script) and script[index + 1] == "'":
                output.append(script[index + 1])
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            output.append(char)
            if in_double and index + 1 < len(script) and script[index + 1] == '"':
                output.append(script[index + 1])
                index += 2
                continue
            in_double = not in_double
        elif char == ";" and not in_single and not in_double:
            statement = "".join(output).strip()
            if statement:
                statements.append(statement)
            output = []
        else:
            output.append(char)
        index += 1

    statement = "".join(output).strip()
    if statement:
        statements.append(statement)
    return statements


def translate_group_concat(sql: str) -> str:
    return re.sub(
        r"GROUP_CONCAT\(\s*([A-Za-z_][\w.]*?)\s*,\s*('(?:''|[^'])*')\s*\)",
        r"GROUP_CONCAT(\1 SEPARATOR \2)",
        sql,
        flags=re.IGNORECASE,
    )


def translate_sqlite_upsert(sql: str) -> str:
    match = SQLITE_DO_NOTHING_RE.search(sql)
    if match:
        return sql[: match.start()] + "\nON DUPLICATE KEY UPDATE id = id"

    match = SQLITE_UPSERT_RE.search(sql)
    if not match:
        return sql
    updates = match.group("updates").rstrip().rstrip(";")
    updates = re.sub(
        r"\bexcluded\.([A-Za-z_]\w*)\b",
        r"VALUES(\1)",
        updates,
        flags=re.IGNORECASE,
    )
    return sql[: match.start()] + "\nON DUPLICATE KEY UPDATE " + updates


def translate_create_table(sql: str) -> str:
    sql = re.sub(
        r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b",
        "INT AUTO_INCREMENT PRIMARY KEY",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(r"\bREAL\b", "DOUBLE", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bTEXT\b", "VARCHAR(255)", sql, flags=re.IGNORECASE)
    for column in LONG_TEXT_COLUMNS:
        sql = re.sub(
            rf"\b({column})\s+VARCHAR\(255\)",
            r"\1 TEXT",
            sql,
            flags=re.IGNORECASE,
        )
    if "ENGINE=" not in sql.upper():
        sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    return sql


def translate_mysql_sql(sql: str) -> str:
    statement = sql.strip()
    if not statement:
        return statement

    sql = translate_sqlite_upsert(sql)
    sql = re.sub(
        r"\bINSERT\s+OR\s+IGNORE\s+INTO\b",
        "INSERT IGNORE INTO",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r"\bCREATE\s+(UNIQUE\s+)?INDEX\s+IF\s+NOT\s+EXISTS\b",
        lambda match: "CREATE " + (match.group(1) or "") + "INDEX",
        sql,
        flags=re.IGNORECASE,
    )
    sql = translate_group_concat(sql)
    if statement.upper().startswith("CREATE TABLE"):
        sql = translate_create_table(sql)
    return replace_qmark_placeholders(sql)


def is_ignorable_mysql_ddl_error(sql: str, error) -> bool:
    errno = getattr(error, "errno", None)
    normalized = sql.lstrip().upper()
    return normalized.startswith("CREATE INDEX") and errno in {1060, 1061}


class StaticCursor:
    lastrowid = None
    rowcount = 0

    def __init__(self, rows=None):
        self._rows = rows or []

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)

    def __iter__(self):
        return iter(self._rows)


class MySQLConnection:
    is_mysql = True

    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql: str, params=()):
        statement = sql.strip()
        if statement.upper().startswith("PRAGMA "):
            return StaticCursor()
        translated = translate_mysql_sql(sql)
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(translated, params or ())
        except mysql.Error as exc:
            cursor.close()
            if is_ignorable_mysql_ddl_error(translated, exc):
                return StaticCursor()
            raise
        return cursor

    def executescript(self, script: str):
        for statement in split_sql_script(script):
            if statement.upper().startswith("PRAGMA "):
                continue
            cursor = self.execute(statement)
            close = getattr(cursor, "close", None)
            if close:
                close()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def mysql_connection_settings(include_database: bool = True) -> dict:
    if mysql is None:
        raise RuntimeError(
            "MySQL support requires mysql-connector-python. Install dependencies from requirements.txt."
        )
    config = current_app.config["MYSQL"]
    settings = {
        "host": config["host"],
        "port": config["port"],
        "user": config["user"],
        "password": config["password"],
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
        "use_unicode": True,
        "connection_timeout": 5,
    }
    if include_database:
        settings["database"] = config["database"]
    return settings


def create_mysql_database():
    database = current_app.config["MYSQL"]["database"]
    quoted_database = quote_mysql_identifier(database)
    connection = mysql.connect(**mysql_connection_settings(include_database=False))
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {quoted_database} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.close()
        connection.commit()
    finally:
        connection.close()


def open_mysql_connection():
    try:
        return mysql.connect(**mysql_connection_settings(include_database=True))
    except mysql.Error as exc:
        if errorcode is None or exc.errno != errorcode.ER_BAD_DB_ERROR:
            raise
        create_mysql_database()
        return mysql.connect(**mysql_connection_settings(include_database=True))


def get_db():
    if "db" not in g:
        if is_mysql_enabled():
            db = MySQLConnection(open_mysql_connection())
        else:
            db = sqlite3.connect(current_app.config["DATABASE"])
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def table_columns(db, table_name: str) -> set[str]:
    if getattr(db, "is_mysql", False):
        return {
            row["COLUMN_NAME"]
            for row in db.execute(
                """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                """,
                (current_app.config["MYSQL"]["database"], table_name),
            )
        }
    return {row["name"] for row in db.execute(f"PRAGMA table_info({table_name})")}


def ensure_schema_migrations(db):
    lesson_columns = table_columns(db, "lessons")
    user_columns = table_columns(db, "users")
    lesson_scratch_columns = table_columns(db, "lesson_scratch_templates")
    scratch_work_columns = table_columns(db, "scratch_works")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            title TEXT,
            note TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_by INTEGER,
            created_at TEXT NOT NULL,
            UNIQUE (lesson_id, asset_id),
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES uploaded_assets(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )
    if "course_preset_id" not in lesson_columns:
        db.execute("ALTER TABLE lessons ADD COLUMN course_preset_id INTEGER")
    if "student_id" not in user_columns:
        db.execute("ALTER TABLE users ADD COLUMN student_id INTEGER")
    lesson_scratch_new_columns = {
        "assignment_title": "TEXT",
        "statement_md": "TEXT",
        "due_at": "TEXT",
        "judge_config_json": "TEXT",
        "test_point_spec_json": "TEXT",
        "auto_judge": "INTEGER NOT NULL DEFAULT 0",
        "max_score": "REAL NOT NULL DEFAULT 100",
        "published_at": "TEXT",
    }
    for column, definition in lesson_scratch_new_columns.items():
        if column not in lesson_scratch_columns:
            db.execute(f"ALTER TABLE lesson_scratch_templates ADD COLUMN {column} {definition}")
    scratch_work_new_columns = {
        "judge_status": "TEXT NOT NULL DEFAULT 'not_started'",
        "judge_score": "REAL",
        "judge_detail_json": "TEXT",
        "visibility": "TEXT NOT NULL DEFAULT 'private'",
        "is_featured": "INTEGER NOT NULL DEFAULT 0",
        "published_at": "TEXT",
        "like_count": "INTEGER NOT NULL DEFAULT 0",
        "favorite_count": "INTEGER NOT NULL DEFAULT 0",
    }
    for column, definition in scratch_work_new_columns.items():
        if column not in scratch_work_columns:
            db.execute(f"ALTER TABLE scratch_works ADD COLUMN {column} {definition}")
    db.execute("CREATE INDEX IF NOT EXISTS idx_lessons_preset ON lessons(course_preset_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_users_student ON users(student_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_lesson_assets_lesson ON lesson_assets(lesson_id, status)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_scratch_judge_runs_work ON scratch_judge_runs(work_id, created_at)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_student_points_student ON student_points_ledger(student_id, created_at)")


def apply_permission_data_migrations(db, now: str):
    migrations = [
        (
            "20260605_teacher_scratch_classroom_defaults",
            "teacher",
            ("scratch.templates.manage", "scratch.works.review", "uploads.manage"),
        ),
        (
            "20260606_student_scratch_submit_defaults",
            "student",
            ("student_portal.view", "scratch.templates.view", "scratch.works.view", "scratch.works.manage"),
        ),
    ]
    for migration_key, role_code, permission_keys in migrations:
        applied = db.execute(
            "SELECT migration_key FROM system_migrations WHERE migration_key = ?",
            (migration_key,),
        ).fetchone()
        if applied:
            continue
        for permission_key in permission_keys:
            db.execute(
                """
                INSERT OR IGNORE INTO role_permission_assignments
                    (role_code, permission_key, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (role_code, permission_key, now, now),
            )
        db.execute(
            "INSERT OR IGNORE INTO system_migrations (migration_key, applied_at) VALUES (?, ?)",
            (migration_key, now),
        )


def seed_permission_tables(db, now: str):
    for raw_role, permissions in ROLE_PERMISSIONS.items():
        role_code = normalize_role(raw_role)
        if raw_role in {"admin", "staff"}:
            continue
        db.execute(
            """
            INSERT INTO role_definitions
                (role_code, label, level, note, is_system, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, 'active', ?, ?)
            ON CONFLICT(role_code) DO UPDATE SET
                label = excluded.label,
                level = excluded.level,
                note = excluded.note,
                is_system = 1,
                updated_at = excluded.updated_at
            """,
            (
                role_code,
                role_label(role_code),
                ROLE_LEVELS.get(role_code, 10),
                ROLE_NOTES.get(role_code, ""),
                now,
                now,
            ),
        )

    for permission_key, (label, description, category) in PERMISSION_CATALOG.items():
        db.execute(
            """
            INSERT INTO permission_definitions
                (permission_key, label, description, category, is_system, status,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, 'active', ?, ?)
            ON CONFLICT(permission_key) DO UPDATE SET
                label = excluded.label,
                description = excluded.description,
                category = excluded.category,
                is_system = 1,
                updated_at = excluded.updated_at
            """,
            (permission_key, label, description, category, now, now),
        )

    for raw_role, permissions in ROLE_PERMISSIONS.items():
        role_code = normalize_role(raw_role)
        if raw_role in {"admin", "staff"}:
            continue
        count_row = db.execute(
            "SELECT COUNT(*) AS count_value FROM role_permission_assignments WHERE role_code = ?",
            (role_code,),
        ).fetchone()
        has_existing_permissions = bool(count_row and count_row["count_value"])
        should_seed_role = role_code == "super_admin" or not has_existing_permissions
        if not should_seed_role:
            continue
        if role_code == "super_admin":
            db.execute(
                "DELETE FROM role_permission_assignments WHERE role_code = ?",
                (role_code,),
            )
        for permission_key in permissions:
            db.execute(
                """
                INSERT OR IGNORE INTO role_permission_assignments
                    (role_code, permission_key, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (role_code, permission_key, now, now),
            )
    apply_permission_data_migrations(db, now)


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    ensure_schema_migrations(db)
    db.executescript(VIEWS_SCHEMA)
    now = datetime.now().isoformat(timespec="seconds")
    seed_permission_tables(db, now)
    for type_name, default_hours, count_in_statistics, remark in DEFAULT_LESSON_TYPES:
        db.execute(
            """
            INSERT OR IGNORE INTO lesson_types
                (type_name, default_hours, count_in_statistics, remark, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (type_name, default_hours, count_in_statistics, remark, now),
        )
    lesson_type_ids = {
        row["type_name"]: row["id"] for row in db.execute("SELECT id, type_name FROM lesson_types")
    }
    for category, stage, lesson_no, course_name, type_name, default_hours, remark in DEFAULT_COURSE_PRESETS:
        db.execute(
            """
            INSERT OR IGNORE INTO course_presets
                (category, stage, lesson_no, course_name, lesson_type_id,
                 default_hours, status, remark, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?)
            """,
            (
                category,
                stage,
                lesson_no,
                course_name,
                lesson_type_ids.get(type_name),
                default_hours,
                remark,
                now,
            ),
        )
    admin_exists = db.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
    if admin_exists is None:
        db.execute(
            """
            INSERT INTO users
                (username, password_hash, display_name, role, status, remark, created_at)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
            """,
            (
                "admin",
                generate_password_hash("admin123"),
                "系统管理员",
                "super_admin",
                "系统默认管理员，请上线后尽快修改密码。",
                now,
            ),
        )
    demo_teacher_ids = {}
    for username, name, phone, subject in DEFAULT_DEMO_TEACHERS:
        teacher = db.execute(
            "SELECT id FROM teachers WHERE phone = ? OR name = ?",
            (phone, name),
        ).fetchone()
        if teacher is None:
            cursor = db.execute(
                """
                INSERT INTO teachers (name, phone, subject, status, remark, created_at)
                VALUES (?, ?, ?, 'active', ?, ?)
                """,
                (name, phone, subject, "系统初始化演示老师", now),
            )
            teacher_id = cursor.lastrowid
        else:
            teacher_id = teacher["id"]
        demo_teacher_ids[username] = teacher_id

        user_exists = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if user_exists is None:
            db.execute(
                """
                INSERT INTO users
                    (username, password_hash, display_name, role, status, teacher_id,
                     remark, created_at)
                VALUES (?, ?, ?, 'teacher', 'active', ?, ?, ?)
                """,
                (
                    username,
                    generate_password_hash("teacher123"),
                    name,
                    teacher_id,
                    "演示老师账号，默认密码 teacher123",
                    now,
                ),
            )
        else:
            db.execute(
                "UPDATE users SET role = 'teacher', teacher_id = ? WHERE username = ?",
                (teacher_id, username),
            )

    demo_class_ids = []
    for class_name, course_name, class_type, teacher_username, weekday, start_time, end_time, capacity in DEFAULT_DEMO_CLASSES:
        class_row = db.execute("SELECT id FROM classes WHERE class_name = ?", (class_name,)).fetchone()
        teacher_id = demo_teacher_ids.get(teacher_username)
        if class_row is None:
            cursor = db.execute(
                """
                INSERT INTO classes
                    (class_name, course_name, class_type, teacher_id, default_weekday,
                     default_start_time, default_end_time, capacity, start_date, end_date,
                     status, remark, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '', 'active', ?, ?)
                """,
                (
                    class_name,
                    course_name,
                    class_type,
                    teacher_id,
                    weekday,
                    start_time,
                    end_time,
                    capacity,
                    datetime.now().date().isoformat(),
                    "系统初始化演示班级",
                    now,
                ),
            )
            class_id = cursor.lastrowid
        else:
            class_id = class_row["id"]
            db.execute(
                """
                UPDATE classes
                SET teacher_id = ?, default_weekday = ?, default_start_time = ?,
                    default_end_time = ?, capacity = ?, status = 'active'
                WHERE id = ?
                """,
                (teacher_id, weekday, start_time, end_time, capacity, class_id),
            )
        demo_class_ids.append(class_id)

    for index in range(1, 31):
        name = f"模拟学员{index:02d}"
        parent_phone = f"13920{index:06d}"
        student = db.execute(
            "SELECT id FROM students WHERE parent_phone = ? OR name = ?",
            (parent_phone, name),
        ).fetchone()
        if student is None:
            cursor = db.execute(
                """
                INSERT INTO students
                    (name, gender, age, phone, parent_name, parent_phone, school,
                     purchased_hours, gift_hours, status, remark, created_at)
                VALUES (?, ?, ?, '', ?, ?, ?, ?, ?, 'active', ?, ?)
                """,
                (
                    name,
                    "男" if index % 2 else "女",
                    8 + (index % 6),
                    f"家长{index:02d}",
                    parent_phone,
                    f"演示小学{(index % 5) + 1}",
                    24,
                    2,
                    "系统初始化模拟学员",
                    now,
                ),
            )
            student_id = cursor.lastrowid
        else:
            student_id = student["id"]
        if demo_class_ids:
            class_id = demo_class_ids[(index - 1) % len(demo_class_ids)]
            db.execute(
                """
                INSERT INTO class_students (class_id, student_id, join_date, leave_date, status)
                VALUES (?, ?, ?, NULL, 'active')
                ON CONFLICT(class_id, student_id) DO UPDATE SET
                    leave_date = NULL,
                    status = 'active'
                """,
                (class_id, student_id, datetime.now().date().isoformat()),
            )
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    for path_key in (
        "DATA_DIR",
        "EXPORT_DIR",
        "BACKUP_DIR",
        "UPLOAD_DIR",
        "COURSEWARE_UPLOAD_DIR",
        "SCRATCH_UPLOAD_DIR",
        "MATERIAL_UPLOAD_DIR",
    ):
        app.config[path_key].mkdir(parents=True, exist_ok=True)
    with app.app_context():
        init_db()
