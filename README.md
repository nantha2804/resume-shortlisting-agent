# Resume Shortlisting App

## Live demo

[Open the live demo](https://frontend-1atoauzea-snk18.vercel.app/)

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

Open http://localhost:5500. The frontend uses the same-origin `/review` API route, which is correct for the combined Vercel deployment. For local API testing, change `API_URL` in `frontend/app.js` to `http://localhost:8000/review`.

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

## Live deployment on Vercel

This repository is configured as one Vercel project. The static frontend is served from `frontend/`, and the Python serverless API is served from `api/index.py`. The frontend calls `/review`, so no separate frontend API URL is required.

In the Vercel project settings:

1. Set Root Directory to `.` (or leave it blank) when the Vercel repository is already this project. Do not enter `resume_shortlisting_app` unless that folder is actually nested inside the connected repository.
2. Keep the Framework Preset as `Other` and leave the Build Command and Output Directory empty.
3. Add `GROQ_API_KEY` under Settings → Environment Variables for the environments you use.
4. Redeploy from the latest commit.
5. Verify `/health` on the deployed domain, then open the root page and run one analysis.

Do not commit `.env`; use Vercel Environment Variables instead. If the deployment redirects to Vercel login, review Deployment Protection and test the URL in a private browser window.

## Suggested next steps

1. Add the environment variable in Vercel and redeploy the combined project.
2. Check `https://YOUR-VERCEL-DOMAIN/health`, then test analysis from the deployed frontend.
3. Test each supported upload type, the 5 MB boundary, invalid files, clear, and report download.
4. Implement and evaluate the future AI workflow above in small stages, beginning with section-aware resume extraction.

## Notes

- The current API score is keyword-based. The optional Groq helper is not currently included in the API response contract.
- Do not commit `.env` to GitHub.
