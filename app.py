from __future__ import annotations

def generate_pdf(content: str) -> bytes:
    """Create a simple, readable PDF from generated resume text."""
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=0.65 * inch, leftMargin=0.65 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    body = getSampleStyleSheet()["BodyText"]
    body.leading = 14
    story = []
    for block in content.split("\n"):
        text = block.strip()
        if text:
            story.extend([Paragraph(text.replace("&", "&amp;"), body), Spacer(1, 6)])
    document.build(story)
    return buffer.getvalue()

import io

import streamlit as st

from resume_analyzer import extract_resume_text, generate_tailored_resume, review_resume

MAX_FILE_SIZE = 10 * 1024 * 1024
SUPPORTED_TYPES = ["pdf", "txt", "docx", "doc", "png", "jpg", "jpeg"]

st.set_page_config(page_title="Resume Review Agent", page_icon="📄", layout="wide")
st.title("Resume Review & Shortlisting Agent")
st.markdown("Upload a resume, paste a job description, and get an instant tailored resume draft and fit review.")

with st.form("resume_form"):
    job_description = st.text_area("Job Description", height=220, placeholder="Paste the complete job description here...")
    uploaded_file = st.file_uploader("Choose a resume file (maximum 10 MB)", type=SUPPORTED_TYPES, help="Supported: PDF, TXT, DOCX, DOC, PNG, JPG, and JPEG.")
    manual_resume = st.text_area("Or paste resume text", height=220, placeholder="Use this when you do not want to upload a file.")
    submitted = st.form_submit_button("Generate & Review Resume", type="primary")

if submitted:
    if not job_description.strip():
        st.warning("Please provide a job description.")
        st.stop()
    if uploaded_file is not None and uploaded_file.size > MAX_FILE_SIZE:
        st.error("This file is larger than 10 MB. Please upload a smaller file.")
        st.stop()
    if uploaded_file is not None:
        try:
            resume_text = extract_resume_text(uploaded_file.getvalue(), uploaded_file.name)
            st.caption(f"Read {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        except ValueError as exc:
            st.error(str(exc))
            st.stop()
    else:
        resume_text = manual_resume.strip()
    if not resume_text:
        st.warning("Please upload a resume file or paste resume text.")
        st.stop()

    with st.spinner("Analyzing resume and generating tailored content..."):
        result = review_resume(resume_text, job_description)
        tailored_resume = generate_tailored_resume(resume_text, job_description)

    st.subheader("Resume Fit Review")
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{result['score']}/100")
    col2.metric("Decision", result["decision"])
    col3.metric("Matched Skills", len(result["matched_skills"]))
    review_col, resume_col = st.columns(2)
    with review_col:
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
        st.write(", ".join(result["matched_skills"]) or "No direct matches")
        st.subheader("Missing Skills")
        st.write(", ".join(result["missing_skills"]) or "No major missing skills found")
        if "llm_feedback" in result:
            st.subheader("LLM Review")
            st.write(result["llm_feedback"])
    with resume_col:
        st.subheader("Generated Resume Content")
        edited_resume = st.text_area("Review and modify before downloading", value=tailored_resume, height=620, label_visibility="collapsed")
        st.download_button("Download as PDF", data=generate_pdf(edited_resume), file_name="tailored_resume.pdf", mime="application/pdf", type="primary")


def generate_pdf(content: str) -> bytes:
    """Create a simple, readable PDF from generated resume text."""
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:
        raise RuntimeError("PDF support requires the reportlab package.") from exc
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=0.65 * inch, leftMargin=0.65 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    body = getSampleStyleSheet()["BodyText"]
    body.leading = 14
    story = []
    for block in content.split("\n"):
        text = block.strip()
        if text:
            story.extend([Paragraph(text.replace("&", "&amp;"), body), Spacer(1, 6)])
    document.build(story)
    return buffer.getvalue()
