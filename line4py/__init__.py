import sys

from loguru import logger

from .service.TalkService.ttypes import ApplicationType
from .client import Client

log_format = "<blue>{time:%s}:{process}</blue> <cyan>{name}:{line}</cyan> <level>{level: <8} | {message}</level>" % (
    "YYYY-MM-DD-HH:mm:ss.SSS")

logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True, format=log_format)
logger.add("logs/line4py.log",
           level="DEBUG",
           format=log_format,
           rotation="1 MB",
           retention=10)
