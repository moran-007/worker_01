# P2 Scratch 课堂资源闭环实现记录

更新时间：2026-06-05

## 当前范围

本阶段课堂过程先收敛为两件事：

1. 老师在课次详情中上传本节课件。
2. 老师上传或绑定 Scratch 预设代码模板，学生从学生端开始模板、保存个人作品并提交，老师查看和点评。

测试点、自动判题、动态运行测评暂不进入当前上课流程。相关表和接口保留为未来扩展口，但默认不触发。

## 已实现内容

- 课次课件绑定：新增 `lesson_assets`，把 `uploaded_assets` 明确挂到某节课。
- 课件 API：
  - `GET /api/lessons/<lesson_id>/assets`
  - `POST /api/lessons/<lesson_id>/assets`
  - `DELETE /api/lessons/<lesson_id>/assets/<lesson_asset_id>`
- 课次详情 API：`GET /api/lessons/<lesson_id>/detail` 返回 `courseware_assets`、`scratch_assignments`、`scratch_works`、`scratch_templates`。
- 老师端 Vue 课次详情：
  - 上传本节课件。
  - 上传或绑定 `.sb3/.sb2` Scratch 预设模板。
  - 查看学生作品并保存点评。
  - 移除课件或模板绑定。
- 学生端：
  - 显示“我的课件”，只列出本人所在班级课次关联的课件。
  - 显示 Scratch 课堂作品入口。
  - 支持从模板开始、打开 Scratch 编辑器、保存 `.sb3` 和缩略图、提交作品。
- 权限隔离：
  - 老师只能管理自己课次范围内的资源。
  - 学生只能查看和下载自己班级课次关联的课件和模板。
  - 学生作品访问继续按 `student_id` 校验。
- 提交流程：
  - 无测评配置时，提交后 `judge_status` 保持 `not_started`。
  - 不会自动进入测评或手动复核状态。

## 关键文件清单

- 后端路由与业务：`app.py`
- 数据库结构与迁移：`database.py`
- 权限矩阵：`permissions.py`
- 老师端课次详情：`frontend/src/views/LessonDetailView.vue`
- 前端 API：`frontend/src/api/http.js`
- 前端样式：`frontend/src/styles/app.css`
- 学生端页面：`templates/student_portal.html`
- Scratch 编辑器桥接页：`templates/scratch_editor.html`

## 已验证

- `python -m py_compile app.py database.py permissions.py config.py`
- `npm run build`
- 端到端接口验证：
  - 老师上传课件。
  - 老师上传 Scratch 预设模板。
  - 学生只看到本人课次关联课件并可下载。
  - 学生开始模板、从编辑器保存 `.sb3` 和缩略图、提交作品。
  - 提交后不触发测评。
  - 老师查看作品并保存点评。
- 运行入口均返回 `200`：
  - 主后端：`http://127.0.0.1:8000`
  - 主 Vue：`http://127.0.0.1:5173`
  - OJ_text 后端：`http://127.0.0.1:3000`
  - OJ_text 前端：`http://127.0.0.1:5174`
  - Scratch GUI：`http://127.0.0.1:8601`

## 后续预留

- 未来需要测评时，可复用当前保留的 `scratch_judge_runs`、`judge_config_json`、`test_point_spec_json` 和 `/api/scratch/test-points/generate`。
- 动态运行类测评建议后续再接 `scratch_oj` worker 或本地 Scratch runtime，不影响当前课件与模板闭环。
