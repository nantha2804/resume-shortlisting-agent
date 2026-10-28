from __future__ import annotations

import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from resume_analyzer import extract_resume_text, generate_tailored_resume, review_resume

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc", ".png", ".jpg", ".jpeg"}

app = FastAPI(title="Resume Shortlisting Agent API", version="1.0.0")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allowed_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "resume-shortlisting-agent"}


@app.post("/review")
async def review(
    job_description: str = Form(...),
    resume: UploadFile = File(...),
) -> dict:
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    filename = resume.filename or "resume"
    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported resume file type.")

    file_bytes = await resume.read(MAX_FILE_SIZE + 1)
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Resume file must be 10 MB or smaller.")

    try:
        resume_text = extract_resume_text(file_bytes, filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="No readable text was found in the resume.")

    return {
        "review": review_resume(resume_text, job_description),
        "tailored_resume": generate_tailored_resume(resume_text, job_description),
        "filename": filename,
    }
