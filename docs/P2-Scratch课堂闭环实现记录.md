# P2 Scratch 课堂闭环实现记录

日期：2026-06-05  
实现目录：`E:\moran_project\worker_01\app`

## 1. 当前结论

P2 当前已经完成“课件 + Scratch 预设模板 + 学生作品提交 + 教师点评”的课堂闭环。

本轮按照最新需求收敛范围：上课过程老师只需要上传课件和预设代码模板，暂时不考虑测试点、动态测评和自动判题。后端仍保留测评相关字段和接口，未来可接 `scratch_oj` 或 `hydro_scratch`，但当前默认不触发。

## 2. 已完成模块

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| Vue 唯一入口 | 已完成 | 经典 Flask 展示模板已删除，GET 页面统一返回 Vue shell，非 API 表单写入返回 `410`。 |
| 登录跳转修复 | 已完成 | 学生和家长跳转严格按 `role` 判断，超级管理员不会再因拥有全权限被误判为学生端。 |
| 动态权限 | 已完成 | 超级管理员可新增自定义身份，并手动控制该身份是否拥有某个权限点。 |
| 老师上传课件 | 已完成 | 课件写入 `uploaded_assets`，并通过 `lesson_assets` 绑定到具体课次。 |
| Scratch 模板上传 | 已完成 | 支持 `.sb3/.sb2` 模板上传、缩略图、课次绑定和解绑。 |
| Scratch 文件校验 | 已完成 | `.sb3/.sb2` 必须可解析且包含有效 `project.json`。 |
| 学生作品闭环 | 已完成 | 学生复制模板为个人作品，支持从编辑器保存 `.sb3` 和缩略图并提交。 |
| 教师点评 | 已完成 | 教师可查看本人课次下的学生作品，保存评分和点评。 |
| 学生端 Vue | 已完成 | 只展示本人课程、课件、Scratch 任务和作品状态，预留社区、积分、测试入口。 |
| 家长端 Vue | 已完成 | 只展示关联孩子的班级、排课和学习记录，不展示同班其他学生。 |
| 数据范围 helper | 已完成 | `current_access_scope` 统一支撑教师、学生、家长的数据范围校验。 |
| P3 端口 | 已预留 | Scratch 素材分类、素材列表、作品社区方向保留表和查询入口。 |

## 3. 关键接口

| 接口 | 用途 |
| --- | --- |
| `POST /api/auth/login` | 账号登录。 |
| `POST /api/auth/logout` | 退出登录。 |
| `GET /api/student/me` | 学生端本人数据。 |
| `GET /api/parent/me` | 家长端关联孩子数据。 |
| `GET /api/lessons/<lesson_id>/detail` | 课次详情，包含课件、模板、作品。 |
| `POST /api/lessons/<lesson_id>/assets` | 老师上传课件。 |
| `DELETE /api/lessons/<lesson_id>/assets/<lesson_asset_id>` | 移除课件绑定。 |
| `POST /api/lessons/<lesson_id>/scratch/assignments` | 上传或绑定 Scratch 预设模板。 |
| `PUT /api/lessons/<lesson_id>/scratch/templates/<template_id>/assignment` | 更新模板作业说明。 |
| `DELETE /api/lessons/<lesson_id>/scratch/templates/<template_id>` | 解绑课次模板。 |
| `GET /api/student/scratch/works` | 学生查看本人 Scratch 课堂任务。 |
| `POST /api/lessons/<lesson_id>/scratch/templates/<template_id>/work` | 学生复制模板为个人作品。 |
| `POST /api/scratch/works/<work_id>/editor-save` | Scratch GUI 保存 `.sb3` 和缩略图。 |
| `POST /api/scratch/works/<work_id>/submit` | 学生提交作品。 |
| `PUT /api/scratch/works/<work_id>/review` | 教师点评作品。 |

## 4. 权限与数据范围

- 超级管理员：拥有完整权限，可维护身份和权限矩阵。
- 教师：默认可上传课件、上传/绑定模板、查看并点评本人课次下的作品。
- 学生：只能查看本人相关课程、课件、Scratch 任务和作品；不能查看学生列表、老师课次详情 API 或同班其他学生信息。
- 家长：只能查看账号关联孩子的数据；不能创建学生作品、不能上传课件、不能调用学生 Scratch 写入 API。
- 学生课时：当前默认不向学生展示；如果后续超级管理员给学生身份分配 `student_portal.hours.view`，则由权限矩阵显式控制。

## 5. 验证结果

自动验证脚本：`scripts/validate_p2_flow.py`

最新测试报告：`docs/测试报告-P2-20260606-094057.md`

本轮自动验证共 39 项，全部通过。覆盖内容包括：

- Vue shell 接管旧页面入口。
- Flask 经典表单入口禁用。
- 登录、退出登录、管理员不误跳学生端。
- 自定义身份创建与权限分配。
- 老师上传课件。
- 无效 `.sb3` 被拒绝。
- 有效 `.sb3` 上传并绑定课次。
- 学生查看本人数据、下载本人课件、复制模板、保存作品、提交作品。
- 老师查看并点评作品。
- 学生不能修改已点评作品。
- 老师不能访问其他老师课次。
- 学生和家长均不能看到同班其他学生。
- 家长不能调用学生写入类接口。

## 6. 本地启动

已新增一键启动脚本：

```bat
restart_all_services.bat
```

脚本会先关闭占用端口，再启动：

| 服务 | 地址 |
| --- | --- |
| 主系统 Flask/API | `http://127.0.0.1:8000/` |
| 主系统 Vue dev server | `http://127.0.0.1:5173/login` |
| OJ_text Backend | `http://127.0.0.1:3000/health` |
| OJ_text Frontend | `http://127.0.0.1:5174/` |
| Scratch GUI | `http://127.0.0.1:8601/` |

日志目录：`runtime_logs`

## 7. 后续建议

- 后续若恢复测试点能力，再接入 `scratch_oj` 的测评规则、测试点生成、自动判题和手动复核。
- P3 素材库和作品社区只保留端口，等 P2 稳定后再实现素材上传、审核、启停、作品发布、开源、点赞、收藏和优秀作品推荐。
