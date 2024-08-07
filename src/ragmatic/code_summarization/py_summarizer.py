from typing import List
import re

from .bases import CodeSummarizerBase


class PyCodeSummarizer(CodeSummarizerBase):

    summarizer_name = "python_code"
    file_filters: List = [(lambda x: x.endswith('.py'))]

    _system_prompt = (
        "You are an assistant who is an expert in Python programming who pays "
        "careful attention to details of code structure, but is also able to "
        "provide high-level summaries of code and its functionality. Your answers "
        "are expected to be concise and informative."

    )
    _code_document_prompt = (
        "Please review the following Python code and provide several summaries. "
        "The first summary should be a high-level overview of the code's functionality. "
        "Then, create a summary for each function or class present in the code. "
        "Finally, provide a summary for any other important components of the code."
        "Identify each summary by a set of <summary></summary> tags."
    )

    def summarize_code_document(self, code_doc: str) -> list[str]:
        message = self._build_message(code_doc)
        response = self._llm_client.send_message(
            message,
            self._system_prompt,
            role="user"
        )
        return re.findall(r"<summary>(.*?)</summary>", response, re.DOTALL)
    