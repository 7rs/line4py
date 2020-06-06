from typing import Dict, Optional
from io import BytesIO

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL
from geventhttpclient.response import HTTPSocketPoolResponse
from thrift.transport.TTransport import TTransportBase

from line4py.config import LONG_POLLING_V4_PATH


class THttpClient(TTransportBase):
    __custom_headers: Dict[str, str]
    __wbuf: BytesIO
    __response: Optional[HTTPSocketPoolResponse] = None
    __looped: bool = False
    __concurrency: int
    __url: URL

    __once_client: HTTPClient
    client: HTTPClient

    code: Optional[int] = None
    message: Optional[str] = None
    headers: Optional[str] = None

    def __init__(self,
                 url: str,
                 headers: Dict[str, str],
                 concurrency: int = 30,
                 client: Optional[HTTPClient] = None):
        self.__url = URL(url)
        self.__custom_headers = headers
        self.__concurrency = concurrency

        if not client:
            self.client = HTTPClient(self.__url.host,
                                     self.__url.port,
                                     concurrency=self.__concurrency,
                                     ssl=True)
        else:
            self.client = client

        if self.__url.path != LONG_POLLING_V4_PATH:
            self.flush = self.__flush
        else:
            self.open()
            self.flush = self.__flush_and_reconnect

        self.__wbuf = BytesIO()

    def __flush_and_reconnect(self):
        if not self.__looped:
            self.close()
            self.open()
            self.__looped = True
        else:
            self.flush = self.__flush
            self.close()
            self.flush()
            return

        data = self.__get_data()
        headers = self.__get_headers(data)

        self.__response = self.__once_client.request("POST",
                                                     self.__url.path,
                                                     body=data,
                                                     headers=headers)
        self.__set_response(self.__response)

    def __flush(self):
        data = self.__get_data()
        headers = self.__get_headers(data)

        self.__response = self.client.request("POST",
                                              self.__url.path,
                                              body=data,
                                              headers=headers)
        self.__set_response(self.__response)

    def __get_data(self) -> bytes:
        data = self.__wbuf.getvalue()
        self.__wbuf = BytesIO()
        return data

    def __get_headers(self, data: bytes) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/x-thrift",
            "Content-Length": str(len(data)),
            'connection': 'keep-alive',
        }
        headers.update(self.__custom_headers)

        return headers

    def __set_response(self, response: HTTPSocketPoolResponse):
        self.code = response.status_code
        self.message = response.status_message
        self.headers = response.headers

    def open(self):
        self.__once_client = HTTPClient(self.__url.host,
                                        self.__url.port,
                                        concurrency=self.__concurrency,
                                        ssl=True)

    def close(self):
        self.__once_client.close()
        self.__response = None

    def read(self, sz: int) -> bytes:
        return self.__response.read(sz)

    def write(self, buf: bytes):
        self.__wbuf.write(buf)
