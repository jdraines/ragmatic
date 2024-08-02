from logging import getLogger
import os
from pathlib import Path

import yaml

from ._types import MasterConfig

logger = getLogger(__name__)

def load_config(configpath: Path = None) -> MasterConfig:
    with open(str(configpath)) as f:
        config = yaml.safe_load(f)
    return MasterConfig(**config)

