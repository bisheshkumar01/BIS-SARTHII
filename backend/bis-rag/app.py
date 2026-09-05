from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import easyocr
import tempfile
import os

from full_rag import answer_question


app = FastAPI(title="BIS Sarthi API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


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


reader = easyocr.Reader(['en'])


@app.post("/api/scan")
async def scan_product(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            contents = await file.read()
            temp.write(contents)
            temp_path = temp.name

        results = reader.readtext(temp_path)

        extracted_text = [
            text for _, text, confidence in results
            if confidence > 0.3
        ]

        os.remove(temp_path)

        return {
            "filename": file.filename,
            "extracted_text": extracted_text
        }

    except Exception as e:
        return {
            "error": str(e),
            "extracted_text": []
        }