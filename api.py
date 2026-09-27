from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from resume_analyzer import review_resume

app = FastAPI(title="Resume Review API", version="1.0.0")


class ReviewRequest(BaseModel):
    resume: str
    job_description: str


class ReviewResponse(BaseModel):
    score: int
    decision: str
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    suggestions: list[str]
    key_points: list[str]


@app.get("/")
def root():
    return {"message": "Resume Review API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
def review_api(payload: ReviewRequest):
    result = review_resume(payload.resume, payload.job_description)
    return ReviewResponse(
        score=result["score"],
        decision=result["decision"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        strengths=result["strengths"],
        suggestions=result["suggestions"],
        key_points=result["key_points"],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
