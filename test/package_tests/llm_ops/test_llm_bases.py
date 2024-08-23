import pytest
import os
from unittest.mock import patch, mock_open
from ragmatic.llm_ops.bases import MessageBox, ContentBase, LLMState, LLMClientBase

def test_message_box():
    msg = "Hello, world!"
    box = MessageBox(msg)
    assert box.msg == msg

def test_content_base():
    content = ContentBase("Test message")
    with pytest.raises(NotImplementedError):
        content.get_content()

def test_llm_state():
    state = LLMState(
        model="gpt-3.5-turbo",
        client=None,
        content_type=ContentBase("Test"),
        messages=[{"role": "user", "content": "Hello"}],
        system_prompt="You are a helpful assistant."
    )
    assert state.model == "gpt-3.5-turbo"
    assert state.client is None
    assert isinstance(state.content_type, ContentBase)
    assert state.messages == [{"role": "user", "content": "Hello"}]
    assert state.system_prompt == "You are a helpful assistant."

class TestLLMClientBase:
    
    @pytest.fixture
    def config(self):
        return {
            "api_keyenvvar": "TEST_API_KEY"
        }
    
    @pytest.fixture(autouse=True)
    def set_api_keyenvvar(self):
        os.environ["TEST_API_KEY"] = "test_key"

    @pytest.fixture
    def mock_llmclient(self):
        class MockLLMClient(LLMClientBase):
            def send_message(self, message: str, system_prompt: str = None, role: str = "user") -> str:
                return message

            def send_chat(self, state: LLMState) -> str:
                return state.content_type.ms
        
        return MockLLMClient

    def test_init(self, config, mock_llmclient):
        config = config.copy()
        config["api_keypath"] = "/path/to/api/key.txt"
        client = mock_llmclient(config)
        assert client.config == config
        assert client._api_keyenvvar == "TEST_API_KEY"
        assert client._api_keypath == "/path/to/api/key.txt"

    def test_load_api_key_from_env(self, config, mock_llmclient):
        client = mock_llmclient(config)
        assert client._load_api_key() == "dGVzdF9rZXk="  # base64 encoded "test_key"

    @patch("builtins.open", mock_open(read_data="file_test_key"))
    def test_load_api_key_from_file(self, config, mock_llmclient):
        config = config.copy()
        config["api_keyenvvar"] = ""
        config["api_keypath"] = "/path/to/api/key.txt"
        client = mock_llmclient(config)
        assert client._api_key is not None
        assert client._load_api_key() == "ZmlsZV90ZXN0X2tleQ=="  # base64 encoded "file_test_key"

    def test_b64key(self, config, mock_llmclient):
        client = mock_llmclient(config)
        assert client._b64key("test_key") == "dGVzdF9rZXk="

    def test_plaintextkey(self, config, mock_llmclient):
        client = mock_llmclient(config)
        client._api_key = "dGVzdF9rZXk="
        assert client._plaintextkey() == "test_key"

    def test_abstract_methods(self, config, mock_llmclient):
        with pytest.raises(Exception):
            client = LLMClientBase(config)
        
