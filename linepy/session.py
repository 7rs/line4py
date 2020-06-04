from typing import Optional

from thrift.protocol.TCompactProtocol import TCompactProtocolAccelerated
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

from .service.TalkService.ttypes import ApplicationType
from .service.TalkService import TalkService
from .config import HeaderBuilder, LEGY_HOST, TALK_SERVICE_V4, LONG_POLLING_V4
from .thrift import THttpClient


class Session:
    __concurrency: int

    def __init__(self,
                 app_type: ApplicationType = ApplicationType.IOS,
                 concurrency: int = 30):
        self.header_builder = HeaderBuilder(app_type)
        self.__concurrency = concurrency
        url = URL(LEGY_HOST)
        self.__client = HTTPClient(url.host,
                                   url.port,
                                   concurrency=self.__concurrency,
                                   ssl=True)

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
                       service,
                       client: Optional[HTTPClient] = None):
        trans = self.__get_transport(url, client)
        proto = TCompactProtocolAccelerated(trans)

        return service.Client(proto)

    def set_access_token(self, access_token: str):
        self.header_builder.set_access_token(access_token)

    def create_talk_service_client(self) -> TalkService.Client:
        return self.create_session(TALK_SERVICE_V4, TalkService, self.__client)

    def create_long_polling_client(self) -> TalkService.Client:
        return self.create_session(LONG_POLLING_V4, TalkService, self.__client)
