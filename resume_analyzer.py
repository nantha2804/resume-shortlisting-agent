from __future__ import annotations

import os
import re
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_groq import ChatGroq
except Exception:  # pragma: no cover
    ChatGroq = None

SKILL_KEYWORDS = [
    "python",
    "sql",
    "aws",
    "docker",
    "kubernetes",
    "langchain",
    "langgraph",
    "fastapi",
    "flask",
    "ai",
    "machine learning",
    "ml",
    "data science",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "javascript",
    "typescript",
    "react",
    "node",
    "nodejs",
    "mongodb",
    "postgresql",
    "mysql",
    "redis",
    "spark",
    "airflow",
    "azure",
    "gcp",
    "linux",
    "rest api",
    "api",
    "pytest",
    "ci/cd",
    "git",
    "graphql",
    "microservices",
    "etl",
]


def normalize_text(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip().lower())


def extract_skills(text: str) -> List[str]:
    text_norm = normalize_text(text)
    found = []
    for skill in SKILL_KEYWORDS:
        if skill in text_norm:
            found.append(skill)
    return found


def estimate_score(resume_text: str, job_description: str) -> Dict[str, Any]:
    resume_norm = normalize_text(resume_text)
    jd_norm = normalize_text(job_description)

    required_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)
    matched = sorted(set(required_skills) & set(resume_skills))
    missing = sorted(set(required_skills) - set(resume_skills))

    if not required_skills:
        required_skills = ["python", "sql", "aws", "api"]

    score = round((len(matched) / max(len(required_skills), 1)) * 100)
    score = max(0, min(score, 100))

    if score >= 80:
        decision = "Shortlist"
    elif score >= 55:
        decision = "Human Review"
    else:
        decision = "Reject"

    strengths = []
    for skill in matched[:5]:
        strengths.append(f"Has relevant experience in {skill}.")

    if not strengths:
        strengths = ["Resume does not strongly match the job requirements yet."]

    suggestions = []
    if missing:
        suggestions.append(f"Add more evidence for: {', '.join(missing[:5])}.")
    if "python" not in resume_skills and "python" in required_skills:
        suggestions.append("Mention Python projects or practical implementation examples.")
    if "sql" not in resume_skills and "sql" in required_skills:
        suggestions.append("Add database/query experience with SQL in projects or work history.")
    if "aws" not in resume_skills and "aws" in required_skills:
        suggestions.append("Highlight cloud deployment, hosting, or infrastructure exposure.")
    if not suggestions:
        suggestions.append("Keep experience statements impact-focused and quantify results with numbers.")

    key_points = [
        f"Matched skills: {', '.join(matched[:5]) if matched else 'none'}",
        f"Missing skills: {', '.join(missing[:5]) if missing else 'none'}",
        f"Resume fit: {score}/100",
        f"Recommendation: {decision}",
    ]

    result = {
        "score": score,
        "decision": decision,
        "matched_skills": matched,
        "missing_skills": missing,
        "strengths": strengths,
        "suggestions": suggestions,
        "key_points": key_points,
        "resume_summary": resume_norm[:500],
    }

    return result


def llm_review_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    if not os.getenv("GROQ_API_KEY") or ChatGroq is None:
        return {} 

    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
        prompt = (
            "Review this resume against the job description. "
            "Return JSON with keys: score, decision, strengths, suggestions, key_points. "
            "Score should be 0 to 100, decision should be Shortlist/Human Review/Reject.\n\n"
            f"JOB DESCRIPTION:\n{job_description}\n\nRESUME:\n{resume_text}"
        )
        response = llm.invoke(prompt)
        text = getattr(response, "content", str(response))
        return {"llm_feedback": text}
    except Exception:
        return {}


def review_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    base_result = estimate_score(resume_text, job_description)
    llm_data = llm_review_resume(resume_text, job_description)
    if llm_data:
        base_result.update(llm_data)
    return base_result
