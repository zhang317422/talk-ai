# Talk AI

AI English speaking practice tutor.

## Quick Start

### Prerequisites

- Python 3.10+

### Setup

```bash
git clone https://github.com/zhang317422/talk-ai.git
cd talk-ai/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# Edit .env with your DeepSeek API key

# Run
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` for the test page, or `http://localhost:8000/api` for API docs.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api` | API documentation |
| POST | `/api/tutor` | Tutor chat (JSON) |
| POST | `/api/tutor/stream` | Tutor chat (SSE stream) |
| POST | `/api/tutor/reset` | Clear session history |

See `http://localhost:8000/api` for full request/response examples.
