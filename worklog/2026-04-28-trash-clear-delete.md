# 2026-04-28 trash clear delete

## 目标
- 修复软删除后同名分类/账户再次新增失败的问题。
- 增加 Trash 的永久删除和清空功能。

## 实际修改
- 后端 `backend/app/api/routes.py`：
  - 新增 `DELETE /trash/{entity_type}/{record_id}`，支持永久删除 Trash 中的流水、分类、账户。
  - 新增 `DELETE /trash?entity_type=...`，支持按类型或全部清空 Trash。
  - 新增数据库唯一约束冲突兜底，把同名仍在 Trash 的情况返回为明确的 `409` 提示。
  - 清空 Trash 时先永久删除已软删流水和子项，再处理分类、账户。
  - 仍被现有流水引用的分类/账户会跳过并返回原因，避免破坏历史数据。
- 前端 `frontend/src/api/client.js`：
  - 增加 `permanentlyDeleteTrash` 和 `clearTrash`。
- 前端 `frontend/src/pages/TrashPage.vue`：
  - 修复页面中文文案乱码。
  - 增加单条“永久删除”按钮。
  - 增加“清空当前范围”按钮。
  - 增加清空结果和跳过原因提示。
- 前端 `frontend/src/styles/main.css`：
  - 增加 Trash 工具栏、提示文案、操作按钮组样式。

## 验证结果
- 后端测试通过：`5 passed`。
- 前端构建通过：`npm run build`。
- 已重启后端服务，`http://127.0.0.1:8000/health` 返回 `ok`。
- 已验证新 Trash 删除路由加载：`DELETE /trash/transaction/999999` 返回 `404`，不是旧服务的 `405`。

## 遗留问题
- 如果分类/账户仍被流水引用，永久删除会被阻止；可先删除相关流水，或继续保留在 Trash。
