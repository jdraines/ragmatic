from openai import OpenAI

from .bases import LLMClientBase, ContentBase, LLMState


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

