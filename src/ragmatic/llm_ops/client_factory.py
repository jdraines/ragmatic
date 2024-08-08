from typing import Type
from ragmatic.utils import import_object
from .bases import LLMClient
from ragmatic.utils import import_object

_clients = {
    "openai": "ragmatic.llm_ops.openai_.OpenAIClient",
    "anthropic": "ragmatic.llm_ops.anthropic_.AnthropicClient"
}


def get_llm_client_class(client_name: str) -> Type[LLMClient]:
    if client_name not in _clients:
        try:
            return import_object(client_name)
        except Exception:
            raise ValueError(f"Client name {client_name} not found in available clients: {list(_clients)}")
    return import_object(_clients[client_name])
