# WeHire ML Hub – FastAPI Service

This FastAPI application provides endpoints for resume parsing, structured extraction, and job matching using AI agents and OpenAI APIs.

## Setup

1. **Install dependencies**
   Make sure you have Python 3.8+ and install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**
   ```bash
   uvicorn application.app:app --reload --host 0.0.0.0 --port 3000
   ```

---

## API Endpoints

### 1. Upload Resume (Extract Text)

**POST** `/upload-resume/`
Upload a PDF resume and get extracted plain text.

- **Request:** `multipart/form-data` with a `file` field (PDF only)
- **Response:** Plain text of the resume

**Example using `curl`:**
```bash
curl -F "file=@your_resume.pdf" http://localhost:3000/upload-resume/
```

---

### 2. Parse Resume Text to Structured JSON

**POST** `/parse-resume/`
Send raw resume text and get structured JSON using OpenAI.

- **Request:** `application/x-www-form-urlencoded` with `cv_text` field (resume text)
- **Response:** Structured JSON

**Example:**
```bash
curl -X POST -d "cv_text=Paste your resume text here" http://localhost:3000/parse-resume/
```

---

### 3. Parse Resume PDF to Structured JSON (OpenAI)

**POST** `/parse-resume-structured/`
Upload a PDF resume, extract text, and get structured JSON using OpenAI.

- **Request:** `multipart/form-data` with a `file` field (PDF only)
- **Response:** Structured JSON

**Example:**
```bash
curl -F "file=@your_resume.pdf" http://localhost:3000/parse-resume-structured/
```

---

### 4. Match Resume with Jobs

**POST** `/match-jobs-form/`
Match a structured resume with job descriptions and get top 3 matches.

- **Request:**
  - `resume_json`: JSON string of structured resume
  - `jobs_json`: JSON string of job descriptions

- **Response:** JSON with top 3 matched jobs and matching scores

**Example:**
```bash
curl -X POST \
  -F 'resume_json={"name":"John Doe", ...}' \
  -F 'jobs_json=[{"title":"Data Scientist", ...}, ...]' \
  http://localhost:3000/match-jobs-form/
```

---

## Notes

- Only PDF files are supported for upload endpoints.
- The service uses OpenAI APIs for parsing and matching.
- Temporary files are stored in `temp_uploads/` and deleted after processing.

---

## Development

- Main app file: `application/app.py`
- AI agent logic: `ai_agents/`
- Resume text extraction: `main_functions.py`

---

##
