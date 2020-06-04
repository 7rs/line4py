import base64
import time
import hashlib
import hmac

from .service.TalkService.ttypes import ApplicationType
from .session import Session


class Client(Session):

    def __init__(self,
                 app_type: ApplicationType = ApplicationType.IOS,
                 concurrency: int = 30):
        super().__init__(app_type, concurrency)

    def get_issued_at(self) -> bytes:
        return base64.b64encode(
            f"iat: {int(time.time()) * 60}\n".encode("utf-8")) + b"."

    def get_digest(self, key: bytes, iat: bytes) -> bytes:
        return base64.b64encode(hmac.new(key, iat, hashlib.sha1).digest())

    def create_token(self, auth_key: str) -> str:
        mid, key = auth_key.partition(":")[::2]
        key = base64.b64decode(key.encode("utf-8"))
        iat = self.get_issued_at()

        digest = self.get_digest(key, iat).decode("utf-8")
        iat = iat.decode("utf-8")

        return mid + ":" + iat + "." + digest
