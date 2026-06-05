# Vue3 + Element Plus 前端说明

> 更新时间：2026-05-16
>
> 前端目录：`E:\moran_project\class_worker\frontend`
>
> 后端地址：`http://127.0.0.1:8000`
>
> 前端地址：`http://127.0.0.1:5173`

------

## 一、当前定位

这是课时签到系统的新一代模块化前端，采用 Vue3 + Element Plus 实现。

当前 Vue 前端已经覆盖主要日常操作，原 Flask 模板页面仍保留可用，作为稳定兜底版本。

------

## 二、技术栈

```text
Vue 3
Vite
Vue Router
Element Plus
Fetch API
```

------

## 三、已完成页面

| 页面 | 路由 | 说明 |
|---|---|---|
| 登录页 | `/login` | 账号登录 |
| 首页工作台 | `/` | 今日课程、课时提醒、未来课程 |
| 学生管理 | `/students` | 学生列表、新增、编辑、课时余额展示 |
| 教师管理 | `/teachers` | 教师列表、新增、编辑 |
| 班级管理 | `/classes` | 班级列表、新增、编辑、维护班级学生、进入批量排课 |
| 课程类型 | `/lesson-types` | 课程类型列表、新增、编辑 |
| 预设课程 | `/course-presets` | 维护课程大类、阶段、节次和具体课程名称，支持批量导入和模板下载 |
| 课次管理 | `/lessons` | 按日期查看课次、新增/取消课次，按大类、阶段、内容/标题选择预设课程 |
| 批量排课 | `/lessons/generate` | 按班级、日期范围、星期和预设课程批量生成课次 |
| 课程详情 | `/lessons/:id/detail` | 记录本节课内容、教学目标、课堂表现、作业、下节安排 |
| 签到页面 | `/lessons/:id/attendance` | 一键全员已到、逐个修改状态、保存签到 |
| 统计导出 | `/statistics` | 日期范围统计、出勤率柱状图、老师课时图、明细查看、Excel 导出入口 |
| 账号权限 | `/users` | 账号列表、新增、编辑、角色和教师关联；顶部支持当前用户自助修改密码 |
| 操作日志 | `/logs` | 日志筛选、列表和 Excel 导出 |
| 数据库关系 | `/database` | 数据库表、视图、外键关系展示 |

------

## 四、后端 API

前端通过 `/api` 访问 Flask 后端，Vite 已在 `vite.config.js` 中配置代理。

主要接口：

```text
/api/auth/login
/api/auth/logout
/api/me
/api/me/password
/api/dashboard
/api/students
/api/teachers
/api/classes
/api/classes/<id>/students
/api/classes/<id>/lessons/generate
/api/lesson-types
/api/course-presets
/api/course-presets/import
/api/course-presets/import-template
/api/lessons
/api/lessons/<id>/cancel
/api/lessons/<id>/detail
/api/lessons/<id>/attendance
/api/statistics
/api/users
/api/logs
/api/logs/export
/api/database/meta
```

表单校验已覆盖主要弹窗和筛选表单：必填项、手机号、课时数、班级日期范围、上课时间范围，以及老师账号必须关联教师。危险操作会先弹窗确认，例如停用、归档、移出学生、取消课次和批量生成课次。

未登录访问 API 会返回 JSON 401。

------

## 五、启动方式

先启动 Flask 后端：

```powershell
cd E:\moran_project\class_worker
py -3.11 app.py
```

再启动 Vue 前端：

```powershell
cd E:\moran_project\class_worker\frontend
npm run dev
```

也可以在项目根目录运行：

```powershell
.\start_frontend.ps1
```

浏览器访问：

```text
http://127.0.0.1:5173
```

默认账号：

```text
admin / admin123
```

------

## 六、构建验证

```powershell
cd E:\moran_project\class_worker\frontend
npm run build
```

打包产物：

```text
frontend/dist
```

------

## 七、后续前端优化建议

1. 补全表单必填校验和错误提示。
2. 增加删除、停用、归档等危险操作确认弹窗。
3. 增加批量生成课次页面。
4. 增加统计图表，例如出勤率柱状图、老师课时图。
5. 增加操作日志 Excel 导出。
6. 将经典 Flask 模板页逐步降级为备用入口。
