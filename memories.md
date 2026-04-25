# memories

- 项目名称：账目记录应用。
- 当前技术栈已定：`FastAPI + MySQL 8 + Vue 3 + Vite`。
- 当前开发环境：`Windows 11`。
- 首版产品定位：单用户本地账本，不做登录注册。
- 核心业务对象：账户、分类、交易记录。
- 交易三大类型：收入、支出、转账。
- 分类采用单分类绑定，但分类本身支持父子层级。
- 遇到方向选择必须先询问用户，不擅作主张。
- 若出现不同实现方向，使用 git 新分支承载，再由用户决定是否并入 `main`。
- 当前仓库已完成 V1 基础骨架：治理文档、FastAPI 后端骨架、Vue 3 前端骨架、数据库初始化 SQL、基础测试文件已创建。
- 当前环境状态：`backend/.venv` 已安装后端依赖，后端测试通过；前端依赖已安装，Vite 构建通过；MySQL80 服务已安装并运行。
- 当前阻塞项：尚未创建 `backend/.env`，尚未确认 MySQL 账号密码并执行 `backend/sql/init_db.sql`，尚未完成前后端联调。
- 前端命令可使用 DevEco Node：`E:\Program Files\Huawei\DevEco Studio\tools\node\npm.cmd`。
- 当前联调状态：账户新增、分类新增、支出流水新增链路已跑通；分类父级、流水分类、来源账户、目标账户已改为下拉选择。
- 电脑重启后启动项目：确认/启动 MySQL80；项目根目录启动 FastAPI；另开终端进入 `frontend/` 启动 Vite。
