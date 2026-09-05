"""
build_database.py
------------------
Builds a simple local vector database from bis_documents.json.

Uses TF-IDF vectors (scikit-learn) instead of a neural embedding model so
this runs fully offline with no API keys or downloads. You can swap in
OpenAI/Cohere/sentence-transformers embeddings later by replacing the
`vectorize()` function — the rest of the pipeline (store, retrieve) stays
the same.

Run:
    python3 build_database.py
Creates:
    bis_vector_store.pkl   <- the "database" (vectors + text + metadata)
"""

import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

SOURCE_FILE = "bis_documents.json"
CRS_PRODUCTS_FILE = "bis_crs_products.json"
DB_FILE = "bis_vector_store.pkl"


def load_documents(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def crs_products_to_chunks(products):
    """Turn each CRS product row into a retrievable text chunk."""
    chunks = []
    for p in products:
        text = (
            f"The product '{p['product']}' falls under BIS's Compulsory Registration "
            f"Scheme (CRS) and must comply with {p['is_number']}. "
            f"This requirement has been in effect since {p['date_of_implementation']}."
        )
        chunks.append({
            "id": f"crs_{p['sl_no']}",
            "title": f"CRS requirement: {p['product']}",
            "text": text,
        })
    return chunks


def build_database():
    docs = load_documents(SOURCE_FILE)
    crs_products = load_documents(CRS_PRODUCTS_FILE)
    docs = docs + crs_products_to_chunks(crs_products)

    texts = [f"{d['title']}. {d['text']}" for d in docs]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    doc_vectors = vectorizer.fit_transform(texts)

    store = {
        "vectorizer": vectorizer,   # fitted TF-IDF model (acts as the embedder)
        "doc_vectors": doc_vectors,  # sparse matrix, one row per chunk
        "documents": docs,           # original text + metadata
    }

    with open(DB_FILE, "wb") as f:
        pickle.dump(store, f)

    print(f"Indexed {len(docs)} chunks -> {DB_FILE}")


if __name__ == "__main__":
    build_database()
