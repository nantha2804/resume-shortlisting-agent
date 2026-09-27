# Resume Shortlisting App

This app reviews a resume against a job description and returns:

- a score out of 100
- shortlist / human review / reject decision
- matched skills
- missing skills
- strengths
- improvement suggestions
- key review points

It can run in two modes:

1. Local Streamlit dashboard
2. FastAPI backend for web deployment

## Local setup

```bash
cd resume_shortlisting_app
uv pip install -r requirements.txt
```

Create a `.env` file with your Groq key if you want extra LLM review:

```env
GROQ_API_KEY=your_key_here
```

## Run the local UI

```bash
cd resume_shortlisting_app
uv run streamlit run app.py
```

## Run the API locally

```bash
cd resume_shortlisting_app
uv run uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Test the API

```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "resume": "Python Developer with SQL, FastAPI, Docker and AWS experience.",
    "job_description": "Looking for Python, SQL, AWS, Docker and LangGraph experience."
  }'
```

## Docker

Build the image:

```bash
docker build -t resume-review-app .
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env resume-review-app
```

Or with Docker Compose:

```bash
docker-compose up --build
```

## GitHub push

```bash
git init
git add .
git commit -m "Resume review app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Live deployment

This API is ready for cloud deployment on:

- Render
- Railway
- Fly.io
- Azure App Service
- Docker VPS

Use the start command:

```bash
uvicorn api:app --host 0.0.0.0 --port 10000
```

Add the environment variable:

```env
GROQ_API_KEY=your_key_here
```

## Notes

- The main resume scoring is keyword-based, which is good for fast local testing.
- If `GROQ_API_KEY` is configured, Groq can provide extra AI review content.
- Do not commit `.env` to GitHub.
