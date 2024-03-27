from ..logger import logger


# TODO: DataCheckError
class DataCheckError(ValueError):
    ...


def _import_warning(e: ImportError, filetype: str):
    logger.warning(f'Package {e.name} not found, disable {filetype} file support.')
