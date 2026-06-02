# KaburAjaDulu.AI — Backend API

FastAPI backend with Gemini API integration for CV analysis and career roadmap generation.

## Stack

- **FastAPI** + **Pydantic v2** — API framework & validation
- **TensorFlow 2.18** — Role classification model inference
- **Google Gemini** — Career roadmap & CV feedback generation

---

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create venv (already done if you're reading this)
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env and fill in your GEMINI_API_KEY
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check + model status |
| POST | `/api/v1/skills/extract` | Rule-based skill extraction from CV text |
| POST | `/api/v1/roles/predict` | Deep learning role classification |
| POST | `/api/v1/skills/gap-analysis` | Skill gap against industry top skills |
| POST | `/api/v1/roadmap/generate` | AI-generated career roadmap (Gemini) |
| POST | `/api/v1/cv/feedback` | Upload CV file → AI feedback (Gemini) |

---

## Project Structure

```
kabur-aja-dulu-ai-api/
├── app/
│   ├── api/v1/endpoints/   # Route handlers
│   ├── core/               # Config, logging, security
│   ├── services/           # Business logic
│   ├── models/             # Pydantic request/response schemas
│   ├── utils/              # Text cleaner, PDF/image parsers
│   ├── ai/                 # Model singleton, Gemini client
│   └── main.py             # FastAPI app entry point
├── artifacts/              # Model artifacts (auto-copied from ../models/)
├── prompts/                # Gemini prompt templates
├── requirements.txt
├── .env.example
└── README.md
```

---

## Response Format

All endpoints follow a consistent format:

```json
{
  "success": true,
  "message": "OK",
  "data": "..."
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE"
}
```

---

## Prompts Customization

Edit the placeholder prompts in `prompts/`:

- `prompts/roadmap_prompt.txt` — Career roadmap generation prompt
- `prompts/cv_feedback_prompt.txt` — CV analysis feedback prompt

Variables available: `{role}`, `{skills}`, `{cv_text}`
