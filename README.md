# Resume Shortlisting App

Compare resume text with a job description and view a keyword-based match score, recommendation, matched and missing skills, strengths, suggestions, and key points. The web frontend can extract text from supported uploads, display the result, and download a plain-text report.

## What works today

- Resume input by pasted text or TXT, text-based PDF, DOCX, PNG, JPG/JPEG, and WebP upload (maximum 5 MB).
- PDF and DOCX text extraction in the browser; OCR for supported image files.
- FastAPI review endpoint that matches terms from a fixed skill list and returns a score and recommendation.
- Result score visualization, clear form, and downloadable text report in the web frontend.

The score is a basic keyword match, not a complete assessment of candidate suitability. Experience/education matching, semantic matching, and the staged AI workflow below are not implemented yet. Legacy `.doc` and scanned PDFs are not supported.

## Future AI workflow

The following is a suggested roadmap, not current behavior:

```text
Resume
  -> Job description
  -> Skill extraction
  -> Experience matching
  -> Education matching
  -> Keyword and semantic matching
  -> AI explanation
  -> Final report
```

Suggested implementation order: improve structured resume extraction, add section-aware experience and education matching, add semantic similarity, then generate explanations with evidence linked to resume sections. Keep a human reviewer in the loop and evaluate scoring against representative examples before using it for hiring decisions.

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

## Run the web frontend locally

In a separate terminal:

```bash
cd resume_shortlisting_app/frontend
python -m http.server 5500
```

Open http://localhost:5500. The frontend uses the deployed Render API by default. For local API testing, change `API_URL` in `frontend/app.js` to `http://localhost:8000/review`.

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

### Frontend

- Vercel: https://frontend-fh4eh9aju-snk18.vercel.app/

If the deployment redirects to Vercel login, check Vercel Deployment Protection and verify public access in a private browser window.

### API

The frontend currently calls `https://resume-shortlisting-agent.onrender.com/review`.

The API can also be deployed on:

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

## Suggested next steps

1. Configure Vercel access and deploy the latest frontend; verify the app in a private browser window.
2. Check API health at `https://resume-shortlisting-agent.onrender.com/health`, then test analysis from the deployed frontend.
3. Test each supported upload type, the 5 MB boundary, invalid files, clear, and report download.
4. Implement and evaluate the future AI workflow above in small stages, beginning with section-aware resume extraction.

## Notes

- The current API score is keyword-based. The optional Groq helper is not currently included in the API response contract.
- Do not commit `.env` to GitHub.
