from typing import Optional

from thrift.protocol.TCompactProtocol import TCompactProtocolAccelerated
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

from line4py.service.TalkService.ttypes import ApplicationType
from line4py.service.TalkService import TalkService
from line4py.service.SecondaryQrCodeLoginService import SecondaryQrCodeLoginService
from line4py.service.SecondaryQrCodeLoginPermitNoticeService import SecondaryQrCodeLoginPermitNoticeService
from line4py.config import (HeaderBuilder, LEGY_HOST, TALK_SERVICE_V4,
                            LONG_POLLING_V4, SECONDARY_LOGIN_REQUEST_V1,
                            SECONDARY_LOGIN_CHECK_V1)
from line4py.thrift import THttpClient
from line4py.api import TalkServiceClient, LongPollingClient

DEFAULT_TIMEOUT = 180.0


class Session:
    __concurrency: int

    def __init__(self,
                 app_type: ApplicationType = ApplicationType.IOS,
                 concurrency: int = 30,
                 secondary: bool = False):
        self.header_builder = HeaderBuilder(app_type, secondary=secondary)
        self.__concurrency = concurrency
        url = URL(LEGY_HOST)
        self.__client = HTTPClient(url.host,
                                   url.port,
                                   concurrency=self.__concurrency,
                                   ssl=True,
                                   connection_timeout=DEFAULT_TIMEOUT,
                                   network_timeout=DEFAULT_TIMEOUT)

    def __get_transport(self,
                        url: str,
                        client: Optional[HTTPClient] = None) -> THttpClient:
        if client:
            return THttpClient(url,
                               self.header_builder.to_dict(),
                               self.__concurrency,
                               client=client)
        else:
            return THttpClient(url, self.header_builder.to_dict(),
                               self.__concurrency)

    def create_session(self,
                       url: str,
                       service_client,
                       http_client: Optional[HTTPClient] = None):
        trans = self.__get_transport(url, http_client)
        proto = TCompactProtocolAccelerated(trans)

        return service_client(proto)

    def set_access_token(self, access_token: str):
        self.header_builder.set_access_token(access_token)

    def create_talk_service_client(self) -> TalkService.Client:
        return self.create_session(TALK_SERVICE_V4, TalkServiceClient,
                                   self.__client)

    def create_long_polling_client(self) -> TalkService.Client:
        return self.create_session(LONG_POLLING_V4, LongPollingClient,
                                   self.__client)

    def create_secondary_qr_code_login_service_client(
            self) -> SecondaryQrCodeLoginService.Client:
        return self.create_session(SECONDARY_LOGIN_REQUEST_V1,
                                   SecondaryQrCodeLoginService.Client,
                                   self.__client)

    def create_secondary_qr_code_login_permit_notice_service_client(
            self) -> SecondaryQrCodeLoginPermitNoticeService.Client:
        return self.create_session(
            SECONDARY_LOGIN_CHECK_V1,
            SecondaryQrCodeLoginPermitNoticeService.Client, self.__client)
