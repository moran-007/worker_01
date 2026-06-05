# moran-007 GitHub 深度扫描与平台优化技术文档

版本：v2.0  
日期：2026-06-05  
扫描对象：GitHub 公开账号 `moran-007`  
当前重点：Scratch 上课/备课、导入课件与模板作品、登录功能、管理员注册功能

补充说明：

- 已根据新增外部参考仓库 `yanhaogg0830/ScratchLite` 生成 v2.1 补充文档 `ScratchLite参考补充与平台方案优化技术文档.md`，用于吸收 ScratchLite 在默认作品、素材库、作品互动、批量账号和后台管理方面的产品经验。
- 已根据本地路径 `E:\moran_project` 生成 v2.2 补充文档 `本地素材库与worker系统资产整合技术文档.md`。其中 `worker`、`class_worker` 相关目录按系统类资产理解；结合本地扫描结果，`class_worker` 比 `ceshi003` 更适合作为当前教务/课次/签到/权限主系统候选，`ceshi003` 保留为 MySQL 设计和 API 文档参考。

## 1. 扫描结论

本次重新扫描 `moran-007` 公开 GitHub 后，可以把现有资产归纳为一条清晰的技术演进线：

```txt
早期网页/Java 实验
  ↓
Java + MyBatis 图书管理系统 code_yue
  ↓
Node.js + MySQL + Vue 课程管理系统 ceshi003
  ↓
独立 Scratch OJ 原型 OJ_text
  ↓
Hydro Scratch 插件 hydro_scratch
  ↓
Hydro 积分插件 hydro_points
```

因此，当前平台不建议重新从零做 Scratch 在线编辑器或积分系统。最稳的方向是：

```txt
ceshi003 作为课程/班级/课次/签到/课消/账号主系统
hydro_scratch 作为 Scratch 题目、模板、编辑器、提交、评分、自动测评引擎
hydro_points 作为 Hydro 侧积分、签到、商城、称号、结算插件
业务平台与 Hydro 之间通过账号绑定、任务绑定、跳转、回调、结果同步连接
```

核心优化判断：

- `hydro_scratch` 已经比 `OJ_text` 更成熟，Scratch 课堂功能应优先复用 `hydro_scratch`，不要继续维护独立 Scratch OJ 服务作为主线。
- `hydro_points` 已经具备积分流水、去重、商城、称号、作业/比赛结算，平台积分设计应复用它的“流水事实 + 余额缓存 + dedupeKey”思想。
- `ceshi003` 已经有课程管理数据库、API 路由、排课/签到/扣课/上课记录设计，但登录认证仍处于测试/临时实现状态，必须优先重构。
- 管理员注册不能开放给所有用户，必须采用“初始化超级管理员 + 超级管理员创建管理员 + 后续邀请注册”的闭环。

## 2. 扫描范围

本次扫描到 `moran-007` 公开仓库 7 个：

| 仓库 | 文件数 | 最近提交 | 技术栈/性质 | 当前价值 |
| --- | ---: | --- | --- | --- |
| `hydro_points` | 63 | 2026-06-04 | TypeScript, Hydro 插件 | 积分系统主资产 |
| `hydro_scratch` | 3086 | 2026-06-04 | TypeScript/JavaScript, Hydro 插件, Scratch GUI | Scratch 教学与测评主资产 |
| `OJ_text` | 3082 | 2026-05-21 | NestJS, React, Vite, Scratch GUI, judge-worker | Scratch OJ 原型资产 |
| `ceshi003` | 114 | 2025-10-20 | Node.js, Express, MySQL, Vue/Vite | 课程管理主系统底座 |
| `ceshi0001` | 0 | 空仓库 | 无 | 暂不纳入 |
| `code_yue` | 197 | 2023-05-15 | Java, Servlet, MyBatis, MySQL | 早期管理系统参考 |
| `moran` | 16 | 2021-09-26 | HTML/Java 基础实验 | 仅历史参考 |

说明：用户本次写的是 `moran007`，本文按前文提供的 GitHub 链接 `https://github.com/moran-007` 扫描。

## 3. 仓库深度汇总

### 3.1 `ceshi003`：课程管理系统底座

定位：培训机构课程管理系统。

已有内容：

- 前端：Vue 3、Vite、Axios、Chart.js。
- 后端：Node.js、Express、MySQL2、dotenv、Axios。
- 数据库：`course_management_system.sql`、`课程管理系统数据库设计.md`。
- API：`backend/api/routes`、`backend/api/controllers`、`api_documentation.md`、`swagger.json`。
- 文档：课程管理设计、排课扣课上课记录设计、数据库设计。

已有核心模块：

