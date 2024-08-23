from anthropic import Anthropic

from .bases import LLMClientBase, ContentBase, LLMState


class AnthropicContent(ContentBase):

    def get_content(self):
        return {
            "type": "text",
            "text": self.msg
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
        return Anthropic(
            api_key=self._plaintextkey(),
            default_headers=self.default_headers
        )

    def _load_api_key(self) -> str:
        key = super()._load_api_key()
        if not key:
            raise ValueError("anthropic API key not found.")
        return key

    def send_message(self,
                     message: str,
                     system_prompt: str = None,
                     role: str = "user",
                     ) -> str:
        messages = [{
            "role": role,
            "content": AnthropicContent(message).get_content()
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

