# 数据库 SQL 资产说明

> 更新时间：2026-05-16
>
> 数据库文件：`E:\moran_project\class_worker\data\attendance.db`

本目录用于给专业数据库软件和后续数据库迁移使用。

当前系统仍使用 SQLite 文件数据库：

```text
E:\moran_project\class_worker\data\attendance.db
```

推荐使用 DBeaver、SQLiteStudio、Navicat Premium 等工具直接连接该 `.db` 文件。

## 文件说明

| 文件 | 用途 |
|---|---|
| `views.sql` | 联表查询视图定义，和 `database.py` 中的 `VIEWS_SCHEMA` 保持一致 |
| `common_queries.sql` | 常用查询样例，可直接在数据库软件中执行 |
| `erd.md` | 表关系说明和 Mermaid ER 图 |

## 当前已提供视图

| 视图 | 作用 |
|---|---|
| `v_students_summary` | 学生课时余额、出勤统计、所在班级 |
| `v_class_roster` | 班级花名册 |
| `v_lessons_detail` | 课次详情、预设课程、课程详情状态和出勤汇总 |
| `v_lesson_details` | 每节课课程详情和预设课程 |
| `v_attendance_detail` | 签到明细 |
| `v_teacher_lesson_summary` | 教师授课汇总 |
| `v_class_lesson_summary` | 班级授课汇总 |
| `v_student_monthly_attendance` | 学生月度出勤汇总 |

## 使用建议

1. 日常业务修改仍建议通过系统页面完成，避免数据库软件直接改错数据。
2. 数据分析、核对、导出可以优先查询 `v_` 开头的视图。
3. 如果需要直接修改数据库，先在系统“数据备份”中创建备份。
4. SQLite 外键需要开启 `PRAGMA foreign_keys = ON;` 后才会强制生效。
5. 如果使用 DBeaver/Navicat/SQLiteStudio，可以直接打开 `attendance.db` 后查看 `Views`。

## 与系统代码的关系

这些 SQL 资产不是孤立文件：

1. `database.py` 中的 `SCHEMA` 负责建表和索引。
2. `database.py` 中的 `VIEWS_SCHEMA` 负责创建或刷新视图。
3. `views.sql` 是给数据库软件或迁移时使用的独立视图版本。
4. `common_queries.sql` 是后续排查、统计、导出的查询样例。
