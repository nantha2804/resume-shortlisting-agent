from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from resume_analyzer import extract_resume_text, generate_tailored_resume, review_resume

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".webp"}

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
async def review(request: Request) -> dict:
    """Review either the browser's JSON payload or a multipart file upload."""
    content_type = request.headers.get("content-type", "")
    resume_filename = "pasted-resume.txt"

    if content_type.startswith("application/json"):
        payload = await request.json()
        job_description = str(payload.get("job_description", ""))
        resume_text = str(payload.get("resume", ""))
    else:
        form = await request.form()
        job_description = str(form.get("job_description", ""))
        uploaded_resume = form.get("resume")
        if not isinstance(uploaded_resume, UploadFile):
            raise HTTPException(status_code=400, detail="A resume file is required.")

        resume_filename = uploaded_resume.filename or "resume"
        extension = os.path.splitext(resume_filename)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported resume file type.")

        file_bytes = await uploaded_resume.read(MAX_FILE_SIZE + 1)
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Resume file must be 5 MB or smaller.")

        try:
            resume_text = extract_resume_text(file_bytes, resume_filename)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="No readable text was found in the resume.")

    review_result = review_resume(resume_text, job_description)
    return {
        **review_result,
        "tailored_resume": generate_tailored_resume(resume_text, job_description),
        "filename": resume_filename,
    }
