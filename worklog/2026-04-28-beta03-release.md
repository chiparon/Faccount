# 2026-04-28 beta0.3 release

## 目标
- 将 `candi-beta0.3-foundation` 当前候选版本并入 `main`。
- 版本号标记为 `beta0.3`。
- 补齐 beta0.3 的工作日志和长期记忆。

## 实际修改范围
- 后端：流水编辑、Trash 软删除/恢复/永久删除/清空、流水子元素、来源逻辑、运行期 schema 补列、筛选搜索增强。
- 前端：页内分页布局、流水编辑、Trash 页面、账单导入缓存、微信 XLSX/支付宝 CSV 识别、预算流转雏形、筛选排序体验优化。
- 文档：更新 `plan.md`、`memories.md`，新增 beta0.3 多个 worklog。
- 依赖：新增前端 `fflate`，用于安全解析微信 XLSX。

## 验证计划
- 后端测试：`$env:PYTHONPATH='backend'; .\backend\.venv\Scripts\python.exe -m pytest backend\tests -q`。
- 前端构建：`& 'E:\Program Files\Huawei\DevEco Studio\tools\node\npm.cmd' run build`。
- 前端依赖审计：`npm audit --audit-level=high`。

## 遗留问题
- `pageref/` 包含参考图片和真实账单导出文件，本次不提交。
- 统计页只保留 5 个候选方案记录，尚未实现。
- 桌面封装只是远期展望，不纳入 beta0.3。
