"""
query.py
--------
Retrieval (and optional generation) over the BIS vector database.

Retrieval-only:
    python3 query.py "documents needed for BIS CRS registration"

With generation (needs ANTHROPIC_API_KEY set in your environment):
    python3 query.py "documents needed for BIS CRS registration" --answer
"""

import sys
import pickle
from sklearn.metrics.pairwise import cosine_similarity

DB_FILE = "bis_vector_store.pkl"


def load_database():
    with open(DB_FILE, "rb") as f:
        return pickle.load(f)


def retrieve(query, store, top_k=3):
    vectorizer = store["vectorizer"]
    doc_vectors = store["doc_vectors"]
    documents = store["documents"]

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, doc_vectors)[0]

    ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
    return ranked[:top_k]


def generate_answer(query, context_chunks):
    """Optional: send retrieved context + query to Claude for a final answer.
    Requires: pip install anthropic --break-system-packages
              export ANTHROPIC_API_KEY=your_key
    """
    import anthropic

    client = anthropic.Anthropic()
    context = "\n\n".join(f"[{c['title']}] {c['text']}" for c in context_chunks)

    prompt = f"""Answer the question using only the context below. Be concise.

Context:
{context}

Question: {query}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 query.py "your question" [--answer]')
        sys.exit(1)

    query = sys.argv[1]
    want_answer = "--answer" in sys.argv

    store = load_database()
    results = retrieve(query, store, top_k=3)

    print(f"\nTop matches for: {query!r}\n" + "-" * 50)
    context_chunks = []
    for score, doc in results:
        print(f"[{score:.3f}] {doc['title']}")
        print(f"  {doc['text']}\n")
        context_chunks.append(doc)

    if want_answer:
        print("-" * 50)
        print("Generating answer...\n")
        print(generate_answer(query, context_chunks))


if __name__ == "__main__":
    main()
