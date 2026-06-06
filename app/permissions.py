from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping


PERMISSION_CATALOG = OrderedDict(
    [
        ("dashboard.view", ("工作台查看", "查看首页统计、今日课次和提醒。", "基础")),
        ("students.view", ("学生查看", "查看学生档案、课时和历史记录。", "学生")),
        ("students.manage", ("学生管理", "新增、编辑、停用学生。", "学生")),
        ("teachers.view", ("教师查看", "查看教师资料和授课统计。", "教师")),
        ("teachers.manage", ("教师管理", "新增、编辑、停用教师。", "教师")),
        ("classes.view", ("班级查看", "查看班级资料和学生名单。", "班级")),
        ("classes.manage", ("班级管理", "新增、编辑、归档班级。", "班级")),
        ("class_roster.manage", ("班级名单管理", "维护班级学生加入和移出。", "班级")),
        ("lesson_types.view", ("课程类型查看", "查看课程类型和默认课时。", "课程")),
        ("lesson_types.manage", ("课程类型管理", "新增、编辑课程类型。", "课程")),
        ("course_presets.view", ("预设课程查看", "查看预设课程体系。", "课程")),
        ("course_presets.manage", ("预设课程管理", "新增、编辑、导入预设课程。", "课程")),
        ("lessons.view", ("课次查看", "查看课次和排课记录。", "课次")),
        ("lessons.manage", ("课次管理", "新增、取消单节课次。", "课次")),
        ("lessons.generate", ("批量排课", "按班级批量生成计划课次。", "课次")),
        ("attendance.view", ("签到查看", "查看班级签到记录。", "签到")),
        ("attendance.manage", ("签到管理", "保存签到状态和扣课时。", "签到")),
        ("attendance.export", ("签到导出", "导出单节课签到表。", "签到")),
        ("lesson_detail.view", ("课程详情查看", "查看课程详情、作业和下节安排。", "课程详情")),
        ("lesson_detail.manage", ("课程详情管理", "填写和更新课程详情。", "课程详情")),
        ("statistics.view", ("统计查看", "查看课时、到课和教师统计。", "统计")),
        ("statistics.export", ("统计导出", "导出统计明细。", "统计")),
        ("users.manage", ("账号权限管理", "创建账号、停用账号、分配角色。", "系统")),
        ("permissions.assign", ("权限分配", "分配角色和维护权限体系。", "系统")),
        ("logs.view", ("日志查看", "查看系统关键操作记录。", "系统")),
        ("logs.export", ("日志导出", "导出系统操作日志。", "系统")),
        ("database.view", ("数据库关系查看", "查看数据库表、视图和外键关系。", "系统")),
        ("backups.view", ("备份查看", "查看数据库备份列表。", "系统")),
        ("backups.create", ("备份创建", "创建数据库备份。", "系统")),
        ("backups.download", ("备份下载", "下载数据库备份文件。", "系统")),
        ("backups.restore", ("备份恢复", "从备份恢复数据库。", "系统")),
        ("student_portal.view", ("学生端查看", "查看学生自己的课程、任务、作品和学习记录。", "学生端")),
        ("student_portal.hours.view", ("学生端课时查看", "允许学生端查看本人购买、消耗和剩余课时。", "学生端")),
        ("parent_portal.view", ("家长端查看", "查看家长账号关联学生的课程、课时和学习报告。", "家长端")),
        ("scratch.templates.view", ("Scratch 模板查看", "查看课次绑定的 Scratch 模板作品。", "Scratch")),
        ("scratch.templates.manage", ("Scratch 模板管理", "导入、编辑、绑定 Scratch 模板作品。", "Scratch")),
        ("scratch.works.view", ("Scratch 作品查看", "查看学生 Scratch 作品。", "Scratch")),
        ("scratch.works.manage", ("Scratch 作品管理", "保存、提交、点评和归档 Scratch 作品。", "Scratch")),
        ("scratch.works.review", ("Scratch 作品审核", "审核、推荐和发布学生 Scratch 作品。", "Scratch")),
        ("scratch.materials.view", ("Scratch 素材查看", "查看 Scratch 背景、角色、造型、声音素材。", "Scratch")),
        ("scratch.materials.manage", ("Scratch 素材管理", "上传、审核、启停和维护 Scratch 素材。", "Scratch")),
        ("uploads.manage", ("上传资源管理", "上传课件、素材、模板作品并维护文件状态。", "资源")),
        ("integrations.manage", ("外部系统集成", "维护 Hydro 等外部系统账号绑定和集成配置。", "系统")),
    ]
)

