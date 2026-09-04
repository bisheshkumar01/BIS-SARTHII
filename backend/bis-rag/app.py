from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from full_rag import answer_question


app = FastAPI(
    title="BIS Sarthi API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "BIS Sarthi API is running"
    }


@app.post("/ask")
def ask_question(data: Question):

    try:

        answer, sources = answer_question(
            data.question
        )

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

        from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from full_rag import answer_question


app = FastAPI(title="BIS Sarthi API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "BIS Sarthi API is running"
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
                    "title": source.get("title", "Unknown document")
                }
                for source in sources
            ],
            "next_steps": [],
            "warnings": []
        }

    except Exception as e:
        print("ERROR:", e)

        return {
            "answer": "Sorry, I could not process your question.",
            "error": str(e),
            "message_id": None,
            "confidence": "low",
            "citations": [],
            "next_steps": [],
            "warnings": []
        }


@app.get("/api/chat/{session_id}/history")
def chat_history(session_id: str):
    return {
        "messages": []
    }


@app.post("/api/feedback")
def feedback(data: dict):
    return {
        "status": "ok"
    }