| 模块 | 已有程度 | 说明 |
| --- | --- | --- |
| 用户/角色/权限 | 数据库有基础表，接口有用户路由 | 权限控制未真正中间件化 |
| 登录 | 有 `/api/auth/login` | 当前是内存 session，密码验证被临时放开 |
| 课程 | 有课程表、接口、控制器 | 可作为课程目录底座 |
| 教师 | 有教师表和列表接口 | 可扩展教师端权限 |
| 学生 | 有学生表和课时表 | 可接入班级和课堂任务 |
| 班级 | 有 `class`、`student_class` | 可承载班级教学 |
| 排课 | 有 `schedule`、`schedule_student` | 适合作为“课次 lesson”的现有承载表 |
| 签到 | 有 `attendance` 和统计接口 | 可承接上课流程 |
| 扣课 | 有 `course_hours_record`、`deduction_rule` | 可承接课消 |
| 上课记录 | 有 `class_record`、`student_class_archive` | 可保存课后点评和学生档案 |
| 系统配置/备份 | 有 `system_config`、`system_backup` | 可保存注册、密码、备份策略 |

重要问题：

- `backend/package.json` 只包含 Express/MySQL/dotenv/Axios，没有 JWT、bcrypt、argon2、Redis 等正式认证依赖。
- `userController.login` 中密码验证失败阻止逻辑被注释，导致测试环境下可能任意密码登录。
- 当前 token 是随机 sessionId，并保存在进程内 `sessions = {}`，服务重启后失效，多实例部署不可用。
- `createUser`、`resetPassword` 只判断 `sessions[token].roleName === 'admin'`，不是完整 RBAC。
- 路由整体没有统一认证中间件，很多业务接口裸露。
- `DBUtils.findOne` 返回对象，但部分代码使用 `const [user] = await DBUtils.findOne(...)`，存在运行错误风险。
- `DBUtils.create/update/delete` 对 `executeQuery` 返回值的处理与 MySQL2 `ResultSetHeader` 不匹配，插入/更新可能异常。
- `user` 表结构与控制器字段存在不一致风险，例如文档中有 `role_id`，登录中又查 `role_name_id`。

结论：`ceshi003` 适合作为业务平台基础，但第一步必须修复认证、DB 工具、权限中间件和用户表字段一致性。

### 3.2 `OJ_text`：独立 Scratch OJ 原型

定位：Scratch 闯关测评系统 MVP。

技术栈：

- 前端：React、TypeScript、Vite、Ant Design。
- 后端：NestJS、TypeScript。
- 判题：Node.js 解析 `.sb3` 中的 `project.json`。
- 存储：本地 JSON + 本地上传目录。
- 预留：PostgreSQL、Redis、Docker Compose。
- Scratch GUI：本地 `scratch_GUI`，顶栏增加“提交测评”能力。

已实现能力：

- Scratch/Python/C++ 分类题库。
- Scratch 题目题干、测试点、提交面板。
- 在线 Scratch 编辑器嵌入。
- `.sb3` 上传。
- 静态解析角色、变量、列表、广播、积木 opcode。
- 静态测试点评分。
- 提交记录保存、下载提交作品。
- 动态判题原型：绿旗、等待、按键、变量读取。
- 题目 JSON 格式样例和判题规则文档。

接口资产：

| 控制器 | 路由 | 作用 |
| --- | --- | --- |
| `ProblemsController` | `/api/problems` | 题目列表、题目详情、创建、导入、图片素材上传 |
| `ScratchAssetsController` | `/api/scratch-assets` | Scratch 素材代理与缓存 |
| `SubmissionsController` | `/api/problems/:problemId/submissions` 等 | 提交、下载、从编辑器目录提交 |

结论：`OJ_text` 是非常有价值的原型，但不建议继续作为主生产系统。它的判题规则、题目格式、在线编辑器交互经验已经被 `hydro_scratch` 吸收并增强，后续只保留为参考。

### 3.3 `hydro_scratch`：Scratch 教学与测评主资产

定位：Hydro Scratch 题目、在线编辑、提交、手动/自动测评插件。

当前版本：`0.6.9`。

核心能力：

- 创建普通 Hydro 题目并标记为 Scratch。
- 在 Hydro 题目中打开内嵌 Scratch 在线编辑器。
- 加载教师上传的 `.sb3` 模板或学生最新草稿。
- 保存草稿。
- 从编辑器提交 `.sb3`。
- 将提交保存为 Hydro record，并带可下载附件。
- 教师预览、下载、列表、手动评分。
- 域级待评分队列 `/scratch/review`。
- 支持 `manual`、`static`、`dynamic`、`hybrid` 四种评分模式。
- 支持 `staticChecks`、`structureChecks`、`dynamicChecks`。
- 支持 Scratch VM 动态检查变量和角色位置。
- 支持 Hydro 原生 Scratch 题目包导入/导出。
- 自带 Scratch GUI 构建和 Scratch 素材代理。
- 支持按 Hydro domain 限制插件启用范围。

主要路由：

