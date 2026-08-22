import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from local_ai import local_ai


def _mock_completion_response(completions: list[str]) -> MagicMock:
    mock_response = MagicMock()
    mock_response.json.return_value = {"completions": completions}
    return mock_response


@patch("local_ai.requests.request")
def test_local_ai_returns_completions(mock_request):
    mock_request.return_value = _mock_completion_response(["alpha", "beta"])

    assert local_ai("patient notes") == ["alpha", "beta"]
    mock_request.return_value.raise_for_status.assert_called_once()


@patch("local_ai.requests.request")
def test_local_ai_posts_chat_completion_for_document(mock_request, monkeypatch):
    monkeypatch.setenv("STONEY_KEY", "test-key")
    mock_request.return_value = _mock_completion_response(["ok"])

    local_ai("secret doc")

    mock_request.assert_called_once()
    method, url = mock_request.call_args.args
    assert method == "POST"
    assert url == "https://llm.stoney-cloud.com/v1/chat/completions"

    payload = mock_request.call_args.kwargs["json"]
    assert payload["model"] == "apertus-ai/Apertus-v1.5-8B"
    assert payload["max_tokens"] == 100
    assert payload["message"] == [{"role": "user", "content": "hello: secret doc"}]


@patch("local_ai.requests.request")
def test_local_ai_raises_when_http_fails(mock_request):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("boom")
    mock_request.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        local_ai("doc")


@pytest.mark.skipif(not os.getenv("STONEY_KEY"), reason="STONEY_KEY is not set")
def test_local_ai_live_call_with_stoney_key():
    result = local_ai("hello")

    assert isinstance(result, list)
    assert result
    assert all(isinstance(item, str) for item in result)
