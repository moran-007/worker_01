# P2 Scratch 课堂闭环实现记录

日期：2026-06-05  
实现目录：`E:\moran_project\worker_01\app`

## 1. 本轮已完成

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| Vue 管理端账号页 | 已完成 | 账号创建/编辑已同步 `student_id`，账号页内加入身份权限矩阵，可新增身份、动态勾选权限。 |
| 动态权限 | 已完成 | 超级管理员可手动控制任意身份的权限；教师默认补齐 Scratch 备课、上传和点评能力，且只做一次旧库迁移，后续可手动取消。 |
| 资源上传 API | 已完成 | 新增上传接口，文件写入 `uploaded_assets`，按 `usage_scope` 分目录保存。 |
| Scratch 模板作品 | 已完成 | 新增模板表，支持 `.sb3` 模板导入、缩略图、模板启停和编辑。 |
| 课次绑定模板 | 已完成 | 课次可绑定/解绑 Scratch 模板，学生端自动生成可开始任务。 |
| 学生作品闭环 | 已完成 | 学生复制模板为个人作品，支持保存 `.sb3`、缩略图、提交作品。 |
| 教师点评 | 已完成 | 教师可查看自己课次下的学生作品，并填写评分和点评。 |
| Scratch 编辑器接入 | 已完成基础接入 | 新增 `/scratch/editor` iframe 容器，配置指向本地 `OJ_text`/Scratch GUI 或后续 `hydro_scratch`。 |
| 数据范围 helper | 已完成 | 抽象 `current_access_scope`，统一支撑教师、学生、家长的数据范围校验。 |
| P3 预留 | 已完成端口 | 预留 Scratch 素材分类、素材列表、优秀作品/社区方向的数据表和查询接口。 |

## 2. 新增数据表

```txt
scratch_templates
lesson_scratch_templates
scratch_works
scratch_material_categories
scratch_materials
system_migrations
```

已有并接入：

```txt
uploaded_assets
external_account_bindings
permission_definitions
role_permission_assignments
```

## 3. 新增接口

| 接口 | 用途 |
| --- | --- |
| `GET /api/uploads/assets` | 查询上传资源，教师默认只看自己上传的资源。 |
| `POST /api/uploads/assets` | 上传课件、Scratch 模板、作品、缩略图、素材等资源。 |
| `GET /api/uploads/assets/<asset_id>/download` | 下载资源，按账号身份和绑定关系校验访问范围。 |
| `GET /api/scratch/editor/config` | 返回 Scratch/OJ/Hydro 编辑器集成配置。 |
| `GET /scratch/editor` | 本地 Scratch 编辑器 iframe 容器入口。 |
| `GET /api/scratch/templates` | 查询 Scratch 模板。 |
| `POST /api/scratch/templates` | 导入 Scratch 模板 `.sb3`。 |
| `PUT /api/scratch/templates/<template_id>` | 更新模板；教师只能更新自己创建的模板。 |
| `GET /api/lessons/<lesson_id>/scratch/templates` | 查询课次绑定模板。 |
| `POST /api/lessons/<lesson_id>/scratch/templates` | 给课次绑定模板。 |
| `DELETE /api/lessons/<lesson_id>/scratch/templates/<template_id>` | 取消课次模板绑定。 |
| `GET /api/lessons/<lesson_id>/scratch/works` | 教师/管理员查看课次学生作品。 |
| `GET /api/student/scratch/works` | 学生查看自己的 Scratch 课次任务和作品状态。 |
| `POST /api/lessons/<lesson_id>/scratch/templates/<template_id>/work` | 学生复制模板为个人作品。 |
| `PUT /api/scratch/works/<work_id>/save` | 学生保存作品文件、缩略图、提交说明。 |
| `POST /api/scratch/works/<work_id>/submit` | 学生提交作品。 |
| `PUT /api/scratch/works/<work_id>/review` | 教师点评作品。 |
| `GET /api/scratch/material-categories` | P3 素材分类预留。 |
| `GET /api/scratch/materials` | P3 素材库预留。 |

## 4. 权限与数据范围

新增/接入权限点：

```txt
uploads.manage
scratch.templates.view
scratch.templates.manage
scratch.works.view
scratch.works.manage
scratch.works.review
scratch.materials.view
scratch.materials.manage
```

默认策略：

- 超级管理员：全部权限强制完整。
- 教师：默认可上传资源、导入模板、绑定本人课次模板、查看本人课次作品、点评本人课次作品。
- 学生：只能查看自己绑定课次的 Scratch 任务，只能创建、保存、提交自己的作品。
- 家长：不开放学生 Scratch API；后续如接作品展示，需要按 `student_id` 做只读范围。
- 教师模板编辑：只能编辑自己创建的模板；管理员模板可被教师用于绑定课次，但不能被教师修改。
- 资源下载：管理员可全量访问；教师/学生只能访问自己上传的资源，或与自己可访问 Scratch 课次、模板、作品有关的资源。

## 5. Scratch 编辑器集成配置

配置项位于 `config.py`：

```txt
SCRATCH_EDITOR_URL
SCRATCH_OJ_API_URL
SCRATCH_EDITOR_PROJECT_DIR
HYDRO_INTEGRATION_MODE
HYDRO_BASE_URL
```

当前采用轻量本地集成策略：

- `/scratch/editor` 先以内嵌 iframe 承载本地 Scratch GUI。
- 默认编辑器 URL 为 `http://127.0.0.1:8601/`。
- OJ/Scratch API 默认预留 `http://127.0.0.1:3000/`。
- 后续接 `hydro_scratch` 时，可通过外部账号绑定表 `external_account_bindings` 做账号关联。

## 6. 页面变化

| 页面 | 变化 |
| --- | --- |
| Vue 账号页 | 增加 `student_id` 选择与动态权限矩阵。 |
| 学生端 `/student` | 新增 Scratch 任务卡片，显示课次、模板、状态、开始/打开入口。 |
| 课次详情页 | 新增 Scratch 课堂闭环区块，展示绑定模板和学生作品点评状态。 |
| `/scratch/editor` | 新增 Scratch 编辑器容器页。 |

## 7. 验证结果

已通过：

- `python -m py_compile app.py database.py permissions.py config.py`
- `npm run build`
- 管理员上传资源写入 `uploaded_assets`
- 管理员导入 `.sb3` 模板
- 管理员绑定模板到课次
- 学生端可看到绑定 Scratch 任务
- 学生复制模板为个人作品
- 学生保存 `.sb3` 作品和缩略图
- 学生提交作品
- 教师查看本人课次作品
- 教师点评并保存评分
- 学生不能给非本人班级课次创建作品
- 家长不能访问学生 Scratch API
- 学生不能修改已点评作品
- 教师不能修改管理员创建的模板

自动验证产生的本地数据：

```txt
lesson_id=13
out_lesson_id=14
asset_id=3
template_id=2
work_id=1
```

## 8. 后续建议

P2 后续可继续增强：

- Scratch 编辑器与保存接口做双向联动，直接从 GUI 保存 `.sb3` 和缩略图。
- 接入 `scratch_oj` 的测评规则、测试点生成、自动判题和手动复核。
- 在教师端 Vue 课次详情中加入模板上传、绑定、作品点评的完整操作 UI。
- 学生端加入社区、积分、测试入口的真实数据联动。

P3 建议保持当前预留表和接口，等 P2 稳定后再实现：

- Scratch 素材分类、上传、审核、启停。
- 作品发布、开源、点赞、收藏。
- 优秀作品推荐与社区展示。
