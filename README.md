# 📖 WhiteNote

> **像刷小红书一样刷论文**  
> *Scroll through papers like you scroll through social media*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.52+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/PostgreSQL-16-blue.svg" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-7-red.svg" alt="Redis">
</p>

---

## ✨ Features

### 📚 论文获取 Paper Fetching
- **arXiv 自动抓取**：根据关键词定时从 arXiv 获取最新论文
- **关键词订阅**：自定义关注的研究方向（如 RAG、Agent、Vector Database）
- **定时任务**：每日自动更新，不错过任何重要论文

### 🎨 AI 漫画解读 AI Comic Interpretation
- **一键生成漫画**：将枯燥的论文转化为易懂的 10 格漫画
- **Gemini 驱动**：使用 Google Gemini 生成精美插图
- **全文理解**：基于论文全文内容生成，而非仅摘要

### 🧠 AI 智能分析 AI Analysis
- **摘要翻译**：将英文摘要翻译为中文
- **全文总结**：PDF 解析 + AI 生成结构化总结
- **论文问答**：基于论文内容的多轮对话，支持流式输出

### ⭐ 收藏管理 Collection Management
- **多文件夹收藏**：创建多个收藏夹分类管理论文
- **自动处理流水线**：收藏后自动下载 PDF → 生成总结 → 生成漫画
- **不喜欢标记**：过滤不感兴趣的论文

### 📋 任务监控 Task Monitoring
- **队列可视化**：查看 AI 总结和漫画生成任务状态
- **日志追踪**：实时查看后台任务日志
- **失败重试**：一键重试失败的任务

---

## 🚀 Quick Start

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-repo/WhiteNote.git
cd WhiteNote

# 启动依赖服务 (PostgreSQL + Redis + Qdrant)
docker-compose up -d
```

### 2. 安装依赖

```bash
cd backend

# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -e .
```

### 3. 配置

编辑 `backend/settings.yaml`：

```yaml
# 语言设置
language: "中文（简体）"

# 关键词订阅
keywords:
  - "RAG"
  - "agent"
  - "vector database"

# LLM 配置 (用于翻译/总结/问答)
chat_litellm:
  model: "gpt-4o-mini"
  api_key: "your-openai-api-key"
  api_base: "https://api.openai.com/v1"

# Gemini 配置 (用于漫画生成)
gemini:
  api_key: "your-gemini-api-key"
  model: "gemini-2.0-flash-preview-image-generation"
```

创建 `backend/.env` 文件（可选，覆盖 yaml 配置）：

```bash
GEMINI__API_KEY=your-gemini-api-key
DATABASE_URL=postgresql://whitenote:whitenote_password@localhost:5432/whitenote
```

### 4. 初始化数据库

```bash
cd backend
uv run python -m src.scripts.init_db
```

### 5. 启动服务

**终端 1：启动 RQ Worker（后台任务处理）**

```bash
cd backend
uv run supervisord -c supervisord.conf
```

**终端 2：启动 Streamlit 应用**

```bash
cd backend
uv run streamlit run app.py
```

访问 http://localhost:8501 🎉

---

## 📁 项目结构

```
WhiteNote/
├── docker-compose.yaml      # PostgreSQL + Redis + Qdrant
├── backend/
│   ├── app.py               # 主应用入口
│   ├── settings.yaml        # 配置文件
│   ├── supervisord.conf     # RQ Worker 管理
│   ├── worker.py            # RQ Worker 入口
│   ├── pages/
│   │   ├── 1_Page_Detail.py # 论文详情页
│   │   └── 2_Task_Monitor.py# 任务监控页
│   └── src/
│       ├── config/          # 配置管理
│       ├── crawler/         # arXiv 爬虫
│       ├── database/        # 数据库操作
│       ├── jobs/            # 后台任务
│       ├── model/           # 数据模型
│       ├── queue/           # RQ 队列
│       ├── scheduler/       # APScheduler 定时任务
│       └── service/         # 业务服务
│           ├── chat_service.py           # 论文问答
│           ├── image_generation_service.py # 漫画生成
│           ├── llm_service.py            # LLM 封装
│           ├── pdf_download_service.py   # PDF 下载
│           └── pdf_parser_service.py     # PDF 解析
└── cache/
    ├── pdfs/                # PDF 缓存
    └── imgs/                # 漫画缓存
```

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Streamlit |
| 后端 | Python 3.11+ |
| 数据库 | PostgreSQL 16 |
| 向量库 | Qdrant |
| 任务队列 | Redis + RQ |
| 定时任务 | APScheduler |
| PDF 解析 | Marker |
| LLM | LiteLLM (支持 OpenAI/Claude/...) |
| 图片生成 | Google Gemini |

---

## 📝 常用命令

```bash
# 手动抓取 arXiv 论文
uv run python -c "from src.crawler.fetch_task import run_fetch; run_fetch()"

# 查看 RQ Worker 状态
uv run supervisorctl -c supervisord.conf status

# 重启 RQ Worker
uv run supervisorctl -c supervisord.conf restart rq-worker

# 查看 Worker 日志
tail -f logs/rq-worker.log
```

---

## 📄 License

MIT License

---

<p align="center">
  Made with ❤️ for researchers who love papers
</p>