| 路由 | 作用 |
| --- | --- |
| `GET /scratch/problem/create` | 创建 Scratch 题目 |
| `GET/POST /scratch/problem/import` | 导入 Scratch 题目包 |
| `GET /scratch/problem/:pid/edit` | 编辑题目 |
| `GET/POST /scratch/problem/:pid/config` | 配置 Scratch 题目 |
| `GET /scratch/problem/:pid/export` | 导出题目包 |
| `GET /scratch/problem/:pid/editor` | 学生进入编辑器 |
| `GET/POST /scratch/problem/:pid/draft` | 草稿读取/保存 |
| `GET /scratch/problem/:pid/draft/project` | 读取草稿工程 |
| `POST /scratch/submit/:pid` | 提交作品 |
| `GET /scratch/problem/:pid/submissions` | 题目提交列表 |
| `GET /scratch/submission/:rid/preview` | 预览提交 |
| `GET /scratch/submission/:rid/project` | 下载提交工程 |
| `GET /scratch/submission/:rid/report` | 自动判题报告 |
| `GET/POST /scratch/submission/:rid/score` | 教师评分 |
| `GET /scratch/review` | 域级待评分队列 |

数据集合：

| 集合 | 作用 |
| --- | --- |
| `scratch.problem` | Scratch 题目配置 |
| `scratch.submission` | Scratch 提交元数据 |
| `scratch.draft` | 学生草稿 |

关键索引：

- `scratch.submission`: `domainId + rid` 唯一。
- `scratch.draft`: `domainId + problemId + userId` 唯一。

`.sb3` 安全校验能力：

- 扩展名必须 `.sb3`。
- 必须是合法 zip。
- 拒绝路径穿越和不安全路径。
- 必须包含 `project.json`。
- `project.json` 必须是合法 JSON。
- 必须包含 targets 和舞台 target。
- 限制 project 文件大小、解包总大小、单素材大小、素材数量。
- 拒绝嵌套压缩包。
- 检测异常压缩率，降低压缩炸弹风险。

题目包格式：

```txt
problem.yaml
statement.md
scratch-judge.json
template.sb3
```

结论：`hydro_scratch` 应作为 Scratch 上课、备课、模板作品、在线编辑、提交、评分的核心实现。业务平台只需要保存课程/课次与 Hydro domain、problemId、recordId 的绑定关系。

### 3.4 `hydro_points`：积分与激励主资产

定位：Hydro 积分/硬币激励系统插件。

当前版本：`0.1.12`。

核心能力：

- 积分账户。
- 积分流水。
- 每日签到。
- 课堂签到。
- 首次 AC 自动发放积分，监听 `record/judge`。
- 首次 AC 扫描补偿。
- 教师端规则配置。
- 教师手动加减积分。
- 积分商城。
- 商品图片、批量导入、排序、兑换详情、取消退还。
- 称号奖励、自动解锁、学生佩戴。
- 称号有效期、赛季、过期处理。
- 排名页和排行榜显示称号。
- 积分流水查询。
- 规则变更日志。
- 站内通知。
- 签到 IP 防刷配置。
- 作业/比赛结算。
- 自动结算任务。

主要路由：

| 路由 | 作用 |
| --- | --- |
| `GET /points` | 学生积分首页 |
| `POST /points/checkin` | 每日签到 |
| `GET /points/ranking` | 积分排行榜 |
| `GET /points/shop` | 积分商城 |
| `POST /points/shop/:id/redeem` | 兑换 |
| `POST /points/title/active` | 切换称号 |
| `GET /points/manage` | 教师管理首页 |
| `POST /points/manage/adjust` | 手动加减积分 |
| `POST /points/manage/scan-first-ac` | 扫描首次 AC |
| `GET/POST /points/manage/rules` | 积分规则 |
| `GET /points/manage/checkins` | 课堂签到管理 |
| `POST /points/manage/checkins/create` | 创建课堂签到 |
| `GET /points/manage/shop` | 商品管理 |
| `POST /points/manage/shop/create` | 创建商品 |
| `POST /points/manage/shop/import` | 批量导入商品 |
| `GET /points/manage/settlement` | 作业/比赛结算 |
| `POST /points/manage/settle/homework` | 作业结算 |
| `POST /points/manage/settle/contest` | 比赛结算 |

数据集合：

| 集合 | 作用 |
| --- | --- |
| `points.account` | 积分账户 |
| `points.ledger` | 积分流水 |
| `points.rule` | 规则配置 |
| `points.classCheckin` | 课堂签到 |
| `points.reward` | 商城商品/称号 |
| `points.redemption` | 兑换记录 |
| `points.userTitle` | 用户称号 |
| `points.ruleLog` | 规则变更日志 |
| `points.settlementJob` | 自动结算任务 |

最重要设计原则：

```txt
所有积分变化都必须写入 points.ledger
points.account.balance 只是读取加速字段
domainId + dedupeKey 是自动事件防重复的唯一依据
```

已有去重 key：

| key | 场景 |
| --- | --- |
| `daily_checkin:{domainId}:{uid}:{date}` | 每日签到 |
| `class_checkin:{domainId}:{sessionId}:{uid}` | 课堂签到 |
| `first_ac:{domainId}:{uid}:{pid}` | 首次通过题目 |
| `homework_problem:{domainId}:{tid}:{uid}:{pid}` | 作业单题 |
| `homework_full:{domainId}:{tid}:{uid}` | 作业全完成 |
| `contest_participation:{domainId}:{tid}:{uid}` | 比赛参与 |
| `contest_rank:{domainId}:{tid}:{uid}` | 比赛排名 |
| `shop:{domainId}:{uid}:{rewardId}:{redemptionId}` | 商城兑换 |
| `refund:{domainId}:{redemptionId}` | 兑换退款 |

