from typing import Dict, Optional

from line4py.service.TalkService import TalkService
from line4py.service.TalkService.ttypes import Message, MessageRelationType, ServiceCode


class TalkServiceClient(TalkService.Client):

    def __init__(self, iprot):
        super().__init__(iprot)

    def send_text(self,
                  seq: int,
                  to: str,
                  text: str,
                  content_metadata: Optional[Dict[str, str]] = None,
                  related_message_id: Optional[str] = None):
        msg = Message(
            to=to,
            text=text,
            contentMetadata=content_metadata,
        )
        if related_message_id:
            msg.relatedMessageId = related_message_id
            msg.messageRelationType = MessageRelationType.REPLY
            msg.relatedMessageServiceCode = ServiceCode.TALK

        return self.sendMessage(seq, msg)
