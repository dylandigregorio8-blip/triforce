import json
import os
from cmd import PROMPT
from unittest.mock import MagicMock, patch

import pytest
import requests
from local_ai import local_ai


def _mock_completion_response(completions: list[str]) -> MagicMock:
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(completions)
                }
            }
        ]}
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
    assert payload["max_tokens"] == 200
    assert payload["messages"] == [{"role": "system", "content": PROMPT},
                                   {"role": "user", "content": "Here is the text: secret doc"}]
    print(PROMPT)


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


@pytest.mark.skipif(not os.getenv("STONEY_KEY"), reason="STONEY_KEY is not set")
def test_local_ai_live_call_with_stoney_key_with_prompt():
    result = local_ai(
        "Please be advised that the confidential profile for patient Jane Doe (Date of Birth: 05/12/1988, SSN: XXX-45-6789) has been updated. Her primary residence is listed as 1234 Main Street, Apt 4B, Springfield, OR 97477, and she can be reached at (555) 019-2831 or via email at jane.doe@example.com. The recent charge of $1,450.00 for her treatment plan was billed to her Visa card ending in 4321 (Expiration: 08/26, CVV: 891). Her confidential medical record indicates a diagnosis of Type 1 Diabetes, and her patient portal login username is jdoe_med88 with the temporary access pin 9021#4.")

    #    assert (result["choices"][0]["message"]["content"], str)
    print(result)

    # assert isinstance(result, dict)
    # assert result
    # assert all(isinstance(item, str) for item in result)