结论：业务平台如果要做自己的积分，也必须采用同样的流水和去重设计。如果积分主要发生在 Hydro 题目、作业、比赛、签到侧，则优先复用 `hydro_points`。

### 3.5 `code_yue` 与 `moran`

`code_yue` 是 Java Servlet + MyBatis + MySQL 的图书管理系统，包含管理员、用户、图书、借阅、预约、罚金、评论等模块。它能提供一些后台管理经验，例如实体/Mapper/Service/Servlet 分层，但与当前课程平台技术栈不一致。

重要提醒：

- `code_yue` SQL 中存在明文或弱格式密码样例。
- 使用较老的 `jjwt 0.7.0`、`fastjson 1.2.46` 等依赖。
- 不建议将其代码直接迁入当前平台。

`moran` 是早期 HTML/Java 学习项目，仅作历史参考。

## 4. 技术资产复用策略

### 4.1 应直接复用

| 资产 | 复用方式 |
| --- | --- |
| `hydro_scratch` Scratch 插件 | 作为 Scratch 编辑、模板、提交、评分、题目包导入导出的生产能力 |
| `hydro_points` 积分插件 | 作为 Hydro 域内积分、签到、商城、称号、作业/比赛结算能力 |
| `ceshi003` 数据库设计 | 作为课程、班级、课次、签到、课消、上课记录底座 |
| `ceshi003` 排课/扣课/上课记录文档 | 作为教师端上课流程的业务依据 |

### 4.2 应迁移思想但不直接作为主线

| 资产 | 迁移内容 |
| --- | --- |
| `OJ_text` | 题目格式、Scratch 判题规则、在线编辑器交互、动态判题思路 |
| `code_yue` | Java 项目的后台分层经验，不能迁移安全设计 |

### 4.3 应重构

| 模块 | 原因 | 优化方向 |
| --- | --- | --- |
| `ceshi003` 登录 | 密码验证被临时放开，session 存内存 | JWT + refresh token 或 Redis session |
| `ceshi003` 权限 | 只用角色名判断，路由无统一中间件 | RBAC 权限点 + 数据范围 |
| `ceshi003` DBUtils | 返回值处理存在不一致 | 修复 INSERT/UPDATE/SELECT 返回模型 |
| `ceshi003` 用户表字段 | `role_id`、`role_name_id` 混用风险 | 统一 schema 和控制器字段 |
| Scratch 业务接入 | 课程系统与 Hydro 插件尚未绑定 | 新增绑定表和跳转/同步接口 |

## 5. 优化后的总体架构

推荐第一阶段架构：

```txt
管理后台 / 教师端 / 学生端
        ↓
Vue 3 + Vite 前端
        ↓
Node.js + Express 业务 API
        ↓
MySQL 课程业务库
        ↓
Hydro 独立服务
        ↓
hydro_scratch + hydro_points
```

业务平台负责：

- 用户、角色、权限、登录、管理员注册。
- 教师、学生、班级、课程、排课。
- 签到、课消、上课记录、课后点评。
- 备课包、课件资源、课堂任务发布。
- 与 Hydro 的账号绑定、题目绑定、结果同步。

Hydro 负责：

- Scratch 题目。
- Scratch `.sb3` 模板。
- Scratch 在线编辑器。
- Scratch 草稿与提交。
- Scratch 手动评分和自动判题。
- Hydro 内作业/比赛/题目积分。
- Hydro 侧商城、称号、排行榜。

## 6. Scratch 备课与上课深度方案

### 6.1 业务对象映射

`ceshi003` 已经使用 `schedule` 表承载排课。第一阶段不必新建完整 `lesson` 表，可以把一条 `schedule` 视为一节课次：

| 平台概念 | 当前表/新增表 | 说明 |
| --- | --- | --- |
| 课程 | `course` | 课程目录 |
| 班级 | `class` | 学生组织 |
| 课次 | `schedule` | 具体上课时间 |
| 上课记录 | `class_record` | 教师课后记录 |
| 学生课堂档案 | `student_class_archive` | 每个学生在每节课表现 |
| 备课包 | 新增 `lesson_prep` | 绑定 `schedule_id` |
| 课件资源 | 新增 `lesson_resource` | PDF、PPT、图片、视频、Markdown、链接 |
| Scratch 任务 | 新增 `scratch_lesson_task` | 绑定 Hydro domain/problem |
| 学生任务状态 | 新增 `scratch_lesson_result` | 保存打开、草稿、提交、评分状态 |

### 6.2 教师备课流程

```txt
教师登录
↓
进入今日/未来排课
↓
选择某一节 schedule
↓
创建备课包 lesson_prep
↓
上传课件 lesson_resource
↓
选择 Scratch 题目来源
  ├─ 绑定已有 Hydro Scratch problemId
  ├─ 跳转 Hydro 创建 Scratch 题目
  └─ 跳转 Hydro 导入 Scratch 题目包
↓
配置课堂任务标题、开放时间、是否计入积分
↓
发布给班级或指定学生
```

