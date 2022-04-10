from pathlib import Path
from typing import Union

from ..logger import logger


def _config_warning(path: Union[Path, str]):
    logger.warning(f'{path} not found, use default settings.')
