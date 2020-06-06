from typing import Optional
import urllib.parse
import base64
import os

from loguru import logger
import axolotl_curve25519 as curve

from line4py.service.TalkService.ttypes import ApplicationType
from line4py.service.TalkService import TalkService
from line4py.service.SecondaryQrCodeLoginService.ttypes import (
    CreateQrSessionRequest, CreateQrCodeRequest, VerifyCertificateRequest,
    CreatePinCodeRequest, QrCodeLoginRequest, QrCodeLoginResponse,
    SecondaryQrCodeException)
from line4py.service.SecondaryQrCodeLoginPermitNoticeService.ttypes import (
    CheckQrCodeVerifiedRequest, CheckPinCodeVerifiedRequest)
from line4py.session import Session
from line4py.token import create_token


def create_message(*args):
    return "\n".join(args)


class Client(Session):
    talk: TalkService.Client
    poll: TalkService.Client

    access_token: Optional[str] = None
    certificate: Optional[str] = None
    mid: Optional[str] = None

    def __init__(self,
                 app_type: ApplicationType = ApplicationType.IOS,
                 concurrency: int = 30,
                 secondary: bool = False):
        super().__init__(app_type, concurrency, secondary)

    def __login(self, access_token: str):
        self.set_access_token(access_token)
        self.access_token = access_token

        self.talk = self.create_talk_service_client()
        self.poll = self.create_long_polling_client()

    def login_with_auth_key(self, auth_key: str):
        self.mid = auth_key[:33]
        self.__login(create_token(auth_key))

    def login_with_qrcode(self,
                          certificate: Optional[str] = None,
                          system_name: str = "LINE for Python"):
        session_id = self.create_qrcode_session()
        logger.info(f"QRCode Session ID: {session_id}")

        url = self.create_qrcode(session_id)
        secret = self.create_secret()
        logger.info(
            create_message("Please login from this URL on your smartphone",
                           f"URL: {url}{secret}"))

        pincode = self.check_qrcode_and_verify_certificate(
            session_id, certificate)
        if pincode:
            logger.info(
                create_message(
                    f"Enter your {len(pincode)}-digit verification number using Artphone",
                    f"PIN Code: {pincode}"))
            self.check_pincode(session_id)

        response = self.login_with_qrcode_request(session_id, system_name)
        self.certificate = response.certificate
        self.__login(response.accessToken)

    def create_qrcode_session(self) -> str:
        self.lr = self.create_secondary_qr_code_login_service_client()
        return self.lr.createSession(CreateQrSessionRequest()).authSessionId

    def create_qrcode(self, session_id: str) -> str:
        return self.lr.createQrCode(CreateQrCodeRequest(session_id)).callbackUrl

    def check_qrcode_and_verify_certificate(
            self, session_id: str, certificate: Optional[str]) -> Optional[str]:
        self.set_access_token("")
        self.lc = self.create_secondary_qr_code_login_permit_notice_service_client(
        )
        self.lc.checkQrCodeVerified(CheckQrCodeVerifiedRequest(session_id))

        try:
            self.lr.verifyCertificate(
                VerifyCertificateRequest(session_id, certificate))
            return None
        except SecondaryQrCodeException:
            return self.lr.createPinCode(
                CreatePinCodeRequest(session_id)).pinCode

    def check_pincode(self, session_id: str):
        self.lc.checkPinCodeVerified(CheckPinCodeVerifiedRequest(session_id))

    def login_with_qrcode_request(self, session_id: str,
                                  system_name: str) -> QrCodeLoginResponse:
        return self.lr.qrCodeLogin(
            QrCodeLoginRequest(session_id,
                               system_name,
                               autoLoginIsRequired=True))

    def create_secret(self):
        private_key = curve.generatePrivateKey(os.urandom(32))
        public_key = curve.generatePublicKey(private_key)

        secret = urllib.parse.quote(base64.b64encode(public_key).decode())
        version = 1
        return f"?secret={secret}&e2eeVersion={version}"