ROLE_LABELS = OrderedDict(
    [
        ("super_admin", "超级管理员"),
        ("principal", "校长"),
        ("academic_manager", "学管师"),
        ("admin_office", "行政"),
        ("teacher", "教师"),
        ("student", "学生"),
        ("parent", "家长"),
        ("readonly", "只读账号"),
        ("admin", "超级管理员（旧账号）"),
        ("staff", "学管师（旧账号）"),
    ]
)

ROLE_ALIASES = {
    "admin": "super_admin",
    "staff": "academic_manager",
}

ASSIGNABLE_ROLES = (
    "super_admin",
    "principal",
    "academic_manager",
    "admin_office",
    "teacher",
    "student",
    "parent",
    "readonly",
)

ROLE_LEVELS = {
    "super_admin": 100,
    "principal": 80,
    "academic_manager": 60,
    "admin_office": 50,
    "teacher": 30,
    "student": 20,
    "parent": 20,
    "readonly": 10,
}

ROLE_NOTES = {
    "super_admin": "系统最高权限，负责账号、角色、备份恢复和权限分配。",
    "principal": "校区负责人，拥有校区业务管理、统计和日志查看权限，不直接分配系统权限。",
    "academic_manager": "学管师，负责学生、班级、排课、签到和课程资料维护。",
    "admin_office": "行政，负责学生基础资料、班级名单、签到协助和统计导出。",
    "teacher": "教师，默认按关联教师范围查看和维护自己的课次、签到、课程详情。",
    "student": "学生，默认只能查看自己的课程、任务、作品和学习记录。",
    "parent": "家长，默认只能查看账号关联学生的课程、课时、排课和学习报告。",
    "readonly": "只读账号，仅查看常用业务数据，不能新增、编辑、导入或删除。",
}

PLANNED_ROLES = OrderedDict(
    [
        (
            "headquarter",
            {
                "label": "总部",
                "level": 90,
                "note": "预留跨校区监管、经营统计、总部审计和制度配置权限，后续多校区模块落地后启用。",
            },
        ),
        (
            "finance",
            {
                "label": "财务",
                "level": 55,
                "note": "预留收款、退费、课消核算、财务导出等权限，等待财务模块完善。",
            },
        ),
        (
            "sales",
            {
                "label": "课程顾问",
                "level": 40,
                "note": "预留线索、试听、转化跟进等权限，等待招生/CRM 模块完善。",
            },
        ),
    ]
)

SUPER_ADMIN_PERMISSIONS = tuple(PERMISSION_CATALOG.keys())

