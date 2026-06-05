# P2 Scratch 课堂资源闭环实现记录

更新时间：2026-06-05

## 当前范围

本阶段上课流程先收敛为两件事：

1. 老师在 Vue 课次详情中上传本节课件。
2. 老师上传或绑定 Scratch 预设代码模板，学生从学生端开始模板、保存个人作品并提交，老师查看和点评。

测试点、自动判题、动态运行测评暂不进入当前上课流程。相关表和接口保留为未来扩展口，但默认不触发。

## 已实现内容

- Vue 作为唯一前端入口：经典 Flask 展示模板已删除，GET 页面请求统一交给 Vue shell，非 API 表单写入返回 `410`。
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
- 学生端 Vue：
  - 显示“我的课件”，只列出本人所在班级课次关联的课件。
  - 显示上课、社区、积分、测试等入口布局。
  - 显示 Scratch 课堂作品入口。
  - 支持从模板开始、打开 Scratch 编辑器、保存 `.sb3` 和缩略图、提交作品。
- 家长端 Vue：
  - 只展示账号关联学生的班级、排课和学习记录。
  - 不展示同班其他学生姓名、联系方式、签到或课时数据。
- 文件校验：
  - `.sb3/.sb2` 模板和 GUI 保存作品必须是可解析压缩包。
  - 压缩包内必须包含有效 `project.json`。
- 权限隔离：
  - 老师只能管理自己课次范围内的资源和学生作品。
  - 学生只能查看和下载自己班级课次关联的课件和模板。
  - 学生作品访问继续按 `student_id` 校验。
  - 家长不能调用学生 Scratch 写入 API，不能上传课件。
- 提交流程：
  - 无测评配置时，提交后 `judge_status` 保持 `not_started`。
  - 不会自动进入测评或手动复核状态。

## 关键文件清单

- 后端路由与业务：`app.py`
- 数据库结构与迁移：`database.py`
- 权限矩阵：`permissions.py`
- 老师端课次详情：`frontend/src/views/LessonDetailView.vue`
- 学生端页面：`frontend/src/views/StudentPortalView.vue`
- 家长端页面：`frontend/src/views/ParentPortalView.vue`
- 前端路由守卫：`frontend/src/router/index.js`
- 前端 API：`frontend/src/api/http.js`
- 前端样式：`frontend/src/styles/app.css`
- Scratch 编辑器桥接页：`templates/scratch_editor.html`

## 已验证

自动验证脚本：`scripts/validate_p2_flow.py`

最新报告：`docs/测试报告-P2-20260605-233134.md`

通过项：

- Vue shell 接管 `/`、`/login`、`/student`、`/parent`、`/students`、`/students/1/edit`。
- 经典 Flask 表单 POST 被禁用。
- 管理员登录、退出登录、`/api/me` 校验通过。
- 超级管理员可新建自定义身份并动态分配权限。
- 老师上传课件。
- 老师上传无效 `.sb3` 被拒绝。
- 老师上传并绑定有效 Scratch 预设模板。
- 学生只看到本人相关上下文，不能看到同班其他学生。
- 学生不能查看学生列表或老师课次详情 API。
- 学生可下载本人相关课件。
- 学生可复制模板为个人作品。
- Scratch 编辑器保存接口可写入 `.sb3` 和缩略图。
- 学生提交后不触发自动判题，`judge_status=not_started`。
- 老师可查看提交作品并点评。
- 已点评作品学生不能继续修改。
- 家长只看到关联孩子上下文，不能调用学生 Scratch 写入 API，也不能上传课件。

验证命令：

```bash
python -m py_compile app.py database.py permissions.py config.py
npm run build
python scripts/validate_p2_flow.py
```

## 后续预留

- 未来需要测评时，可复用当前保留的 `scratch_judge_runs`、`judge_config_json`、`test_point_spec_json` 和 `/api/scratch/test-points/generate`。
- 动态运行类测评建议后续再接 `scratch_oj` worker 或本地 Scratch runtime，不影响当前课件与模板闭环。
- P3 素材库、作品发布、开源、点赞、收藏、优秀作品推荐目前只保留端口，不进入当前稳定主流程。
