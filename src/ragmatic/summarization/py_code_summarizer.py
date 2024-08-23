from typing import List
import re
import os

from .bases import SummarizerBase


class PyCodeSummarizer(SummarizerBase):

    name = "python_code"
    file_filters: List = [(lambda x: x.endswith('.py'))]

    _system_prompt = (
        "You are an assistant who is an expert in Python programming who pays "
        "careful attention to details of code structure, but is also able to "
        "provide high-level summaries of code and its functionality."
    )
    _document_prompt = (
        "Please review the following Python code and provide several summaries. "
        "The first summary should be a high-level overview of the code's functionality. "
        "Then, create a summary for each function or class present in the code. "
        "Finally, provide a summary for any other important components of the code."
        "Identify each summary by a set of <summary></summary> tags."
    )

    def summarize_document(self, doc: str) -> list[str]:
        message = self._build_message(doc)
        response = self._llm_client.send_message(
            message,
            self._system_prompt,
            role="user"
        )
        return re.findall(r"<summary>(.*?)</summary>", response, re.DOTALL)
    
    def _file_path_to_doc_name(self, file_path: str) -> str:
        rel_path = super()._file_path_to_doc_name(file_path)
        return self._file_path_to_module_name(rel_path)

    def _file_path_to_module_name(self, rel_path: str) -> str:
        # strip dots from the beginning of the path
        rel_path = re.sub(r"^\.*", "", rel_path)
        if rel_path.startswith(os.path.sep):
            rel_path = rel_path[1:]
        module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
        return module_name
