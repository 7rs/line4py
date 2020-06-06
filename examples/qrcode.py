from loguru import logger

from line4py import Client, ApplicationType

client = Client(ApplicationType.ANDROIDLITE, concurrency=30, secondary=True)
client.login_with_qrcode()

logger.info(f"Access Token: {client.access_token}")
