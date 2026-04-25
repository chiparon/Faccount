# 2026-04-24 v1 foundation

## 目标
- 按已批准方案初始化仓库、文档、后端和前端基础结构。

## 实际修改
- 建立根目录治理文档：`rules.md`、`plan.md`、`memories.md`。
- 建立 `backend/`、`frontend/`、`worklog/` 目录。
- 建立 FastAPI 后端骨架、SQLAlchemy 模型、Pydantic 模式、V1 接口与基础测试。
- 建立 Vue 3 + Vite 前端骨架、页面容器、API 封装和基础样式。
- 增加 `.gitignore`、数据库初始化 SQL、环境变量示例。

## 验证
- 已完成静态结构检查。
- 受限于当前环境缺少可用 Node.js，未执行前端安装与运行。
- 当前未安装后端依赖，接口与测试未在本地真实启动验证。
- 2026-04-24 追加：发现可用 Node 路径 `E:\Program Files\Huawei\DevEco Studio\tools\node\`。
- 2026-04-24 追加：已在 `frontend/` 执行 `npm install`，并成功执行 `npm run build`。
- 2026-04-24 追加：后端依赖安装仍被 pip 网络代理错误阻塞，`fastapi`、`pydantic`、`sqlalchemy` 尚未安装成功。
- 2026-04-24 追加：`backend/.venv` 已更新为 Python 3.12.0，后端依赖已安装。
- 2026-04-24 追加：后端测试通过，命令为 `$env:PYTHONPATH='backend'; .\backend\.venv\Scripts\python.exe -m pytest backend\tests -q`。
- 2026-04-24 追加：确认 MySQL80 服务正在运行，`mysql.exe` 位于 `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe`。
- 2026-04-25 追加：前端表单并非纯壳子，已有 API 提交逻辑；点击无明显反馈是因为接口失败时没有显示错误。
- 2026-04-25 追加：为账户、分类、流水表单补充加载状态、成功提示和错误提示。
- 2026-04-25 追加：补充 `cryptography==42.0.8`，用于 PyMySQL 连接 MySQL 8 默认认证方式。
- 2026-04-25 追加：当前后端连接 MySQL 仍失败，错误为 root 用户认证拒绝，需要修正 `backend/.env` 中的 MySQL 用户名/密码或调整 MySQL 用户权限。
- 2026-04-25 追加：修复后端配置加载路径，确保从项目根目录启动时也会读取 `backend/.env`。
- 2026-04-25 追加：验证当前配置已读取到 `accounts_app@127.0.0.1/accounts_app`，后端测试通过，前端构建通过。
- 2026-04-25 追加：修复流水创建接口中 `category.kind` 字符串被当作枚举访问导致的 500 错误。
- 2026-04-25 追加：分类管理的父分类改为下拉选择；记一笔页面的分类、来源账户、目标账户改为从接口加载的下拉选择。
- 2026-04-25 追加：后端测试 `5 passed`，前端 Vite 构建通过，已通过 API 成功创建一条支出流水。
- 2026-04-25 追加：用户确认页面侧已 OK；已将电脑重启后的项目启动指令写入 `rules.md`。

## 遗留问题
- 需要补充 `backend/.env` 中的数据库连接字符串。
- 需要执行 `backend/sql/init_db.sql` 完成数据库初始化。
- 前端依赖已安装，后续可用 DevEco Node 路径运行前端命令。
- 需要刷新前端页面验证新的下拉选择交互；后续继续优化列表展示和避免测试数据残留。
- 下次启动时按 `rules.md` 的项目启动指令先启动 MySQL80、后端和前端。
