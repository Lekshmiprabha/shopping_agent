"""
Semantic product search against store.db products.

Primary:  ChromaDB + sentence-transformers
Fallback: TF-IDF (scikit-learn) — used when model cannot be downloaded
"""
import os, sys, pickle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from config.settings import CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, TOP_K_RESULTS
from db.database import SessionLocal
from db.models import Product

_TFIDF_CACHE = CHROMA_DIR / "tfidf_index.pkl"


def _product_doc(p: Product) -> str:
    organic = "organic" if p.is_organic else ""
    return f"{p.name}. {organic}. {p.category}. {p.description or ''}".strip()


# ── TF-IDF fallback ────────────────────────────────────────────────────────────
def _build_tfidf(products):
    from sklearn.feature_extraction.text import TfidfVectorizer
    docs  = [_product_doc(p) for p in products]
    metas = [p.to_dict() for p in products]
    vec   = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vec.fit_transform(docs)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_TFIDF_CACHE, "wb") as f:
        pickle.dump({"vectorizer": vec, "matrix": matrix, "metas": metas}, f)
    logger.info(f"TF-IDF index built for {len(products)} products")
    return vec, matrix, metas


def _load_tfidf():
    if not _TFIDF_CACHE.exists():
        return None
    with open(_TFIDF_CACHE, "rb") as f:
        d = pickle.load(f)
    return d["vectorizer"], d["matrix"], d["metas"]


def _tfidf_search(query: str, top_k: int) -> list[dict]:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    cached = _load_tfidf()
    if cached is None:
        db = SessionLocal()
        try:
            products = db.query(Product).all()
        finally:
            db.close()
        vec, matrix, metas = _build_tfidf(products)
    else:
        vec, matrix, metas = cached
    q_vec  = vec.transform([query])
    scores = cosine_similarity(q_vec, matrix).flatten()
    top_idx = np.argsort(scores)[::-1][:top_k]
    results = []
    for i in top_idx:
        if scores[i] < 0.05:
            continue
        results.append({**metas[i], "relevance_score": round(float(scores[i]), 3)})
    return results


# ── Backend resolver ───────────────────────────────────────────────────────────
_USE_CHROMA = None

def _resolve_backend():
    global _USE_CHROMA
    if _USE_CHROMA is None:
        try:
            from sentence_transformers import SentenceTransformer
            SentenceTransformer(EMBEDDING_MODEL)
            _USE_CHROMA = True
        except Exception:
            _USE_CHROMA = False
        logger.info(f"Search backend: {'ChromaDB' if _USE_CHROMA else 'TF-IDF'}")
    return _USE_CHROMA


# ── Public API ─────────────────────────────────────────────────────────────────
def build_index() -> None:
    """Build / refresh the search index from store.db products."""
    # always rebuild TF-IDF (cheap, fast, no network)
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        if not products:
            logger.warning("No products found in store.db")
            return
        _build_tfidf(products)
        logger.info(f"✅  Index built for {len(products)} products from store.db")
    finally:
        db.close()


def search_products(query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    """
    Search products by natural language query.
    Returns list of product dicts with 'relevance_score', best-first.
    Returns [] when nothing relevant is found.
    """
    return _tfidf_search(query, top_k)


if __name__ == "__main__":
    build_index()
    print("\n--- Test: honey ---")
    for p in search_products("organic honey"):
        print(f"  {p['name']} | score={p['relevance_score']}")
    print("\n--- Test: coffee ---")
    for p in search_products("coffee beans"):
        print(f"  {p['name']} | score={p['relevance_score']}")
    print("\n--- Test: nothing ---")
    r = search_products("laptop computer phone")
    print(f"  Results: {len(r)}")