ROLE_PERMISSIONS = {
    "super_admin": SUPER_ADMIN_PERMISSIONS,
    "principal": (
        "dashboard.view",
        "students.view",
        "students.manage",
        "teachers.view",
        "teachers.manage",
        "classes.view",
        "classes.manage",
        "class_roster.manage",
        "lesson_types.view",
        "lesson_types.manage",
        "course_presets.view",
        "course_presets.manage",
        "lessons.view",
        "lessons.manage",
        "lessons.generate",
        "attendance.view",
        "attendance.manage",
        "attendance.export",
        "lesson_detail.view",
        "lesson_detail.manage",
        "statistics.view",
        "statistics.export",
        "logs.view",
        "logs.export",
        "backups.view",
        "backups.create",
        "backups.download",
        "scratch.templates.view",
        "scratch.templates.manage",
        "scratch.works.view",
        "scratch.works.manage",
        "scratch.works.review",
        "scratch.materials.view",
        "scratch.materials.manage",
        "uploads.manage",
        "integrations.manage",
    ),
    "academic_manager": (
        "dashboard.view",
        "students.view",
        "students.manage",
        "teachers.view",
        "classes.view",
        "classes.manage",
        "class_roster.manage",
        "lesson_types.view",
        "course_presets.view",
        "course_presets.manage",
        "lessons.view",
        "lessons.manage",
        "lessons.generate",
        "attendance.view",
        "attendance.manage",
        "attendance.export",
        "lesson_detail.view",
        "lesson_detail.manage",
        "statistics.view",
        "statistics.export",
        "scratch.templates.view",
        "scratch.templates.manage",
        "scratch.works.view",
        "scratch.works.review",
        "scratch.materials.view",
        "scratch.materials.manage",
        "uploads.manage",
    ),
    "admin_office": (
        "dashboard.view",
        "students.view",
        "students.manage",
        "teachers.view",
        "classes.view",
        "class_roster.manage",
        "lesson_types.view",
        "course_presets.view",
        "lessons.view",
        "attendance.view",
        "attendance.manage",
        "attendance.export",
        "lesson_detail.view",
        "statistics.view",
        "statistics.export",
        "scratch.templates.view",
        "scratch.templates.manage",
        "scratch.works.view",
        "scratch.works.review",
        "scratch.materials.view",
        "scratch.materials.manage",
        "uploads.manage",
    ),
    "teacher": (
        "dashboard.view",
        "students.view",
        "teachers.view",
        "classes.view",
        "lesson_types.view",
        "course_presets.view",
        "lessons.view",
        "attendance.view",
        "attendance.manage",
        "attendance.export",
        "lesson_detail.view",
        "lesson_detail.manage",
        "statistics.view",
        "statistics.export",
        "scratch.templates.view",
        "scratch.templates.manage",
        "scratch.works.view",
        "scratch.works.review",
        "scratch.materials.view",
        "uploads.manage",
    ),
    "student": (
        "student_portal.view",
        "scratch.templates.view",
        "scratch.works.view",
        "scratch.works.manage",
        "scratch.materials.view",
    ),
    "parent": (
        "parent_portal.view",
    ),
    "readonly": (
        "dashboard.view",
        "students.view",
        "teachers.view",
        "classes.view",
        "lesson_types.view",
        "course_presets.view",
        "lessons.view",
        "attendance.view",
        "lesson_detail.view",
        "statistics.view",
    ),
}
ROLE_PERMISSIONS["admin"] = ROLE_PERMISSIONS["super_admin"]
ROLE_PERMISSIONS["staff"] = ROLE_PERMISSIONS["academic_manager"]

LEGACY_ROLE_GROUPS = {
    "admin": {"admin", "super_admin"},
    "staff": {"staff", "academic_manager", "admin_office", "principal"},
    "teacher": {"teacher"},
    "readonly": {"readonly"},
}

