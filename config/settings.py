import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DB_DIR    = BASE_DIR / "db"
DB_PATH   = DB_DIR / "store.db"
DB_URL    = f"sqlite:///{DB_PATH}"

CHROMA_DIR        = BASE_DIR / "vector_store" / "chroma_data"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL      = "claude-sonnet-4-6"
EMBEDDING_MODEL   = "all-MiniLM-L6-v2"
CHROMA_COLLECTION = "store_products"
TOP_K_RESULTS     = 10
APP_TITLE         = "AI Shopping Assistant"
APP_ICON          = "🛒"
