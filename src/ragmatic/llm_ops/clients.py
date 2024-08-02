import os
from typing import Any, Optional
from dataclasses import dataclass, field
import base64
from abc import ABC, abstractmethod



@dataclass
class MessageBox:
    msg: str


class ContentBase:

    def __init__(self, msg: MessageBox):
        self.msg = msg

    def get_content(self):
        raise NotImplementedError

@dataclass
class LLMState:
    model: str
    client: Any
    content_type: ContentBase
    messages: list[dict] = field(default_factory=list)
    system_prompt: Optional[str] = None


class LLMClient(ABC):

    content_type: ContentBase = None

    @abstractmethod
    def __init__(self, config: dict):
        pass

    @abstractmethod
    def send_message(self,
                     message: str,
                     system_prompt: str = None,
                     role: str = "user",
                     ) -> str:
        pass

    @abstractmethod
    def send_chat(self, state: LLMState) -> str:
        pass


class LLMClientBase(LLMClient):

    def __init__(self, config: dict):
        self.config = config
        self._api_keyenvvar = config.get("api_keyenvvar", "")
        self._api_keypath = config.get("api_keypath", "")
        self._api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        if self._api_keyenvvar:
            return os.environ.get(self._api_keyenvvar)
        if self._api_keypath:
            with open(self._api_keypath, "r") as f:
                return self._b64key(f.read().strip())
        
    def _b64key(self, keystring: str) -> str:
        return base64.b64encode(keystring.encode()).decode()

    def _plaintextkey(self) -> str:
        return base64.b64decode(self._api_key.encode()).decode()


class OpenAIContent(ContentBase):

    def get_content(self):
        return self.msg.msg


class OpenAIClient(LLMClientBase):

    content_type = OpenAIContent

    def __init__(self, config: dict):
        super().__init__(config)
        self.model = config.get("model", "gpt-4o")
        self.client = self._get_client()

    def _get_client(self):
        from openai import OpenAI
        return OpenAI(api_key=self._plaintextkey())

    def send_message(self,
                     message: str,
                     system_prompt: str = None,
                     role: str = "user",
                     ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": role, "content": OpenAIContent(message).get_content()})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages    
        )
        return response.choices[0].message.content.strip()
    
    def send_chat(self, state: LLMState) -> str:
        messages = state.messages

        final_role = messages[-1]["role"]
        if final_role != "user":
            raise ValueError("The final message must be from the user.")

        if state.system_prompt:
            penultimate_role = messages[-2]["role"]
            if penultimate_role == "system":
                messages[-2]["content"] = state.system_prompt
            else:
                messages.insert(-2, {"role": "system", "content": state.system_prompt})
        
        response = self.client.chat.completions.create(
            model=state.model,
            messages=messages    
        )
        return response.choices[0].message.content.strip()


class AnthropicContent(ContentBase):

    def get_content(self):
        return {
            "type": "text",
            "text": self.msg.msg
        }


class AnthropicClient(LLMClientBase):

    content_type = AnthropicContent

    def __init__(self, config: dict):
        super().__init__(config)
        self.model = config.get("model", "claude-3-5-sonnet-20240620")
        self.default_headers = config.get("default_headers", {})
        self.max_tokens = config.get("max_tokens", 4096)
        self.client = self._get_client()


    def _get_client(self):
        from anthropic import Anthropic
        return Anthropic(
            api_key=self._plaintextkey(),
            default_headers=self.default_headers
        )

    def send_message(self,
                     message: str,
                     system_prompt: str = None,
                     role: str = "user",
                     ) -> str:
        messages = [{
            "role": role,
            "content": OpenAIContent(message).get_content()
        }]
        
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            system_prompt=[system_prompt] if system_prompt else []
        )
        content = response.content
        return "\n\n".join([c.text for c in content])

    def send_chat(self, state: LLMState) -> str:
        messages = state.messages

        final_role = messages[-1]["role"]
        if final_role != "user":
            raise ValueError("The final message must be from the user.")

        response = self.client.messages.create(
            model=state.model,
            messages=messages,
            max_tokens=self.max_tokens,
            system_prompt=[state.system_prompt] if state.system_prompt else []
        )
        content = response.content
        return "\n\n".join([c.text for c in content])


_llm_clients = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient
}


def get_llm_client(client_name: str, config: dict) -> LLMClient:
    return _llm_clients[client_name](config)
