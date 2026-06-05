# Talk AI API

Base URL: `http://localhost:8000`

## Endpoints

### GET /api/health

Health check.

**Response**
```json
{"status": "ok"}
```

---

### POST /api/tutor

Send a message to the English tutor. Returns structured JSON with corrections.

**Request**
```json
{
  "message": "I have two dog",
  "session_id": "abc123"
}
```
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | yes | User message (Chinese or English) |
| session_id | string | no | Session ID for conversation memory (default: "default") |

**Response**
```json
{
  "reply": "That's great! Two dogs...",
  "corrections": [
    {
      "mistake": "two dog",
      "correct": "two dogs",
      "explanation": "Use plural form 'dogs' when talking about more than one."
    }
  ]
}
```

---

### POST /api/tutor/stream

Same as `/api/tutor` but streams the reply via SSE (Server-Sent Events).

**Request** — same as `/api/tutor`

**SSE Events**
```
data: {"content": "That"}

data: {"content": "'s great!"}

data: {"corrections": [{"mistake": "two dog", "correct": "two dogs", "explanation": "..."}]}

data: [DONE]
```

---

### POST /api/tutor/reset

Clear conversation history for a session.

**Request**
```json
{
  "session_id": "abc123"
}
```

**Response**
```json
{"status": "ok"}
```

---

### POST /api/chat

Generic chat (no tutor system prompt).

**Request**
```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "user", "content": "Hello"}
  ]
}
```

### POST /api/chat/stream

SSE-streaming version of `/api/chat`.
