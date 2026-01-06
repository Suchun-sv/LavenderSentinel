# LavenderSentinel Backend

FastAPI backend for LavenderSentinel.

## Development Setup with uv

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Setup Environment

```bash
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
uv pip install -e ".[dev]"
```

### Run Development Server

```bash
# Make sure virtual environment is activated
uvicorn app.main:app --reload
```

### Sync Dependencies (after pyproject.toml changes)

```bash
uv pip sync
```

## Environment Variables

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `QDRANT_HOST` / `QDRANT_PORT` - Vector database
- `LLM_API_KEY` - OpenAI/Anthropic API key

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Pydantic Settings
│   ├── models/          # Pydantic data models
│   ├── routers/         # API routes
│   ├── services/        # Business logic
│   ├── indexing/        # CocoIndex integration
│   ├── db/              # Database layer
│   └── core/            # Core utilities
├── tests/               # Test files
└── pyproject.toml       # Dependencies
```

## Running Tests

```bash
uv pip install -e ".[dev]"
pytest
```