ENDPOINT_PERMISSIONS = {
    "dashboard": "dashboard.view",
    "api_dashboard": "dashboard.view",
    "students": {"GET": "students.view", "POST": "students.manage"},
    "student_history": "students.view",
    "edit_student": "students.manage",
    "deactivate_student": "students.manage",
    "api_students": "students.view",
    "api_create_student": "students.manage",
    "api_update_student": "students.manage",
    "api_deactivate_student": "students.manage",
    "teachers": {"GET": "teachers.view", "POST": "teachers.manage"},
    "edit_teacher": "teachers.manage",
    "deactivate_teacher": "teachers.manage",
    "api_teachers": "teachers.view",
    "api_create_teacher": "teachers.manage",
    "api_update_teacher": "teachers.manage",
    "api_deactivate_teacher": "teachers.manage",
    "classes": {"GET": "classes.view", "POST": "classes.manage"},
    "edit_class": "classes.manage",
    "archive_class": "classes.manage",
    "class_students": {"GET": "classes.view", "POST": "class_roster.manage"},
    "remove_class_student": "class_roster.manage",
    "api_classes": "classes.view",
    "api_create_class": "classes.manage",
    "api_update_class": "classes.manage",
    "api_archive_class": "classes.manage",
    "api_class_students": "classes.view",
    "api_add_class_student": "class_roster.manage",
    "api_remove_class_student": "class_roster.manage",
    "lesson_types": {"GET": "lesson_types.view", "POST": "lesson_types.manage"},
    "edit_lesson_type": "lesson_types.manage",
    "api_lesson_types": "lesson_types.view",
    "api_create_lesson_type": "lesson_types.manage",
    "api_update_lesson_type": "lesson_types.manage",
    "course_presets": {"GET": "course_presets.view", "POST": "course_presets.manage"},
    "edit_course_preset": "course_presets.manage",
    "download_course_preset_template": "course_presets.manage",
    "import_course_presets": "course_presets.manage",
    "api_course_presets": "course_presets.view",
    "api_download_course_preset_template": "course_presets.manage",
    "api_create_course_preset": "course_presets.manage",
    "api_update_course_preset": "course_presets.manage",
    "api_import_course_presets": "course_presets.manage",
    "lessons": {"GET": "lessons.view", "POST": "lessons.manage"},
    "edit_lesson": "lessons.manage",
    "cancel_lesson": "lessons.manage",
    "generate_lessons": "lessons.generate",
    "api_lessons": "lessons.view",
    "api_create_lesson": "lessons.manage",
    "api_cancel_lesson": "lessons.manage",
    "api_generate_class_lessons": "lessons.generate",
    "attendance": {"GET": "attendance.view", "POST": "attendance.manage"},
    "export_lesson_attendance": "attendance.export",
    "api_lesson_attendance": "attendance.view",
    "api_save_attendance": "attendance.manage",
    "lesson_detail": {"GET": "lesson_detail.view", "POST": "lesson_detail.manage"},
    "api_lesson_detail": "lesson_detail.view",
    "api_save_lesson_detail": "lesson_detail.manage",
    "statistics": "statistics.view",
    "export_attendance": "statistics.export",
    "api_statistics": "statistics.view",
    "users": "users.manage",
    "edit_user": "users.manage",
    "api_users": "users.manage",
    "api_create_user": "users.manage",
    "api_update_user": "users.manage",
    "api_permissions": "permissions.assign",
    "api_upsert_permission": "permissions.assign",
    "api_update_role_permissions": "permissions.assign",
    "permission_matrix": "permissions.assign",
    "create_role": "permissions.assign",
    "update_role": "permissions.assign",
    "api_create_role": "permissions.assign",
    "api_update_role": "permissions.assign",
    "student_portal": "student_portal.view",
    "api_student_me": "student_portal.view",
    "api_student_lesson_detail": "student_portal.view",
    "student_start_scratch_task": "scratch.works.manage",
    "student_portal_preview": "students.view",
    "api_student_portal": "students.view",
    "parent_portal": "parent_portal.view",
    "api_parent_me": "parent_portal.view",
    "parent_portal_preview": "students.view",
    "api_parent_portal": "students.view",
    "api_uploaded_assets": "uploads.manage",
    "api_upload_asset": "uploads.manage",
    "api_lesson_assets": "lesson_detail.view",
    "api_upload_lesson_asset": "uploads.manage",
    "api_delete_lesson_asset": "uploads.manage",
    "api_download_asset": ("uploads.manage", "scratch.templates.view", "scratch.works.view", "scratch.materials.view"),
    "api_scratch_editor_config": "scratch.works.view",
    "scratch_editor": "scratch.works.view",
    "api_scratch_templates": "scratch.templates.view",
    "api_create_scratch_template": "scratch.templates.manage",
    "api_update_scratch_template": "scratch.templates.manage",
    "api_lesson_scratch_templates": "scratch.templates.view",
    "api_bind_lesson_scratch_template": "scratch.templates.manage",
    "api_create_lesson_scratch_assignment": "scratch.templates.manage",
    "api_update_lesson_scratch_assignment": "scratch.templates.manage",
    "api_unbind_lesson_scratch_template": "scratch.templates.manage",
    "api_lesson_scratch_works": "scratch.works.view",
    "api_student_scratch_works": "scratch.works.view",
    "api_create_scratch_work": "scratch.works.manage",
    "api_save_scratch_work": "scratch.works.manage",
    "api_editor_save_scratch_work": "scratch.works.manage",
    "api_submit_scratch_work": "scratch.works.manage",
    "api_scratch_work_judge_runs": "scratch.works.view",
    "api_run_scratch_work_judge": "scratch.works.review",
    "api_review_scratch_work": "scratch.works.review",
    "api_generate_scratch_test_points": "scratch.templates.manage",
    "api_scratch_material_categories": "scratch.materials.view",
    "api_scratch_materials": "scratch.materials.view",
    "api_external_account_bindings": "integrations.manage",
    "api_upsert_external_account_binding": "integrations.manage",
    "logs": "logs.view",
    "export_logs": "logs.export",
    "api_logs": "logs.view",
    "api_export_logs": "logs.export",
    "api_database_meta": "database.view",
    "backups": "backups.view",
    "create_backup": "backups.create",
    "download_backup": "backups.download",
    "restore_backup": "backups.restore",
}