### 6.3 Scratch 题目来源策略

| 来源 | 适用场景 | 实施建议 |
| --- | --- | --- |
| 绑定已有 Hydro 题目 | 复用旧课件、已有题库 | 第一阶段优先 |
| Hydro 题目包导入 | 老师跨站点复用题目 | 直接使用 `hydro_scratch` 的 `/scratch/problem/import` |
| 平台上传 `.sb3` 模板 | 简单作品模板，不带自动判题 | 平台校验后保存，同时可提示老师去 Hydro 配题 |
| 平台一键创建 Hydro 题 | 后期自动化 | 第二阶段再做 |

第一阶段最稳方案：

```txt
平台不强行代理 Hydro 题目创建
教师在 Hydro 中创建/导入 Scratch 题
平台只保存 domainId + problemId + 跳转 URL
```

### 6.4 学生上课流程

```txt
学生登录平台
↓
查看今日课程
↓
进入课堂任务
↓
平台校验学生属于发布范围
↓
平台记录 OPENED 状态
↓
跳转 /d/{domainId}/scratch/problem/{pid}/editor
↓
学生在 Hydro Scratch 编辑器保存草稿/提交
↓
教师在 Hydro 批改或自动判题
↓
平台同步 result 状态
```

### 6.5 教师上课页面

建议教师端一节课页面分 6 个区域：

| 区域 | 功能 |
| --- | --- |
| 课堂概览 | 课程、班级、时间、教室、教师、状态 |
| 签到课消 | 学生名单、出勤、迟到、请假、缺勤、课时扣减 |
| 备课资料 | 课件、模板、教案、链接 |
| Scratch 任务 | 题目、编辑器入口、提交要求、评分方式 |
| 学生进度 | 未打开、已打开、草稿、已提交、待评分、通过 |
| 课后记录 | 教学内容、课堂表现、作业、点评、积分 |

### 6.6 学生任务状态

```txt
NOT_STARTED   未开始
OPENED        已打开
DRAFT_SAVED   已保存草稿
SUBMITTED     已提交
REVIEWING     待评分
PASSED        已通过
NEED_REWORK   需要修改
FAILED        未通过
CLOSED        已关闭
```

第一阶段状态来源：

- `OPENED` 由业务平台记录。
- `SUBMITTED/REVIEWING/PASSED/FAILED` 可由教师手动同步。

第二阶段状态来源：

- 由 `hydro_scratch` 增加回调或由平台定时同步 Hydro record。

## 7. 登录与管理员注册深度方案

### 7.1 当前登录模块扫描结论

`ceshi003` 现有登录接口是可运行雏形，但不能作为正式安全实现：

- 当前会话存放在进程内对象，无法支持重启、横向扩展、统一失效。
- 密码校验逻辑被临时注释，存在严重安全风险。
- 密码哈希使用 PBKDF2 10000 次，强度偏低。
- 管理员权限只判断 `roleName === 'admin'`，不支持超级管理员、校区管理员、教师等细粒度权限。
- 路由缺少统一鉴权中间件。
- 登录日志、失败锁定、刷新 token、主动吊销都未真正落地。

### 7.2 推荐认证模式

第一阶段推荐：

```txt
Access Token: JWT，15-30 分钟
Refresh Token: 数据库存哈希，7-30 天
密码哈希: Argon2id 或 bcrypt
权限: RBAC + 数据范围
审计: audit_log
```

如果希望少改动 Express 现有代码，也可以采用：

```txt
Access Token: 随机 sessionId
Session 存储: Redis
权限: RBAC
```

但从后续平台/Hydro/多端扩展看，JWT + refresh token 更通用。

### 7.3 管理员注册策略

禁止开放普通管理员注册入口。

推荐三段式：

| 阶段 | 注册方式 | 说明 |
| --- | --- | --- |
| 初始化 | `SETUP_TOKEN` 创建首个 `SUPER_ADMIN` | 只允许系统没有超级管理员时使用 |
| 正式运营 | 超级管理员创建管理员 | 可指定角色、校区、状态 |
| 协作扩展 | 邀请链接注册管理员 | 第二阶段实现，邀请码有角色、校区、过期时间 |

初始化流程：

```txt
POST /api/auth/setup-admin
↓
校验环境变量 SETUP_TOKEN
↓
检查数据库中不存在 SUPER_ADMIN
↓
创建用户和角色
↓
写入 audit_log
↓
关闭初始化入口
```

### 7.4 角色模型

| 角色 | 说明 |
| --- | --- |
| `SUPER_ADMIN` | 全局超级管理员 |
| `ADMIN` | 平台/校区管理员 |
| `TEACHER` | 教师 |
| `STUDENT` | 学生 |
| `PARENT` | 家长 |
| `FINANCE` | 财务/行政 |

权限点建议：

