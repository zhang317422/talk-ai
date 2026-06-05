import json
from pathlib import Path

from fastapi.responses import StreamingResponse, HTMLResponse

from config import client, DEFAULT_MODEL
from models import ChatRequest, TutorRequest, TutorResponse
from prompts import TUTOR_PROMPT
from sessions import store

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _parse_tutor_output(raw: str) -> TutorResponse:
    try:
        data = json.loads(raw)
        return TutorResponse(**data)
    except (json.JSONDecodeError, Exception):
        return TutorResponse(reply=raw, corrections=[])


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
        messages = [{"role": "system", "content": TUTOR_PROMPT}]
        messages.extend(store.get(req.session_id))
        messages.append({"role": "user", "content": req.message})

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
        )
        raw = response.choices[0].message.content
        result = _parse_tutor_output(raw)
        store.append(req.session_id, "user", req.message)
        store.append(req.session_id, "assistant", result.model_dump_json())
        return result

    @app.post("/api/tutor/stream")
    def tutor_stream(req: TutorRequest):
        messages = [{"role": "system", "content": TUTOR_PROMPT}]
        messages.extend(store.get(req.session_id))
        messages.append({"role": "user", "content": req.message})

        stream = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            stream=True,
        )

        full_raw = []

        def generate():
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_raw.append(delta.content)
                    yield f"data: {json.dumps({'content': delta.content})}\n\n"

            raw = "".join(full_raw)
            result = _parse_tutor_output(raw)
            store.append(req.session_id, "user", req.message)
            store.append(req.session_id, "assistant", result.model_dump_json())

            if result.corrections:
                yield f"data: {json.dumps({'corrections': [c.model_dump() for c in result.corrections]})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    @app.post("/api/tutor/reset")
    def tutor_reset(req: TutorRequest):
        store.clear(req.session_id)
        return {"status": "ok"}
