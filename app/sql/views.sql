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
