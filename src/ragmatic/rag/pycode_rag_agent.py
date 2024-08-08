from typing import List, Callable
import os

from pydantic import BaseModel
from ..llm_ops.bases import LLMClientBase
from ..llm_ops.client_factory import get_llm_client_class
from .bases import RagAgentBase


class RagAgentConfig(BaseModel):
    llm_client_type: str
    llm_config: dict


class PyCodeRagAgent(RagAgentBase):

    system_prompt = (
        "You are an assistant with expertise in programming, particularly with "
        "python applications. You pay careful attention to detail "
        "and provide clear, concise answers that avoid hyperbole."
    )
    prompt = (
        "I'm a python developer, and I have a question about some code in a "
        "codebase. I'll first ask my question, and then I'll share a number of "
        "code files all from the codebase. Please answer my question as it "
        "relates to these files. Here's the question, followed by divider and "
        "then the codebase files:"
    )

    file_filters = [(lambda x: x.endswith('.py'))]

    def module_name_to_file_path(self, module_name: str):
        parts = module_name.split(".")
        parts[-1] = parts[-1] + ".py"
        return os.path.join(self.root_dir, *parts)
    
    def build_user_message(self, query: str, context_docs: dict[str, str]):
        context_block = ""
        for relpath, doc in context_docs.items():
            context_block += f"```python file={relpath}\n{doc}\n```\n\n"
        return (
            self.prompt +
            "\n" +
            query +
            self.q_context_delimiter +
            context_block
        )
    