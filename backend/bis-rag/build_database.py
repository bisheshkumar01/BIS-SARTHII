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
DB_FILE = "bis_vector_store.pkl"


def load_documents(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_database():
    docs = load_documents(SOURCE_FILE)
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
