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
  "session_id": "abc123",
  "level": "beginner",
  "scenario": "ordering_food"
}
```
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| message | string | yes | - | User message (Chinese or English) |
| session_id | string | no | "default" | Session ID for conversation memory |
| level | string | no | "intermediate" | `beginner` / `intermediate` / `advanced` |
| scenario | string | no | "free_talk" | See scenarios below |

**Scenarios**
| Value | Description |
|-------|-------------|
| `free_talk` | Free conversation on any topic |
| `ordering_food` | Ordering at a fast food counter |
| `checking_in` | Hotel check-in |
| `asking_directions` | Asking for directions |
| `job_interview` | Job interview practice |
| `shopping` | Shopping assistance |
| `at_restaurant` | Dining at a restaurant |

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

**Request** — same as `/api/tutor` (supports `level` and `scenario`)

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