```txt
auth.login
admin.setup
admin.create
admin.update
user.manage
teacher.manage
student.manage
course.manage
class.manage
schedule.manage
attendance.manage
lesson.prepare
lesson.teach
scratch.task.create
scratch.task.publish
scratch.task.review
hydro.bind
points.view
points.adjust
system.config
audit.view
```

## 8. 数据库优化设计

以下为在 `ceshi003` MySQL 基础上的新增/修正建议。

### 8.1 认证相关新增表

```sql
CREATE TABLE IF NOT EXISTS auth_refresh_token (
  token_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  token_hash VARCHAR(255) NOT NULL,
  device_info VARCHAR(255),
  ip_address VARCHAR(64),
  expires_at DATETIME NOT NULL,
  revoked_at DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_refresh_user (user_id),
  INDEX idx_refresh_expires (expires_at),
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS login_attempt (
  attempt_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  ip_address VARCHAR(64),
  success TINYINT NOT NULL DEFAULT 0,
  fail_reason VARCHAR(100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_login_username_time (username, created_at),
  INDEX idx_login_ip_time (ip_address, created_at)
);

CREATE TABLE IF NOT EXISTS audit_log (
  log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  actor_user_id INT NULL,
  action VARCHAR(128) NOT NULL,
  target_type VARCHAR(64),
  target_id VARCHAR(64),
  ip_address VARCHAR(64),
  user_agent VARCHAR(255),
  detail_json JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_audit_actor (actor_user_id),
  INDEX idx_audit_action (action),
  INDEX idx_audit_created (created_at)
);
```

建议给 `user` 表补充字段：

```sql
ALTER TABLE user
  ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL,
  ADD COLUMN IF NOT EXISTS token_version INT NOT NULL DEFAULT 1,
  ADD COLUMN IF NOT EXISTS failed_login_count INT NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS locked_until DATETIME NULL,
  ADD COLUMN IF NOT EXISTS last_login_at DATETIME NULL,
  ADD COLUMN IF NOT EXISTS force_password_change TINYINT NOT NULL DEFAULT 0;
```

说明：如果继续使用 `password` 字段，也要明确它保存哈希而不是明文。建议逐步迁移为 `password_hash`。

### 8.2 Scratch 备课与课堂任务表

```sql
CREATE TABLE IF NOT EXISTS lesson_prep (
  prep_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  schedule_id INT NOT NULL,
  title VARCHAR(128) NOT NULL,
  description TEXT,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  created_by INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_prep_schedule (schedule_id),
  INDEX idx_prep_creator (created_by),
  FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lesson_resource (
  resource_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  prep_id BIGINT NOT NULL,
  resource_type VARCHAR(32) NOT NULL,
  title VARCHAR(128) NOT NULL,
  file_url VARCHAR(500),
  external_url VARCHAR(500),
  file_size BIGINT,
  file_hash VARCHAR(128),
  sort_order INT NOT NULL DEFAULT 0,
  created_by INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_resource_prep (prep_id),
  FOREIGN KEY (prep_id) REFERENCES lesson_prep(prep_id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scratch_lesson_task (
  task_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  schedule_id INT NOT NULL,
  class_id INT NULL,
  prep_id BIGINT NULL,
  title VARCHAR(128) NOT NULL,
  description TEXT,
  hydro_domain_id VARCHAR(64) NOT NULL,
  hydro_problem_id VARCHAR(64) NOT NULL,
  hydro_problem_url VARCHAR(500) NULL,
  judge_mode VARCHAR(32) NOT NULL DEFAULT 'manual',
  points_reward INT NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  start_at DATETIME NULL,
  end_at DATETIME NULL,
  created_by INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_scratch_schedule (schedule_id),
  INDEX idx_scratch_hydro (hydro_domain_id, hydro_problem_id),
  FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE CASCADE,
  FOREIGN KEY (prep_id) REFERENCES lesson_prep(prep_id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scratch_lesson_result (
  result_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  student_id INT NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'not_started',
  hydro_uid INT NULL,
  hydro_record_id VARCHAR(128) NULL,
  score INT NULL,
  comment TEXT NULL,
  opened_at DATETIME NULL,
  last_draft_at DATETIME NULL,
  submitted_at DATETIME NULL,
  reviewed_at DATETIME NULL,
  reviewed_by INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_task_student (task_id, student_id),
  INDEX idx_result_status (task_id, status),
  FOREIGN KEY (task_id) REFERENCES scratch_lesson_task(task_id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);
```

### 8.3 Hydro 账号绑定表

```sql
CREATE TABLE IF NOT EXISTS hydro_account_binding (
  binding_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  student_id INT NULL,
  hydro_domain_id VARCHAR(64) NOT NULL,
  hydro_uid INT NULL,
  hydro_username VARCHAR(128) NOT NULL,
  bind_status VARCHAR(32) NOT NULL DEFAULT 'active',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_domain (user_id, hydro_domain_id),
  UNIQUE KEY uk_hydro_user (hydro_domain_id, hydro_username),
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);
```

## 9. API 优化设计

