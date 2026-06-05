PRAGMA foreign_keys = ON;

-- 1. 学生课时余额
SELECT
    student_id,
    student_name,
    class_names,
    total_hours,
    consumed_hours,
    remaining_hours,
    last_lesson_date
FROM v_students_summary
WHERE status = 'active'
ORDER BY remaining_hours ASC, student_name;

-- 2. 课时不足学生
SELECT
    student_id,
    student_name,
    parent_phone,
    class_names,
    remaining_hours
FROM v_students_summary
WHERE status = 'active'
  AND total_hours > 0
  AND remaining_hours <= 2
ORDER BY remaining_hours ASC;

-- 3. 指定日期课次详情
SELECT
    lesson_date,
    start_time,
    end_time,
    class_name,
    teacher_name,
    lesson_type_name,
    course_category,
    course_stage,
    course_lesson_no,
    preset_course_name,
    lesson_topic,
    expected_count,
    arrived_count,
    leave_count,
    absent_count,
    attendance_rate,
    has_lesson_detail,
    lesson_status
FROM v_lessons_detail
WHERE lesson_date = '2026-05-16'
ORDER BY start_time, class_name;

-- 4. 每节课课程详情
SELECT
    lesson_date,
    start_time,
    class_name,
    teacher_name,
    lesson_type_name,
    course_category,
    course_stage,
    course_lesson_no,
    preset_course_name,
    lesson_topic,
    teaching_content,
    learning_goal,
    class_performance,
    homework,
    next_plan,
    updated_by,
    updated_at
FROM v_lesson_details
WHERE lesson_date BETWEEN '2026-05-01' AND '2026-05-31'
ORDER BY lesson_date, start_time, class_name;

-- 5. 指定日期范围签到明细
SELECT
    lesson_date,
    start_time,
    class_name,
    teacher_name,
    lesson_type_name,
    course_category,
    course_stage,
    course_lesson_no,
    preset_course_name,
    student_name,
    attendance_status,
    deduct_hours,
    checkin_time,
    attendance_remark
FROM v_attendance_detail
WHERE lesson_date BETWEEN '2026-05-01' AND '2026-05-31'
ORDER BY lesson_date, start_time, class_name, student_name;

-- 6. 按老师统计授课
SELECT
    teacher_id,
    teacher_name,
    lesson_count,
    lesson_hours,
    expected_students,
    arrived_students,
    deduct_hours
FROM v_teacher_lesson_summary
ORDER BY lesson_hours DESC;

-- 7. 按班级统计课次和出勤
SELECT
    class_id,
    class_name,
    active_student_count,
    lesson_count,
    lesson_hours,
    arrived_students,
    leave_students,
    absent_students,
    deduct_hours
FROM v_class_lesson_summary
ORDER BY class_name;

-- 8. 学生月度统计
SELECT
    month,
    student_name,
    attendance_records,
    arrived_count,
    leave_count,
    absent_count,
    late_count,
    trial_count,
    deduct_hours
FROM v_student_monthly_attendance
WHERE month = '2026-05'
ORDER BY student_name;

-- 9. 班级花名册
SELECT
    class_name,
    student_name,
    parent_phone,
    join_date,
    roster_status,
    student_status
FROM v_class_roster
WHERE class_id = 1
ORDER BY student_name;
