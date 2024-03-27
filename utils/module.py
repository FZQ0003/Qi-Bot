"""Qi-Bot module manager."""
import pkgutil
from typing import Iterator


def get_modules(root_path: str = 'modules') -> Iterator[str]:
    """Get (saya) modules."""
    for module_info in pkgutil.iter_modules([root_path]):
        if not (module_name := module_info.name).startswith('_'):
            yield f"{root_path}.{module_name}"
