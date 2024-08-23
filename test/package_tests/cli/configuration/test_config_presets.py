from string import Template
import json
import pytest
import sys
import re

from ragmatic.cli.configuration._types import MasterConfig
from ragmatic.cli.configuration.presets import (
    local_docs_preset,
    pycode_preset
)
from ragmatic.cli.configuration.presets._types import PresetData



def _run_one_preset_module(module):
    # Check that a PresetData instance is in the module
    preset = None
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, PresetData):
            preset = obj
            break
    assert preset, f"No PresetData instance found in {module.__name__}"
    _verify_preset_variables(module.__name__, preset)


def _verify_preset_variables(module_name, preset: PresetData):
    # Check that all variables in the preset have a default value
    for var in preset.variable_defaults:
        assert preset.variable_defaults[var] is not None, f"Variable {var} in {preset} has no default value"
    for confidict in [preset.components, preset.pipelines, preset.rag_query_command]:
        configjson = json.dumps(confidict)
        unused = []
        for var in preset.variable_defaults:
            unused.append(var)
        Template(configjson).substitute(preset.variable_defaults)

# define a test function parameterized to run both the local_docs_preset and the pycode_preset modules
@pytest.mark.parametrize("module", [local_docs_preset, pycode_preset])
def test_preset_module(module):
    _run_one_preset_module(module)
