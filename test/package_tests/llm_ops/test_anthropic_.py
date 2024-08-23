import os
import pytest
from unittest.mock import MagicMock, patch
from ragmatic.llm_ops.anthropic_ import AnthropicClient, AnthropicContent, LLMState

@pytest.fixture
def anthropic_config():
    return {
        "api_keyenvvar": "ANTHROPIC_API_KEY",
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 4096,
        "default_headers": {"Custom-Header": "Value"},
        "api_key": "test_key"
    }

@pytest.fixture(autouse=True)
def set_api_keyenvvar():
    os.environ["ANTHROPIC_API_KEY"] = "test_key"

@pytest.fixture(autouse=True)
def mock_anthropic():
    with patch('ragmatic.llm_ops.anthropic_.Anthropic') as mock_anthropic:
        yield mock_anthropic

def test_anthropic_content():
    content = AnthropicContent("Hello, World!")
    assert content.get_content() == {"type": "text", "text": "Hello, World!"}

def test_anthropic_client_initialization(anthropic_config, mock_anthropic):
    client = AnthropicClient(anthropic_config)
    assert client.config == anthropic_config
    assert client._api_keyenvvar == "ANTHROPIC_API_KEY"
    assert client._api_keypath == ""
    assert client._api_key == client._b64key("test_key")
    assert client.model == "claude-3-5-sonnet-20240620"
    assert client.max_tokens == 4096
    assert client.default_headers == {"Custom-Header": "Value"}
    mock_anthropic.assert_called_once_with(api_key="test_key", default_headers={"Custom-Header": "Value"})

def test_get_client(anthropic_config, mock_anthropic):
    client = AnthropicClient(anthropic_config)
    mock_anthropic.assert_called_once_with(api_key="test_key", default_headers={"Custom-Header": "Value"})

def test_load_api_key_error():
    config = {"api_keyenvvar": "NON_EXISTENT_KEY"}
    with pytest.raises(ValueError, match="anthropic API key not found."):
        AnthropicClient(config)

def test_send_message(mock_anthropic, anthropic_config):
    anthropic_client = AnthropicClient(anthropic_config)
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello, I'm Claude.")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    response = anthropic_client.send_message("Hello, AI!", system_prompt="You are a helpful assistant.")
    
    assert response == "Hello, I'm Claude."
    mock_anthropic.return_value.messages.create.assert_called_once_with(
        model="claude-3-5-sonnet-20240620",
        messages=[
            {"role": "user", "content": {"type": "text", "text": "Hello, AI!"}}
        ],
        max_tokens=4096,
        system_prompt=["You are a helpful assistant."]
    )

def test_send_chat(mock_anthropic, anthropic_config):
    anthropic_client = AnthropicClient(anthropic_config)
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello, I'm Claude.")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    state = LLMState(
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ],
        system_prompt="You are a helpful assistant.",
        model="claude-3-5-sonnet-20240620",
        client=MagicMock(),
        content_type=MagicMock(),
    )

    response = anthropic_client.send_chat(state)
    
    assert response == "Hello, I'm Claude."
    mock_anthropic.return_value.messages.create.assert_called_once_with(
        model="claude-3-5-sonnet-20240620",
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ],
        max_tokens=4096,
        system_prompt=["You are a helpful assistant."]
    )

def test_send_chat_invalid_final_message(anthropic_config):
    client = AnthropicClient(anthropic_config)
    state = LLMState(
        model="claude-3-5-sonnet-20240620",
        client=MagicMock(),
        content_type=MagicMock(),
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
    )

    with pytest.raises(ValueError, match="The final message must be from the user."):
        client.send_chat(state)

def test_send_message_multiple_content(mock_anthropic, anthropic_config):
    anthropic_client = AnthropicClient(anthropic_config)
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(text="Hello,"),
        MagicMock(text="I'm Claude."),
        MagicMock(text="How can I help you?")
    ]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    response = anthropic_client.send_message("Hello, AI!")
    
    assert response == "Hello,\n\nI'm Claude.\n\nHow can I help you?"