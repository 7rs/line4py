from typing import List, Dict, Optional

LEGY_HOST = "https://legy-jp-addr.line.naver.jp"
OBS_HOST = "https://obs.line-apps.com"
PROFILE_CDN = "https://profile.line-scdn.net"

TALK_SERVICE_V4 = LEGY_HOST + "/S4"
LONG_POLLING_V4 = LEGY_HOST + "/P4"

LINE_USER_AGENTS = {
    "IOS": "Line/10.1.1 iPhone8,1 13.3",
}
LINE_APPLICATIONS = {
    "IOS": "IOS\t10.1.1\tiOS\t13.3",
}
LINE_APP_NAMES: List[str] = list(LINE_APPLICATIONS.keys())


class HeaderBuilder:

    user_agent: str
    app: str
    access_token: Optional[str] = None

    def __init__(self, app_name: str, access_token: Optional[str] = None):
        if app_name not in LINE_APP_NAMES:
            raise Exception("Undefined application name.")

        self.user_agent = LINE_APPLICATIONS[app_name]
        self.app = LINE_USER_AGENTS[app_name]

        if access_token:
            self.access_token = access_token

    def to_dict(self) -> Dict[str, str]:
        header = {
            "User-Agent": self.user_agent,
            "X-Line-Application": self.app,
        }

        if self.access_token:
            header["X-Line-Access"] = self.access_token

        return header
