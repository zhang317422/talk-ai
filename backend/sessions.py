from collections import defaultdict

MAX_HISTORY = 20  # keep last 20 messages


class SessionStore:
    def __init__(self):
        self._store: dict[str, list[dict]] = defaultdict(list)

    def get(self, session_id: str) -> list[dict]:
        return self._store[session_id]

    def append(self, session_id: str, role: str, content: str):
        history = self._store[session_id]
        history.append({"role": role, "content": content})
        if len(history) > MAX_HISTORY:
            self._store[session_id] = history[-MAX_HISTORY:]

    def clear(self, session_id: str):
        self._store.pop(session_id, None)


store = SessionStore()
