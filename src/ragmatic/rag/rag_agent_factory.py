import typing as t
from .bases import RagAgentBase
from ..utils import import_object

_rag_agents =  {
    "python_code": "ragmatic.rag.pycode_rag_agent.PyCodeRagAgent"
}


def get_rag_agent_class(rag_agent_name:str) -> t.Type[RagAgentBase]:
    if rag_agent_name not in _rag_agents:
        raise ValueError(f"No RagAgent named {rag_agent_name!r} was found.")
    return import_object(_rag_agents[rag_agent_name])