def normalize_role(role: str | None) -> str:
    return ROLE_ALIASES.get(role or "", role or "")


def role_label(role: str | None) -> str:
    value = role or ""
    return ROLE_LABELS.get(value) or ROLE_LABELS.get(normalize_role(value), value)


def _subject_role(subject) -> str:
    if isinstance(subject, str):
        return subject
    if subject is None:
        return ""
    try:
        return subject["role"]
    except (KeyError, TypeError, IndexError):
        return getattr(subject, "role", "")


def permissions_for_role(role: str | None) -> tuple[str, ...]:
    return tuple(ROLE_PERMISSIONS.get(normalize_role(role), ()))


def _subject_permissions(subject) -> tuple[str, ...] | None:
    if isinstance(subject, str) or subject is None:
        return None
    try:
        permissions = subject["permissions"]
    except (KeyError, TypeError, IndexError):
        permissions = getattr(subject, "permissions", None)
    if permissions is None:
        return None
    if isinstance(permissions, str):
        return tuple(part.strip() for part in permissions.split(",") if part.strip())
    return tuple(permissions)


def has_permission(subject, permission: str) -> bool:
    subject_permissions = _subject_permissions(subject)
    if subject_permissions is not None:
        return permission in subject_permissions
    return permission in permissions_for_role(_subject_role(subject))


def has_any_permission(subject, permissions) -> bool:
    if isinstance(permissions, str):
        permissions = (permissions,)
    return any(has_permission(subject, permission) for permission in permissions)


def has_all_permissions(subject, permissions) -> bool:
    if isinstance(permissions, str):
        permissions = (permissions,)
    return all(has_permission(subject, permission) for permission in permissions)


def matches_legacy_roles(subject, allowed_roles: tuple[str, ...]) -> bool:
    role = _subject_role(subject)
    role_key = normalize_role(role)
    for allowed in allowed_roles:
        if role == allowed or role_key == allowed:
            return True
        if role_key in LEGACY_ROLE_GROUPS.get(allowed, set()):
            return True
    return False


def endpoint_permissions(endpoint: str | None, method: str | None) -> tuple[str, ...]:
    if not endpoint:
        return ()
    spec = ENDPOINT_PERMISSIONS.get(endpoint)
    if spec is None:
        return ()
    if isinstance(spec, Mapping):
        spec = spec.get((method or "").upper()) or spec.get("*")
    if not spec:
        return ()
    if isinstance(spec, str):
        return (spec,)
    return tuple(spec)


def permission_catalog() -> list[dict]:
    return [
        {
            "key": key,
            "label": label,
            "description": description,
            "category": category,
        }
        for key, (label, description, category) in PERMISSION_CATALOG.items()
    ]


def role_options() -> list[dict]:
    return [
        {
            "value": role,
            "label": ROLE_LABELS[role],
            "level": ROLE_LEVELS[role],
            "note": ROLE_NOTES[role],
            "permissions": permissions_for_role(role),
        }
        for role in ASSIGNABLE_ROLES
    ]


def planned_role_options() -> list[dict]:
    return [{"value": key, **value} for key, value in PLANNED_ROLES.items()]
