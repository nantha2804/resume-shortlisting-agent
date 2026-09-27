from __future__ import annotations

import streamlit as st

from resume_analyzer import review_resume

st.set_page_config(page_title="Resume Review Agent", page_icon="📄", layout="wide")

st.title("Resume Review & Shortlisting Agent")
st.markdown("Paste a job description and a resume to get a fit score, key points, and suggestions.")

with st.form("resume_form"):
    job_description = st.text_area(
        "Job Description",
        height=220,
        value=(
            "Looking for Python developer with experience in SQL, AWS, FastAPI, LangGraph, "
            "Docker, and cloud deployment."
        ),
    )
    resume_text = st.text_area(
        "Resume",
        height=360,
        value=(
            "Python Developer with experience in SQL, FastAPI, Docker, AWS, and API development. "
            "Worked on backend services, data pipelines, and cloud deployment."
        ),
    )
    submitted = st.form_submit_button("Review Resume")

if submitted:
    if not job_description.strip() or not resume_text.strip():
        st.warning("Please provide both a job description and a resume.")
    else:
        result = review_resume(resume_text, job_description)

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", f"{result['score']}/100")
        col2.metric("Decision", result["decision"])
        col3.metric("Matched Skills", len(result["matched_skills"]))

        st.subheader("Key Points")
        for item in result["key_points"]:
            st.write("•", item)

        st.subheader("Strengths")
        for item in result["strengths"]:
            st.write("•", item)

        st.subheader("Suggestions")
        for item in result["suggestions"]:
            st.write("•", item)

        st.subheader("Matched Skills")
        st.write(", ".join(result["matched_skills"]) if result["matched_skills"] else "No direct matches")

        st.subheader("Missing Skills")
        st.write(", ".join(result["missing_skills"]) if result["missing_skills"] else "No major missing skills found")

        if "llm_feedback" in result:
            st.subheader("LLM Review")
            st.write(result["llm_feedback"])
