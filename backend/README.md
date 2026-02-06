# FastAPI 后端 MVP（MySQL + JWT + 上传/入库占位 + QA示例）

这套后端与前端基础界面接口一一对应，目标是先跑通：

登录 → 上传资料 → 处理入库 → 提问 → 返回答案与引用 → 保存历史。

后续你再把“占位实现”替换为真正的：PDF/DOCX 解析、向量检索、RAG + LLM、重排、评测等。

## 1) 启动 MySQL（推荐 docker-compose）

在本目录执行：

```bash
docker compose up -d
```

默认：MySQL `127.0.0.1:3306`，root 密码 `root`，数据库 `genai_edu`。

## 2) 配置环境变量

复制 `.env.example` 为 `.env`，并修改 `JWT_SECRET_KEY`：

```bash
cp .env.example .env
```

## 3) 安装依赖并启动 FastAPI

建议创建虚拟环境：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- 健康检查：`GET http://127.0.0.1:8000/health`

> 注意：MVP 会在启动时自动 `create_all` 创建表结构（生产建议改用 Alembic）。

## 4) 与前端对接的接口

- `POST /auth/register` {username,password}
- `POST /auth/login` {username,password} -> {token,user}
- `GET /documents`
- `POST /documents/upload` (form-data file)
- `POST /documents/{id}/process`  入库（占位解析 + 切分 + 写 chunks 表）
- `DELETE /documents/{id}`
- `POST /qa/ask` {question,top_k} -> {answer,citations}
- `GET /history`

## 5) 重要说明（占位实现的限制）

- 目前 `process` 只对 `.txt/.md` 做真实读取；`pdf/docx` 暂时返回“占位提示”。
- 目前检索是“关键词重叠”简化版；后续你应替换为 embedding + 向量库（FAISS/Milvus/Qdrant 等）。
- 目前回答是“示例回答”，后续替换为真正 LLM + RAG 提示词。
## 3) 安装依赖并启动后端

建议使用虚拟环境：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

启动后访问：
- 健康检查：`GET http://127.0.0.1:8000/health`
- 接口文档（Swagger）：`http://127.0.0.1:8000/docs`

## 4) 与前端对接（接口清单）

- `POST /auth/register`
- `POST /auth/login`
- `GET /documents`
- `POST /documents/upload`（form-data: file）
- `POST /documents/{id}/process`（占位：txt/md可解析）
- `DELETE /documents/{id}`
- `POST /qa/ask`（占位回答 + 引用示例）
- `GET /history`

## 5) 重要说明（你后续要做的真实实现）

- 目前 `process` 只对 `.txt` / `.md` 做真实抽取；PDF/DOCX 是占位字符串（你后续实现解析即可）。
- 目前检索是“关键词重叠计分”的最小实现；后续替换为向量检索（FAISS/Milvus/Qdrant/pgvector）+ 重排。
- 目前 `qa/ask` 不调用大模型，只返回占位答案 + 引用列表；后续替换为真实 LLM + RAG Prompt。
- `POST /documents/upload`（form-data: file）
- `POST /documents/{id}/process`（占位：txt/md 可解析；pdf/docx 暂提示实现解析器）
- `DELETE /documents/{id}`
- `POST /qa/ask`（占位：用“关键词重叠检索”从 chunks 取证据，并返回示例答案 + citations）
- `GET /history`

## 5) 说明：占位实现有哪些、你后面要替换哪里

1) **解析器占位**：`app/services/doc_processing.py`：目前只支持 `.txt/.md`，pdf/docx 需要后续加解析库。
2) **检索占位** `app/services/retrieval.py`：目前是简单关键词重叠评分，后续替换为“向量检索 + rerank”。
3) **生成占位** `app/services/qa.py`：目前返回固定说明文案，后续替换为大模型 API 调用 + RAG Prompt。

