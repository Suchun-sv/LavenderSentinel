#  🪻 LavenderSentinel
> Your reliable sentinel for academic literature.
 
<img src="./assets/lavender.jpg" alt="LavenderSentinel" width="400">

LavenderSentinel is a system that automatically collects research papers based on keywords, then encodes, indexes, and summarizes them. It provides an optimized responsive Web UI with a side-panel designed for deep LLM-assisted conversation.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![React](https://img.shields.io/badge/React-18-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **📚 Automatic Paper Collection** - Fetch papers from arXiv, Semantic Scholar, and more based on your keywords
- **🔍 Semantic Search** - Find relevant papers using natural language queries powered by vector embeddings
- **🤖 AI Summarization** - Generate concise summaries and key points for any paper
- **💬 RAG-powered Chat** - Deep conversation with an AI assistant that understands your paper collection
- **📱 Responsive UI** - Beautiful, modern interface with dark mode support
- **🔄 Real-time Indexing** - Incremental updates with CocoIndex pipeline

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│           React + TypeScript + TailwindCSS + Zustand            │
└─────────────────────────┬───────────────────────────────────────┘
                          │ REST API / WebSocket
┌─────────────────────────┴───────────────────────────────────────┐
│                         Backend                                  │
│              FastAPI + Pydantic + CocoIndex                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Collector   │  │  Summarizer  │  │   Chat Service       │  │
│  │  (论文采集)   │  │  (摘要生成)   │  │   (RAG 对话)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              │      CocoIndex Pipeline       │                  │
│              │  (Embedding → Vector Index)   │                  │
│              └───────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   PostgreSQL         Qdrant            Redis
   (Metadata)       (Vectors)          (Cache)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (recommended)

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/LavenderSentinel.git
cd LavenderSentinel

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Set environment variables (copy from .env.example)
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📁 Project Structure

```
LavenderSentinel/
├── backend/
│   ├── app/
│   │   ├── config.py           # Pydantic Settings
│   │   ├── main.py             # FastAPI entry point
│   │   ├── models/             # Pydantic data models
│   │   ├── routers/            # API routes
│   │   ├── services/           # Business logic
│   │   ├── indexing/           # CocoIndex integration
│   │   ├── db/                 # Database layer
│   │   └── core/               # Core utilities
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── stores/             # Zustand stores
│   │   ├── hooks/              # Custom hooks
│   │   └── types/              # TypeScript types
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## 🔧 Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend Framework** | FastAPI + Pydantic v2 |
| **Indexing Engine** | CocoIndex + Qdrant |
| **Database** | PostgreSQL + SQLAlchemy (async) |
| **Cache** | Redis |
| **LLM Integration** | LiteLLM (OpenAI, Anthropic, Ollama) |
| **Frontend Framework** | React 18 + TypeScript |
| **State Management** | Zustand + TanStack Query |
| **Styling** | TailwindCSS |

## ⚙️ Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `QDRANT_HOST` | Qdrant host | `localhost` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `LLM_PROVIDER` | LLM provider (openai/anthropic/ollama) | `openai` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |
| `LLM_API_KEY` | LLM API key | - |
| `EMBEDDING_MODEL` | Sentence transformer model | `BAAI/bge-base-en-v1.5` |

## 📖 API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/papers` | List papers with pagination |
| `POST` | `/api/v1/search/semantic` | Semantic search |
| `POST` | `/api/v1/chat` | Send chat message |
| `POST` | `/api/v1/chat/stream` | Stream chat response (SSE) |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CocoIndex](https://github.com/cocoindex/cocoindex) - Data indexing framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Qdrant](https://qdrant.tech/) - Vector database
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
