# 2026-04-25 delete filter monthly

## 目标
- 增加流水、账户、分类的删除条目功能。
- 增加流水筛选功能，支持时间起止、类型、分类、账户等条件。
- 增加流水排序功能，支持按时间、金额、创建时间和编号排序。
- 增加适合每月数百条流水查看的月度流水总览视图。

## 实际修改
- 后端 `backend/app/api/routes.py` 新增账户、分类、流水删除接口。
- 后端流水列表接口新增 `start_at`、`end_at`、`transaction_type`、`category_id`、`account_id`、`sort_by`、`sort_order` 查询参数。
- 删除账户时会阻止删除已被流水使用的账户；删除分类时会阻止删除存在子分类或已被流水使用的分类。
- 前端 `frontend/src/api/client.js` 支持查询参数拼接和 `204 No Content` 响应。
- 前端账户、分类、流水列表增加删除按钮和确认提示。
- 前端流水列表增加筛选栏、排序控件、筛选结果汇总。
- 新增 `frontend/src/pages/MonthlyTransactionsPage.vue`，按月份分组展示流水、收入、支出和净额，适合较大月流水量浏览。
- 更新 `frontend/src/styles/main.css`，补充筛选栏、删除按钮、月度总览表格等样式。

## 验证结果
- 后端测试通过：`$env:PYTHONPATH='backend'; .\backend\.venv\Scripts\python.exe -m pytest backend\tests -q`，结果 `5 passed`。
- 前端构建通过：`& 'E:\Program Files\Huawei\DevEco Studio\tools\node\npm.cmd' run build`。

## 遗留问题
- 尚未在浏览器中用真实数据逐项人工验证删除、筛选、排序和月度总览体验。
- 当前删除为物理删除；若后续需要误删恢复或审计，需要再设计软删除策略。

## 对话结束记录
- 准备以 `beta0.2` 版本提交并推送本轮变更。
- 本轮提交范围包含后端接口、前端页面、样式、API 封装、月度总览视图、`memories.md` 与本轮工作日志。
- `pageref/` 是本地参考页面目录，本次不纳入版本提交。
