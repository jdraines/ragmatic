import os
import pytest
from unittest.mock import MagicMock, patch
from ragmatic.llm_ops.openai_ import OpenAIClient, OpenAIContent, LLMState
import logging

@pytest.fixture
def openai_config():
    return {
        "api_keyenvvar": "OPENAI_API_KEY",
        "model": "mock-model",
        "log_level": logging.INFO,
        "api_key": "test_key"
    }


@pytest.fixture(autouse=True)
def set_api_keyenvvar():
    os.environ["OPENAI_API_KEY"] = "test_key"

@pytest.fixture(autouse=True)
def mock_openai():
    with patch('ragmatic.llm_ops.openai_.OpenAI') as mock_openai:
        yield mock_openai

def test_openai_content():
    content = OpenAIContent("Hello, World!")
    assert content.get_content() == "Hello, World!"

def test_openai_client_initialization(openai_config, mock_openai):
    client = OpenAIClient(openai_config)
    assert client.config == openai_config
    assert client._api_keyenvvar == "OPENAI_API_KEY"
    assert client._api_keypath == ""
    assert client._api_key == client._b64key("test_key")
    assert client.model == "mock-model"
    assert client._log_level == logging.INFO
    mock_openai.assert_called_once_with(api_key="test_key")

def test_get_client(openai_config, mock_openai):
    client = OpenAIClient(openai_config)
    mock_openai.assert_called_once_with(api_key="test_key")

@patch('logging.getLogger')
def test_set_openai_log_level(mock_get_logger, openai_config, mock_openai):
    config = openai_config.copy()
    config["log_level"] = logging.DEBUG
    OpenAIClient(config)
    mock_get_logger.assert_any_call("openai")
    mock_get_logger.assert_any_call("httpx")
    mock_get_logger().setLevel.assert_called_with(logging.DEBUG)

def test_send_message(mock_openai, openai_config):
    openai_client = OpenAIClient(openai_config)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello, I'm an AI."
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    response = openai_client.send_message("Hello, AI!", system_prompt="You are a helpful assistant.")
    
    assert response == "Hello, I'm an AI."
    mock_openai.return_value.chat.completions.create.assert_called_once_with(
        model="mock-model",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, AI!"}
        ]
    )

def test_send_chat(mock_openai, openai_config):
    openai_client = OpenAIClient(openai_config)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello, I'm an AI."
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    state = LLMState(
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ],
        system_prompt="You are a helpful assistant.",
        model="mock-model",
        client=MagicMock(),
        content_type=MagicMock(),
    )

    response = openai_client.send_chat(state)
    
    assert response == "Hello, I'm an AI."
    mock_openai.return_value.chat.completions.create.assert_called_once_with(
        model="mock-model",
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How are you?"}
        ]
    )

def test_send_chat_invalid_final_message(openai_config):
    client = OpenAIClient(openai_config)
    state = LLMState(
        model="mock-model",
        client=MagicMock(),
        content_type=MagicMock(),
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
    )

    with pytest.raises(ValueError, match="The final message must be from the user."):
        client.send_chat(state)
