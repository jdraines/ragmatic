from .bases import RagAgentBase
from ragmatic.utils import ALLOWED_FILE_TYPES

class GenericRagAgent(RagAgentBase):

    name = "generic"
    system_prompt = (
        "You are an assistant with attention to detail who is able to provide "
        "clear answers to questions relating to a collection of documents."
    )
    prompt = (
        "I have a question about some documents in a collection. I'll first ask "
        "my question, and then I'll share a number of documents, all from the collection. "
        "Please answer my question as it relates to these documents, and include "
        "any relevant sections of text from the documents in your response. "
        "Here's the question, followed by a divider and then the documents:"
    )

    file_filters = [(lambda x: x.split(".")[-1] in ALLOWED_FILE_TYPES)]
    
    def build_user_message(self, query: str, context_docs: dict[str, str]):
        context_block = ""
        for relpath, doc in context_docs.items():
            context_block += f"```txt file={relpath}\n{doc}\n```\n\n"
        return (
            self.prompt +
            "\n" +
            query +
            self.q_context_delimiter +
            context_block
        )
    