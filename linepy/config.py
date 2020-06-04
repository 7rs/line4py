from typing import List, Dict, Optional

from .service.TalkService.ttypes import ApplicationType

LEGY_HOST = "https://legy-jp-addr.line.naver.jp"
OBS_HOST = "https://obs.line-apps.com"
PROFILE_CDN = "https://profile.line-scdn.net"

LONG_POLLING_V4_PATH = "/P4"
TALK_SERVICE_V4_PATH = "/S4"

TALK_SERVICE_V4 = LEGY_HOST + TALK_SERVICE_V4_PATH
LONG_POLLING_V4 = LEGY_HOST + LONG_POLLING_V4_PATH

LINE_USER_AGENTS = {
    ApplicationType.IOS: "Line/10.1.1 iPhone8,1 13.3",
}
LINE_APPLICATIONS = {
    ApplicationType.IOS: "IOS\t10.1.1\tiOS\t13.3",
}
LINE_APP_TYPES: List[ApplicationType] = list(LINE_APPLICATIONS.keys())


class HeaderBuilder:

    user_agent: str
    app: str
    access_token: Optional[str] = None

    def __init__(self,
                 app_type: ApplicationType,
                 access_token: Optional[str] = None):
        if app_type not in LINE_APP_TYPES:
            raise Exception("Undefined application name.")

        self.app = LINE_APPLICATIONS[app_type]
        self.user_agent = LINE_USER_AGENTS[app_type]

        if access_token:
            self.access_token = access_token

    def set_access_token(self, access_token: str):
        self.access_token = access_token

    def to_dict(self) -> Dict[str, str]:
        headers = {
            "User-Agent": self.user_agent,
            "X-Line-Application": self.app,
            "x-lal": "ja_jp",
        }

        if self.access_token:
            headers["X-Line-Access"] = self.access_token

        return headers
