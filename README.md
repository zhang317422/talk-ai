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

> **Note:** The `uvicorn` command must be run from the `backend/` directory, since `main:app` references `main.py` in that directory.

Open `http://localhost:8000` in your browser, or `http://localhost:8000/api` for API docs.

## Demo

[Watch the demo video on Bilibili](https://www.bilibili.com/video/BV1dtEh6FEyo)
