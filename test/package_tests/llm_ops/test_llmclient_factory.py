
import pytest
from unittest.mock import patch
from ragmatic.llm_ops.client_factory import get_llm_client_class
from ragmatic.llm_ops.bases import LLMClient

# Mock classes for testing
class MockOpenAIClient(LLMClient):
    pass

class MockAnthropicClient(LLMClient):
    pass

class MockCustomClient(LLMClient):
    pass

@pytest.mark.parametrize("client_name, expected_class", [
    ("openai", MockOpenAIClient),
    ("anthropic", MockAnthropicClient),
])
def test_get_llm_client_class_predefined(client_name, expected_class):
    with patch("ragmatic.llm_ops.client_factory.import_object", return_value=expected_class):
        client_class = get_llm_client_class(client_name)
        assert client_class == expected_class

def test_get_llm_client_class_custom():
    custom_client_path = "path.to.custom.Client"
    with patch("ragmatic.llm_ops.client_factory.import_object", return_value=MockCustomClient):
        client_class = get_llm_client_class(custom_client_path)
        assert client_class == MockCustomClient

def test_get_llm_client_class_not_found():
    non_existent_client = "non_existent_client"
    with patch("ragmatic.llm_ops.client_factory.import_object", side_effect=ImportError):
        with pytest.raises(ValueError) as excinfo:
            get_llm_client_class(non_existent_client)
        assert f"Client name {non_existent_client} not found in available clients:" in str(excinfo.value)

def test_get_llm_client_class_import_error():
    custom_client_path = "path.to.custom.Client"
    with patch("ragmatic.llm_ops.client_factory.import_object", side_effect=ImportError):
        with pytest.raises(ValueError) as excinfo:
            get_llm_client_class(custom_client_path)
        assert f"Client name {custom_client_path} not found in available clients:" in str(excinfo.value)