### 9.1 认证接口

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| `POST` | `/api/auth/setup-admin` | 初始化密钥 | 首次创建超级管理员 |
| `POST` | `/api/auth/login` | 公开 | 登录 |
| `POST` | `/api/auth/refresh` | refresh token | 刷新 access token |
| `POST` | `/api/auth/logout` | 登录用户 | 当前设备退出 |
| `POST` | `/api/auth/logout-all` | 登录用户 | 所有设备退出 |
| `GET` | `/api/auth/me` | 登录用户 | 当前用户、角色、权限 |
| `POST` | `/api/admin/users` | `admin.create` | 创建管理员/教师/学生账号 |
| `PUT` | `/api/admin/users/:userId/status` | `admin.update` | 启用/禁用账号 |
| `POST` | `/api/admin/users/:userId/reset-password` | `admin.update` | 重置密码 |

### 9.2 备课接口

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| `GET` | `/api/teacher/schedules/:scheduleId/prep` | `lesson.prepare` | 获取备课包 |
| `POST` | `/api/teacher/schedules/:scheduleId/prep` | `lesson.prepare` | 创建/更新备课包 |
| `POST` | `/api/teacher/preps/:prepId/resources` | `lesson.prepare` | 上传课件 |
| `DELETE` | `/api/teacher/resources/:resourceId` | `lesson.prepare` | 删除课件 |
| `POST` | `/api/teacher/scratch-tasks` | `scratch.task.create` | 创建 Scratch 任务 |
| `POST` | `/api/teacher/scratch-tasks/:taskId/publish` | `scratch.task.publish` | 发布任务 |
| `GET` | `/api/teacher/schedules/:scheduleId/scratch-progress` | `scratch.task.review` | 查看课堂进度 |
| `POST` | `/api/teacher/scratch-results/:resultId/review` | `scratch.task.review` | 手动回填评分 |

### 9.3 学生接口

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| `GET` | `/api/student/schedules/today` | `student.view` | 今日课程 |
| `GET` | `/api/student/scratch-tasks/:taskId` | `student.view` | 任务详情 |
| `POST` | `/api/student/scratch-tasks/:taskId/open` | `student.view` | 标记打开任务 |
| `GET` | `/api/student/scratch-tasks/:taskId/editor-url` | `student.view` | 获取 Hydro 编辑器跳转地址 |
| `GET` | `/api/student/scratch-results` | `student.view` | 查看提交和评分 |

### 9.4 Hydro 同步接口

第二阶段建议：

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| `POST` | `/api/integrations/hydro/scratch/submitted` | HMAC 签名 | Scratch 提交同步 |
| `POST` | `/api/integrations/hydro/scratch/reviewed` | HMAC 签名 | Scratch 评分同步 |
| `POST` | `/api/integrations/hydro/points/settled` | HMAC 签名 | 积分结算同步 |

签名建议：

```txt
X-Hydro-Timestamp: 1780646400
X-Hydro-Signature: HMAC_SHA256(secret, timestamp + "." + rawBody)
```

## 10. 开发优先级

### P0：修复课程平台基础安全

必须先做：

1. 修复 DBUtils 对 SELECT/INSERT/UPDATE/DELETE 返回值处理。
2. 统一 `user` 表字段和控制器字段。
3. 恢复真实密码校验，删除“任意密码登录”的临时代码。
4. 引入正式认证依赖，完成 access token/refresh token。
5. 增加统一认证中间件。
6. 增加 RBAC 权限中间件。
7. 增加登录失败记录、账户锁定、审计日志。
8. 实现 `setup-admin`。
9. 实现超级管理员创建管理员。

验收标准：

- 任意错误密码无法登录。
- 未登录访问业务接口返回 401。
- 无权限访问管理接口返回 403。
- 第一个超级管理员只能初始化一次。
- 管理员创建、禁用、重置密码均写审计日志。

### P1：打通 Scratch 备课

任务：

1. 新增 `lesson_prep`、`lesson_resource`、`scratch_lesson_task` 表。
2. 教师端课次详情增加“备课资料”和“Scratch 任务”。
3. 支持上传课件。
4. 支持绑定 Hydro domain/problemId。
5. 支持发布 Scratch 任务。
6. 学生端显示今日任务。
7. 学生端获取 Hydro editor URL。

验收标准：

- 教师能在某节课绑定一个 Hydro Scratch 题目。
- 学生只能看到自己班级发布的任务。
- 学生点击任务能进入对应 Hydro Scratch 编辑器。
- 平台记录学生 `OPENED` 状态。

### P2：打通上课进度与评分

任务：

1. 教师端课堂进度页。
2. 手动同步 Hydro recordId 和分数。
3. 教师可跳转 Hydro `/scratch/review` 或单题提交列表。
4. 课后记录关联 Scratch 任务结果。
5. 支持 `PASSED/NEED_REWORK/FAILED` 状态。

验收标准：

- 教师可以看到学生打开、提交、通过状态。
- 教师可以从平台进入 Hydro 批改页。
- 评分结果可以回写平台。

### P3：Hydro 自动回调与积分联动

