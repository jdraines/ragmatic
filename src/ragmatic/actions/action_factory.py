from .bases import Action
from .encode import EncodeAction
from .summarize import SummarizeAction


_actions = {
    EncodeAction.name: EncodeAction,
    SummarizeAction.name: SummarizeAction,
}


def get_action_cls(action_name: str) -> Action:
    if action_name not in _actions:
        raise ValueError(f"Action '{action_name}' not found.")
    return _actions[action_name]


def list_actions() -> list[str]:
    return sorted(list(_actions.keys()))
