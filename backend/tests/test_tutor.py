import json
from unittest.mock import Mock


def test_tutor_structured_response(client, mock_openai):
    mock_openai.create.return_value = Mock(
        choices=[Mock(message=Mock(content=json.dumps({
            "reply": "Hello! How are you?",
            "corrections": [
                {"mistake": "I is", "correct": "I am", "explanation": "Subject-verb agreement"}
            ]
        })))],
        usage=Mock(prompt_tokens=10, completion_tokens=5),
    )

    response = client.post("/api/tutor", json={
        "message": "I is happy",
        "session_id": "test-1",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Hello! How are you?"
    assert len(data["corrections"]) == 1
    assert data["corrections"][0]["mistake"] == "I is"
    assert data["corrections"][0]["correct"] == "I am"


def test_tutor_default_params(client, mock_openai):
    mock_openai.create.return_value = Mock(
        choices=[Mock(message=Mock(content=json.dumps({
            "reply": "Hi!",
            "corrections": []
        })))],
        usage=Mock(prompt_tokens=10, completion_tokens=2),
    )

    response = client.post("/api/tutor", json={"message": "hello"})

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Hi!"
    assert data["corrections"] == []


def test_tutor_passes_level_and_scenario(client, mock_openai):
    mock_openai.create.return_value = Mock(
        choices=[Mock(message=Mock(content=json.dumps({
            "reply": "I'd like a burger please.",
            "corrections": []
        })))],
        usage=Mock(prompt_tokens=10, completion_tokens=5),
    )

    response = client.post("/api/tutor", json={
        "message": "我要一个汉堡",
        "level": "beginner",
        "scenario": "ordering_food",
    })

    assert response.status_code == 200
    call_args = mock_openai.create.call_args
    system_prompt = call_args.kwargs["messages"][0]["content"]
    assert "beginner" in system_prompt
    assert "ordering food" in system_prompt.lower()


def test_tutor_reset(client, mock_openai):
    mock_openai.create.return_value = Mock(
        choices=[Mock(message=Mock(content=json.dumps({
            "reply": "OK",
            "corrections": []
        })))],
        usage=Mock(prompt_tokens=10, completion_tokens=2),
    )

    response = client.post("/api/tutor/reset", json={"session_id": "test-reset"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tutor_session_memory(client, mock_openai):
    mock_openai.create.return_value = Mock(
        choices=[Mock(message=Mock(content=json.dumps({
            "reply": "Your name is Xiaoming.",
            "corrections": []
        })))],
        usage=Mock(prompt_tokens=20, completion_tokens=5),
    )

    sid = "session-mem-test"
    # First message
    client.post("/api/tutor", json={
        "message": "My name is Xiaoming",
        "session_id": sid,
    })

    # Second message
    response = client.post("/api/tutor", json={
        "message": "What is my name?",
        "session_id": sid,
    })

    assert response.status_code == 200
    call_args = mock_openai.create.call_args
    messages = call_args.kwargs["messages"]
    assert len(messages) > 1  # has history beyond system prompt
