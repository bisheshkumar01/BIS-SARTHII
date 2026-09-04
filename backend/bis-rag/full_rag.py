import sys
import os
import pickle

from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from google import genai


# ============================================================
# CONFIG
# ============================================================

DB_FILE = "bis_vector_store.pkl"
MODEL = "gemini-2.5-flash"
TOP_K = 3
MAX_TOKENS = 700


# ============================================================
# LOAD .ENV
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found.")
    print("Create a .env file with:")
    print("GEMINI_API_KEY=your_api_key_here")
    sys.exit(1)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# RETRIEVE RELEVANT DOCUMENTS
# ============================================================

def retrieve(question, store, top_k=TOP_K):

    vectorizer = store["vectorizer"]
    doc_vectors = store["doc_vectors"]
    documents = store["documents"]

    question_vec = vectorizer.transform([question])

    scores = cosine_similarity(
        question_vec,
        doc_vectors
    )[0]

    ranked = sorted(
        zip(scores, documents),
        key=lambda x: x[0],
        reverse=True
    )

    return [
        doc
        for score, doc in ranked[:top_k]
    ]


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(question, chunks):

    context = "\n\n".join(
        f"[{c['title']}]\n{c['text']}"
        for c in chunks
    )

    return f"""
You are BIS Sārthi, an AI assistant for BIS
(Bureau of Indian Standards) certification and compliance.

Answer ONLY using the BIS document context provided below.

Rules:
- Do not guess.
- Do not invent requirements.
- Do not use outside information.
- If the context does not contain the answer, say:
  "The retrieved BIS documents do not contain enough information
  to answer this confidently."
- Use bullet points when listing documents.
- Clearly mention conditions or exceptions if they appear
  in the provided context.

================ BIS DOCUMENT CONTEXT ================

{context}

================ USER QUESTION ================

{question}

================ ANSWER ================
"""


# ============================================================
# CALL GEMINI
# ============================================================

def call_llm(prompt):

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "max_output_tokens": MAX_TOKENS,
                "temperature": 0.2
            }
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text

    except Exception as e:

        print("\nGemini API Error:")
        print(e)

        raise


# ============================================================
# COMPLETE RAG PIPELINE
# ============================================================

def answer_question(question):

    if not os.path.exists(DB_FILE):

        raise FileNotFoundError(
            f"Could not find {DB_FILE}. "
            "Make sure it is in the same folder."
        )

    print("\nLoading BIS vector database...")

    with open(DB_FILE, "rb") as f:
        store = pickle.load(f)

    print("Database loaded.")

    print("\nSearching BIS documents...")

    chunks = retrieve(
        question,
        store,
        TOP_K
    )

    if not chunks:

        return (
            "No relevant BIS documents were found.",
            []
        )

    print(
        f"Retrieved {len(chunks)} relevant chunks."
    )

    prompt = build_prompt(
        question,
        chunks
    )

    print("\nAsking Gemini...")

    answer = call_llm(prompt)

    return answer, chunks


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            'Usage: python full_rag.py '
            '"your question here"'
        )

        sys.exit(1)

    question = " ".join(sys.argv[1:])

    print("\n" + "=" * 60)
    print("BIS SĀRTHI")
    print("AI-Powered BIS Compliance Assistant")
    print("=" * 60)

    print("\nQuestion:", question)

    try:

        answer, sources = answer_question(
            question
        )

        print("\n" + "=" * 60)
        print("ANSWER")
        print("=" * 60)

        print(answer)

        print("\n" + "=" * 60)
        print("SOURCES USED")
        print("=" * 60)

        for source in sources:

            print(
                " -",
                source.get(
                    "title",
                    "Unknown document"
                )
            )

    except KeyboardInterrupt:

        print("\nStopped by user.")

    except Exception as e:

        print("\nERROR:")
        print(e)

        sys.exit(1)