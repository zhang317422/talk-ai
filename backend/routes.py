import json
from pathlib import Path

from fastapi import Request
from fastapi.responses import StreamingResponse, HTMLResponse

from config import client, DEFAULT_MODEL
from models import ChatRequest, TutorRequest
from prompts import TUTOR_PROMPT

TEMPLATE_DIR = Path(__file__).parent / "templates"


def register_routes(app):
    @app.get("/")
    def index():
        html = (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")
        return HTMLResponse(html)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/chat")
    def chat(req: ChatRequest):
        response = client.chat.completions.create(
            model=req.model,
            messages=[m.model_dump() for m in req.messages],
        )
        return {"reply": response.choices[0].message.content}

    @app.post("/api/chat/stream")
    def chat_stream(req: ChatRequest):
        stream = client.chat.completions.create(
            model=req.model,
            messages=[m.model_dump() for m in req.messages],
            stream=True,
        )

        def generate():
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield f"data: {json.dumps({'content': delta.content})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    @app.post("/api/tutor")
    def tutor(req: TutorRequest):
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": TUTOR_PROMPT},
                {"role": "user", "content": req.message},
            ],
        )
        return {"reply": response.choices[0].message.content}

    @app.post("/api/tutor/stream")
    def tutor_stream(req: TutorRequest):
        stream = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": TUTOR_PROMPT},
                {"role": "user", "content": req.message},
            ],
            stream=True,
        )

        def generate():
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield f"data: {json.dumps({'content': delta.content})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
