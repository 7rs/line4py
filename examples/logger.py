import os

from dotenv import load_dotenv
from loguru import logger
from gevent.pool import Pool

from line4py import Client, ApplicationType
from line4py.service.TalkService.ttypes import Operation, OpType, Message, MIDType, ContentType


def received_message(op: Operation):
    msg: Message = op.message

    if msg.toType != MIDType.GROUP:
        return
    elif msg.contentType != ContentType.NONE:
        return
    elif not msg.text:
        return

    logger.info(msg.text)


def start(client: Client, pool: Pool):
    while True:
        operations = client.poll.handle(client.poll.fetch())

        for func, op in operations.items():
            pool.spawn(func, op)

        pool.join()


if __name__ == "__main__":
    c = 30

    load_dotenv(".env")

    client = Client(ApplicationType.IOS, concurrency=c)
    client.login_with_auth_key(os.getenv("AUTH_KEY"))

    client.poll.set_last_revision()
    client.poll.add_operation(OpType.RECEIVE_MESSAGE, received_message)

    start(client, Pool(c))
