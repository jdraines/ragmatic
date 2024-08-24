from . import bases


class PyCodeRagAgent(bases.RagAgentBase):

    name = "python_code"
    system_prompt = (
        "You are an assistant with expertise in programming, particularly with "
        "python applications. You pay careful attention to detail "
        "and provide clear, concise answers that avoid hyperbole."
    )
    prompt = (
        "I'm a python developer, and I have a question about some code in a "
        "codebase. I'll first ask my question, and then I'll share a number of "
        "code files all from the codebase. Please answer my question as it "
        "relates to these files. Here's the question, followed by a divider and "
        "then the codebase files:"
    )

    file_filters = [(lambda x: x.endswith('.py'))]
    
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
    