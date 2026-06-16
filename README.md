# AI Shopping Assistant

A local Streamlit-based shopping assistant that supports text search, image search, product details, and order history.

## Features

- Search products with natural language queries
- Image-based product search
- Product details, ratings, and ordering
- Local SQLite database for products and orders
- Semantic search powered by embeddings and Chroma
- Agent-oriented architecture using Anthropic/Claude and LangChain

## Requirements

- Python 3.10+
- `streamlit`
- `anthropic`
- `langchain`
- `chromadb`
- `sentence-transformers`
- `sqlalchemy`
- `pydantic`
- `python-dotenv`
- `pandas`
- `numpy`
- `Pillow`
- `opencv-python-headless`
- `requests`
- `httpx`
- `pytz`
- `loguru`

Install dependencies with:

```bash
pip install -r Requirements.txt
```

## Setup

1. Copy `.env.example` to `.env` in the project root.
2. Fill in your secret API keys and settings in `.env`.

Example values in `.env.example` are placeholders only and do not contain real keys.

```env
ANTHROPIC_API_KEY=your_api_key_here
GOOGLE_API_KEY=your_api_key_here
GROQ_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
HF_TOKEN=your_api_key_here
APP_NAME=Shopping_List
DEBUG=False
Langsmith_API_KEY=your_api_key_here
```

3. Ensure `config/settings.py` points to the right local paths. The app uses a local SQLite file at `db/store.db`.

> `.env` is excluded from version control by `.gitignore`.

## Run

From the project root:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Project Structure

- `app.py` — Streamlit entrypoint and tab layout
- `config/` — application settings and configuration
- `db/` — database initialization, models, and persistence
- `ui/` — Streamlit UI components and tabs
- `agents/` — search, image search, product detail, and checkout agent logic
- `vector_store/` — embedding creation and Chroma vector index

## Notes

- The app is designed for a local development environment.
- It initializes the database and builds the search index on startup.
- If you want to modify the product data or order flow, update the database models and UI modules.