任务：

1. 在 `hydro_scratch` 增加提交/评分回调。
2. 平台实现 HMAC 校验。
3. 回调自动更新 `scratch_lesson_result`。
4. 接入 `hydro_points` 或平台积分流水。
5. 确保同一任务同一学生只发一次奖励。

验收标准：

- 学生提交后平台自动更新 `SUBMITTED`。
- 教师评分后平台自动更新分数和状态。
- 重复回调不会重复发积分。

## 11. 风险清单

| 风险 | 来源 | 影响 | 优先处理 |
| --- | --- | --- | --- |
| 登录可绕过密码 | `ceshi003` 当前控制器 | 严重安全事故 | P0 |
| session 存内存 | `ceshi003` 当前实现 | 重启丢登录，多实例不可用 | P0 |
| DBUtils 返回值 bug | `ceshi003` DB 工具 | 创建用户/修改密码可能失败 | P0 |
| 权限只靠角色名 | `ceshi003` 当前实现 | 越权访问 | P0 |
| 业务平台直接读 Hydro 数据库 | 未来集成风险 | Hydro 升级后失效 | P2/P3 避免 |
| Scratch 任务状态不同步 | 平台与 Hydro 分离 | 教师看不到实时进度 | P2/P3 |
| `.sb3` 文件不校验 | 平台上传模板 | 压缩包攻击/异常文件 | P1 |
| 积分重复发放 | 多次提交/回调 | 学生刷积分 | P3 |
| 旧 Java 仓库含弱密码样例 | `code_yue` | 误迁移安全隐患 | 不迁移 |

## 12. 推荐目录改造

在 `ceshi003/backend` 中建议新增：

```txt
backend/
  api/
    controllers/
      authController.js
      adminController.js
      lessonPrepController.js
      scratchTaskController.js
      hydroIntegrationController.js
    routes/
      authRoutes.js
      adminRoutes.js
      lessonPrepRoutes.js
      scratchTaskRoutes.js
      hydroIntegrationRoutes.js
    middlewares/
      authRequired.js
      requirePermission.js
      requireDataScope.js
      auditLog.js
  services/
    authService.js
    passwordService.js
    tokenService.js
    permissionService.js
    lessonPrepService.js
    scratchTaskService.js
    hydroUrlService.js
  db/
    migrations/
      20260605_auth_tables.sql
      20260605_scratch_lesson_tables.sql
```

前端建议新增页面：

```txt
frontend/src/views/
  auth/
    Login.vue
    SetupAdmin.vue
  teacher/
    TodaySchedules.vue
    ScheduleDetail.vue
    LessonPrep.vue
    ScratchProgress.vue
  student/
    TodayCourses.vue
    ScratchTaskDetail.vue
  admin/
    UserManage.vue
    RoleManage.vue
```

## 13. 参考技术文档与依据

### GitHub 仓库

- `moran-007` 仓库列表：https://github.com/moran-007?tab=repositories
- `ceshi003`：https://github.com/moran-007/ceshi003
- `OJ_text`：https://github.com/moran-007/OJ_text
- `hydro_scratch`：https://github.com/moran-007/hydro_scratch
- `hydro_points`：https://github.com/moran-007/hydro_points
- `code_yue`：https://github.com/moran-007/code_yue
- `moran`：https://github.com/moran-007/moran

### 外部技术依据

- Hydro 官方仓库：https://github.com/hydro-dev/Hydro
- Scratch `.sb3` 文件格式说明：https://scratchapi.org/File%20format/sb3/
- RFC 7519 JSON Web Token：https://datatracker.ietf.org/doc/html/rfc7519
- OWASP Password Storage Cheat Sheet：https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OWASP Authentication Cheat Sheet：https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- Express Routing：https://expressjs.com/en/guide/routing/
- Vue 官方文档：https://vuejs.org/guide/introduction.html
- Vite 官方文档：https://vite.dev/guide/

## 14. 最终建议

当前最佳路线不是“再造一个完整 Scratch 课堂系统”，而是：

```txt
先把 ceshi003 的登录、管理员注册、权限和 DB 工具修稳
再把 ceshi003 的课次 schedule 与 hydro_scratch 的 Scratch problem 绑定
教师备课只管理业务资源和绑定关系
Scratch 编辑、提交、评分、自动测评都交给 hydro_scratch
积分流水和商城优先复用 hydro_points
最后再通过回调或定时同步把 Hydro 结果回填到业务平台
```

第一版交付边界应控制为：

- 管理员安全登录。
- 首个超级管理员初始化。
- 超级管理员创建管理员/教师账号。
- 教师进入课次并上传课件。
- 教师绑定 Hydro Scratch 题目。
- 教师发布 Scratch 任务给班级。
- 学生从平台跳转 Hydro Scratch 编辑器。
- 教师从平台查看学生任务状态，并跳转 Hydro 批改。

这条路线最小化重复开发，最大化复用现有 GitHub 已完成资产，也能让“Scratch 上课、备课”和“登录、管理员注册”两个当前重点尽快形成可用闭环。
