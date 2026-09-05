from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import easyocr
import pickle
import tempfile
import os

from sklearn.metrics.pairwise import cosine_similarity

from full_rag import answer_question, retrieve, call_llm


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "bis_vector_store.pkl")


# ============================================================
# APP
# ============================================================

app = FastAPI(title="BIS Sarthi API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELS
# ============================================================

class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"


class StandardsRequest(BaseModel):
    query: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "status": "success",
        "message": "BIS Sarthi API is running"
    }


# ============================================================
# CHAT
# ============================================================

@app.post("/ask")
def ask_question(data: Question):

    try:

        answer, sources = answer_question(data.question)

        return {
            "question": data.question,
            "answer": answer,
            "sources": [
                source.get("title", "Unknown")
                for source in sources
            ]
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@app.post("/api/chat")
def chat(request: ChatRequest):

    try:

        answer, sources = answer_question(request.message)

        return {
            "answer": answer,
            "message_id": None,
            "confidence": "high",

            "citations": [
                {
                    "title": source.get(
                        "title",
                        "Unknown document"
                    )
                }
                for source in sources
            ],

            "next_steps": [],

            "warnings": []
        }

    except Exception as e:

        print("CHAT ERROR:", e)

        return {
            "answer": "Sorry, I could not process your question.",
            "error": str(e),
            "message_id": None,
            "confidence": "low",
            "citations": [],
            "next_steps": [],
            "warnings": []
        }


# ============================================================
# CHAT HISTORY
# ============================================================

@app.get("/api/chat/{session_id}/history")
def chat_history(session_id: str):

    return {
        "messages": []
    }


# ============================================================
# FEEDBACK
# ============================================================

@app.post("/api/feedback")
def feedback(data: dict):

    return {
        "status": "ok"
    }


# ============================================================
# OCR SCANNER
# ============================================================

print("Loading EasyOCR...")

reader = easyocr.Reader(["en"])

print("EasyOCR ready.")


@app.post("/api/scan")
async def scan_product(file: UploadFile = File(...)):

    temp_path = None

    try:

        suffix = os.path.splitext(
            file.filename or ""
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp:

            contents = await file.read()

            temp.write(contents)

            temp_path = temp.name


        results = reader.readtext(temp_path)


        extracted_text = [
            text
            for _, text, confidence in results
            if confidence > 0.3
        ]


        return {
            "filename": file.filename,
            "extracted_text": extracted_text
        }


    except Exception as e:

        print("OCR ERROR:", e)

        return {
            "error": str(e),
            "extracted_text": []
        }


    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


# ============================================================
# STANDARDS SEARCH
# ============================================================

@app.post("/api/standards")
def find_standards(request: StandardsRequest):

    try:

        query = request.query.strip()

        if not query:

            return {
                "matches": []
            }


        print("\n========================================")
        print("STANDARDS SEARCH")
        print("Query:", query)
        print("========================================")


        # ----------------------------------------------------
        # LOAD VECTOR DATABASE
        # ----------------------------------------------------

        with open(DB_FILE, "rb") as f:

            store = pickle.load(f)


        # ----------------------------------------------------
        # RETRIEVE RELEVANT BIS DOCUMENTS
        # ----------------------------------------------------

        chunks = retrieve(
            query,
            store,
            top_k=10
        )


        if not chunks:

            return {
                "query": query,
                "matches": []
            }


        # ----------------------------------------------------
        # GET SIMILARITY SCORES
        # ----------------------------------------------------

        vectorizer = store["vectorizer"]

        doc_vectors = store["doc_vectors"]

        documents = store["documents"]


        question_vec = vectorizer.transform([query])


        scores = cosine_similarity(
            question_vec,
            doc_vectors
        )[0]


        ranked = sorted(
            zip(scores, documents),
            key=lambda x: x[0],
            reverse=True
        )


        # ----------------------------------------------------
        # CREATE BASIC MATCH DATA
        # ----------------------------------------------------

        matches = []


        for score, doc in ranked[:10]:

            title = doc.get(
                "title",
                "Unknown BIS document"
            )


            matches.append({

                "isNumber": title,

                "title": title,

                "score": round(
                    float(score) * 100
                ),

                "scheme": "BIS document",

                "why": [
                    "This document was retrieved as relevant to the product description."
                ],

                "url": doc.get("url")

            })


        # ----------------------------------------------------
        # ASK GEMINI TO EXPLAIN THE RESULTS
        # ----------------------------------------------------

        context = "\n\n".join(

            f"""
DOCUMENT {i + 1}

Title:
{doc.get("title", "Unknown")}

Content:
{doc.get("text", "")}
"""

            for i, doc in enumerate(chunks)
        )


        prompt = f"""
You are BIS Sarthi, a BIS compliance assistant.

The user wants to find applicable BIS standards.

USER PRODUCT DESCRIPTION:
{query}


Below are documents retrieved from the BIS vector database.

================ BIS DOCUMENTS ================

{context}

=================================================


TASK:

For each retrieved document:

1. Explain briefly why it may be relevant to the user's product.
2. Do NOT invent requirements.
3. Do NOT invent certification schemes.
4. Do NOT claim that certification is mandatory unless the retrieved document explicitly supports that.
5. If the retrieved document does not contain enough information, say so.
6. Base your explanation ONLY on the supplied BIS document content.

Return the result as a numbered list.

Format:

1. DOCUMENT TITLE
Why it may apply: ...
Important information: ...

2. DOCUMENT TITLE
Why it may apply: ...
Important information: ...
"""


        try:

            explanation = call_llm(prompt)

            print("\nGemini standards explanation:")
            print(explanation)


            # Put Gemini's overall explanation into the response.
            # The frontend can display it later.

            return {
                "query": query,
                "matches": matches,
                "explanation": explanation
            }


        except Exception as gemini_error:

            print(
                "Gemini standards explanation failed:",
                gemini_error
            )

            return {
                "query": query,
                "matches": matches,
                "explanation": None
            }


    except Exception as e:

        print(
            "STANDARDS SEARCH ERROR:",
            e
        )

        return {
            "matches": [],
            "error": str(e)
        }