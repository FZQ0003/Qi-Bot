from ..logger import logger

try:
    from .aliyun import AcsToken, AcsTokenData, AcsAccess
except ModuleNotFoundError:
    logger.warning('Aliyun SDK Core not found.')
