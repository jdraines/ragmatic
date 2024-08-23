import os
from typing import Any, Optional
from dataclasses import dataclass, field
import base64
from abc import ABC, abstractmethod



@dataclass
class MessageBox:
    msg: str


class ContentBase:

    def __init__(self, msg: str):
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
            _key = os.environ.get(self._api_keyenvvar)
            if not _key:
                return None
            return self._b64key(_key)
        if self._api_keypath:
            with open(self._api_keypath, "r") as f:
                return self._b64key(f.read().strip())
        
    def _b64key(self, keystring: str) -> str:
        return base64.b64encode(keystring.encode()).decode()

    def _plaintextkey(self) -> str:
        return base64.b64decode(self._api_key.encode()).decode()
