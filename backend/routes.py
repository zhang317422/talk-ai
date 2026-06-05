import json
import time
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from openai import APIError, APITimeoutError, RateLimitError

from config import client, DEFAULT_MODEL, logger
from models import ChatRequest, TutorRequest, ResetRequest, TutorResponse
from prompts import TUTOR_PROMPT, TUTOR_PROMPT_STREAM
from sessions import store

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _parse_json_output(raw: str) -> TutorResponse:
    try:
        data = json.loads(raw)
        return TutorResponse(**data)
    except (json.JSONDecodeError, Exception):
        return TutorResponse(reply=raw, corrections=[])


def _parse_stream_output(raw: str) -> TutorResponse:
    if "--- Corrections ---" not in raw:
        return TutorResponse(reply=raw, corrections=[])
    parts = raw.split("--- Corrections ---", 1)
    reply = parts[0].strip()
    corrections_block = parts[1].strip()
    corrections = _parse_corrections_text(corrections_block)
    return TutorResponse(reply=reply, corrections=corrections)


def _parse_corrections_text(text: str) -> list:
    corrections = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        item = {}
        for line in lines:
            for key in ("Mistake", "Correct", "Explanation"):
                if line.startswith(f"{key}:"):
                    item[key.lower()] = line[len(key) + 1 :].strip()
        if "mistake" in item:
            corrections.append(item)
    return corrections


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
        t0 = time.time()
        messages = [{"role": "system", "content": TUTOR_PROMPT}]
        history_len = len(store.get(req.session_id))
        messages.extend(store.get(req.session_id))
        messages.append({"role": "user", "content": req.message})

        try:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
            )
        except RateLimitError:
            raise HTTPException(status_code=429, detail="Service busy, please retry later")
        except APITimeoutError:
            raise HTTPException(status_code=504, detail="AI service timeout, please retry")
        except APIError as e:
            logger.error("API error: %s", e)
            raise HTTPException(status_code=502, detail="AI service error")

        raw = response.choices[0].message.content
        usage = response.usage
        result = _parse_json_output(raw)
        store.append(req.session_id, "user", req.message)
        store.append(req.session_id, "assistant", result.model_dump_json())
        elapsed = (time.time() - t0) * 1000
        logger.info(
            "tutor session=%s history=%d tokens_in=%d tokens_out=%d time=%dms",
            req.session_id, history_len,
            usage.prompt_tokens if usage else 0,
            usage.completion_tokens if usage else 0,
            int(elapsed),
        )
        return result

    @app.post("/api/tutor/stream")
    def tutor_stream(req: TutorRequest):
        t0 = time.time()
        messages = [{"role": "system", "content": TUTOR_PROMPT_STREAM}]
        history_len = len(store.get(req.session_id))
        messages.extend(store.get(req.session_id))
        messages.append({"role": "user", "content": req.message})

        try:
            stream = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                stream=True,
            )
        except RateLimitError:
            raise HTTPException(status_code=429, detail="Service busy, please retry later")
        except APITimeoutError:
            raise HTTPException(status_code=504, detail="AI service timeout, please retry")
        except APIError as e:
            logger.error("API error: %s", e)
            raise HTTPException(status_code=502, detail="AI service error")

        full_raw = []
        chunk_count = 0

        def generate():
            nonlocal chunk_count
            try:
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_raw.append(delta.content)
                        chunk_count += 1
                        yield f"data: {json.dumps({'content': delta.content})}\n\n"
            except APIError as e:
                logger.error("Stream API error: %s", e)
                yield f"data: {json.dumps({'error': 'AI service error'})}\n\n"
                yield "data: [DONE]\n\n"
                return

            raw = "".join(full_raw)
            result = _parse_stream_output(raw)
            store.append(req.session_id, "user", req.message)
            store.append(req.session_id, "assistant", result.model_dump_json())

            if result.corrections:
                yield f"data: {json.dumps({'corrections': [c.model_dump() for c in result.corrections]})}\n\n"
            yield "data: [DONE]\n\n"

            elapsed = (time.time() - t0) * 1000
            logger.info(
                "tutor_stream session=%s history=%d chunks=%d time=%dms",
                req.session_id, history_len, chunk_count, int(elapsed),
            )

        return StreamingResponse(generate(), media_type="text/event-stream")

    @app.post("/api/tutor/reset")
    def tutor_reset(req: ResetRequest):
        store.clear(req.session_id)
        return {"status": "ok"}
