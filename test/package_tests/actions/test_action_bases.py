import pytest
from ragmatic.actions.bases import Action, ActionConfig

def test_action_base_class():
    class TestAction(Action):
        config_cls = ActionConfig
        name = "test_action"

        def execute(self):
            return "Executed"

    config = ActionConfig()
    action = TestAction(config)

    assert action.name == "test_action"
    assert action.config == config
    assert action.execute() == "Executed"

def test_action_without_execute():
    class InvalidAction(Action):
        config_cls = ActionConfig
        name = "invalid_action"

    config = ActionConfig()
    action = InvalidAction(config)

    with pytest.raises(NotImplementedError):
        action.execute()
