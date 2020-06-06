import base64
import time
import hashlib
import hmac


def get_issued_at() -> bytes:
    return base64.b64encode(
        f"iat: {int(time.time()) * 60}\n".encode("utf-8")) + b"."


def get_digest(key: bytes, iat: bytes) -> bytes:
    return base64.b64encode(hmac.new(key, iat, hashlib.sha1).digest())


def create_token(auth_key: str) -> str:
    mid, key = auth_key.partition(":")[::2]
    key = base64.b64decode(key.encode("utf-8"))
    iat = get_issued_at()

    digest = get_digest(key, iat).decode("utf-8")
    iat = iat.decode("utf-8")

    return mid + ":" + iat + "." + digest
