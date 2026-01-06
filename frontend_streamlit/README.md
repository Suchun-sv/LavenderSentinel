# LavenderSentinel - Streamlit Frontend

A simple Python-based UI for the academic paper management system.

## 🚀 Quick Start

### Install Dependencies

```bash
cd frontend_streamlit

# Using pip
pip install -r requirements.txt

# Or using uv
uv pip install -r requirements.txt
```

### Run the App

```bash
# Make sure backend is running first
docker compose up -d postgres redis qdrant backend

# Run Streamlit
streamlit run app.py
```

The app will be available at http://localhost:8501

### Configure Backend URL

Create `.streamlit/secrets.toml`:

```toml
API_BASE_URL = "http://localhost:8000/api/v1"
```

## 📁 Project Structure

```
frontend_streamlit/
├── app.py              # Main entry point
├── pages_config.py     # Page configuration & styling
├── api_client.py       # Backend API client
├── views/              # Page views
│   ├── home.py         # Home page
│   ├── search.py       # Search page
│   ├── papers.py       # Papers listing
│   └── chat.py         # Chat interface
├── requirements.txt    # Python dependencies
└── README.md
```

## 🐳 Docker Support

### Build and Run

```bash
docker build -t lavender-streamlit -f Dockerfile.streamlit .
docker run -p 8501:8501 lavender-streamlit
```

### With Docker Compose

Add to `docker-compose.yml`:

```yaml
streamlit:
  build:
    context: ./frontend_streamlit
    dockerfile: Dockerfile
  container_name: lavender-streamlit
  ports:
    - "8501:8501"
  environment:
    - API_BASE_URL=http://backend:8000/api/v1
  depends_on:
    - backend
```

## 🎨 Features

- **🏠 Home** - Dashboard with stats and recent papers
- **🔍 Search** - Semantic search with filters
- **📚 Papers** - Browse and manage paper collection
- **💬 Chat** - AI-powered research assistant with RAG

## 🔧 Customization

### Styling

Edit `pages_config.py` to customize:
- Colors and theme
- CSS styles
- Page layout

### API Client

Edit `api_client.py` to:
- Add new API endpoints
- Modify request handling
- Add authentication


