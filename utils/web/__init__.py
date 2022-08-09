import uvicorn
from fastapi import FastAPI

from ..logger import LogHandler

web_app = FastAPI()

config = uvicorn.Config(
    web_app,
    port=5800,
    log_config={
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "default": {
                "class": LogHandler.__module__ + '.' + LogHandler.__qualname__,
            },
        },
        "loggers": {
            "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.access": {"handlers": ["default"], "level": "INFO"},
        },
    }
)
server = uvicorn.Server(config)
