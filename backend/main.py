from fastapi import FastAPI, UploadFile, File
import shutil
import os

from ocr import extract_text

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "BIS SĀRTHI Backend Running"
    }


@app.post("/api/scan")
async def scan_product(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_path)

    return {
        "filename": file.filename,
        "extracted_text": text
    }