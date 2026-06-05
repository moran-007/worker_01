# Scratch 教学平台开发准备区

本目录已整理为开发准备结构：

```txt
assets      UI 设计参考图
app         P0/P1 复制并改造后的 class_worker 主系统
docs        技术文档与开发引用清单
references 参考源码扫描结果
_archive_removed_unrelated_20260605  已移出当前开发面的归档内容
```

优先阅读：

1. `docs\开发引用清单.md`
2. `docs\P0-P1实现记录.md`
3. `docs\本地素材库与worker系统资产整合技术文档.md`
4. `docs\moran-007 GitHub深度扫描与平台优化技术文档.md`

开发主线：

- 教务/课次/签到/权限：优先参考 `E:\moran_project\class_worker`
- Scratch 模板、提交、评分：优先参考 `references\source_scans\moran_007_20260605\hydro_scratch`
- Scratch 素材库和作品社区：参考 `references\source_scans\scratchlite_20260605`
- UI 设计：参考 `assets\ui-reference\img`
- 权限实现：必须以后端权限校验为准，前端隐藏菜单不能替代后端拦截

当前实现：

- P0/P1 主系统代码位于 `app`
- 默认使用 SQLite，本地可直接启动
- 保留 `DATABASE_ENGINE=mysql` 作为服务器部署迁移开关
- 已新增动态权限表、学生账号关联、Hydro/外部账号绑定表、上传资产表
