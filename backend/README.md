# backend

## setup
1. 创建虚拟环境并安装依赖：
   `python -m venv .venv`
   `.venv\Scripts\pip install -r requirements.txt`
2. 复制 `.env.example` 为 `.env`，填入 MySQL 8 连接串。
3. 在 MySQL 中执行 `sql/init_db.sql`。
4. 启动服务：
   `.venv\Scripts\uvicorn app.main:app --reload`

## api
- `GET /health`
- `GET|POST /accounts`
- `GET|POST /categories`
- `GET|POST /transactions`

