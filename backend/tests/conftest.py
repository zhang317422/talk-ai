from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


class FakeChoice:
    def __init__(self, content):
        self.delta = Mock(content=content)


class FakeStream:
    def __init__(self, chunks: list[str]):
        self._chunks = [FakeChoice(c) for c in chunks]

    def __iter__(self):
        return iter(self._chunks)


def fake_completion(content="", usage=None):
    choice = Mock()
    choice.message.content = content
    msg = Mock()
    msg.choices = [choice]
    msg.usage = usage or Mock(prompt_tokens=10, completion_tokens=5)
    return msg


@pytest.fixture
def mock_openai():
    with patch("routes.client.chat.completions") as mock:
        yield mock


@pytest.fixture
def client():
    from main import app

    return TestClient(app)
