# rules

## 对话启动流程
- 每次开始新对话前，先阅读 `rules.md`、`plan.md`、`memories.md`。
- 根据三份文档确认当前项目状态、未完成事项和已有决策。

## 工作留痕原则
- 只要发生代码或配置修改，就必须在 `worklog/` 中追加本次对话对应的日志。
- 每次新对话新开一个日志文件，文件名使用日期和主题，便于追溯。
- 日志至少记录：目标、实际修改、验证结果、遗留问题。

## 版本管理原则
- 使用 git 管理版本，主分支为 `main`。
- 若出现不同方向的实现思路或产品方案，先开新分支实验。
- 只有在你确认后，实验分支才允许并入 `main`。

## 决策原则
- 涉及方向、技术路线、数据模型、重要交互和兼容策略的选择，必须先询问你。
- 不允许在关键方向问题上擅作主张。

## 开发环境
- 当前默认开发环境：`Windows 11`。
- 后端技术栈：`Python + FastAPI + MySQL 8`。
- 前端技术栈：`Vue 3 + Vite`。

## 项目启动指令
- 电脑重启后，先确认 MySQL80 服务已运行：
  `Get-Service MySQL80`
- 若 MySQL80 未运行，启动服务：
  `Start-Service MySQL80`
- 启动后端，在项目根目录 `E:\Eproject\accounts` 执行：
  `$env:PYTHONPATH='backend'`
  `.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload`
- 启动前端，另开一个终端执行：
  `cd E:\Eproject\accounts\frontend`
  `& 'E:\Program Files\Huawei\DevEco Studio\tools\node\npm.cmd' run dev`
- 前端访问地址通常为：
  `http://localhost:5173/`
- 后端健康检查地址：
  `http://127.0.0.1:8000/health`

## 项目结构约定
- `backend/`：后端服务、模型、接口、测试、数据库初始化脚本。
- `frontend/`：前端页面、组件、样式、接口封装。
- `worklog/`：每次对话的工作日志。
- 根目录文档：
  - `rules.md`：长期规范与隐式约定。
  - `plan.md`：计划、阶段目标、完成情况。
  - `memories.md`：跨对话保留的关键信息。
