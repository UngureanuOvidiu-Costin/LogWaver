from datetime import datetime


class ImapLogEntry:
    def __init__(self, timestamp: datetime, user: str, ip: str, action: str, raw: str):
        self.timestamp = timestamp
        self.user = user
        self.ip = ip
        self.action = action
        self.raw = raw


class MailboxActionEntry:
    def __init__(self, timestamp: datetime, user: str, action: str, box: str, uid: int,
                 msgid: str, size: int, msg_from: str, subject: str, flags: str, raw: str):
        self.timestamp = timestamp
        self.user = user
        self.action = action
        self.box = box
        self.uid = uid
        self.msgid = msgid
        self.size = size
        self.msg_from = msg_from
        self.subject = subject
        self.flags = flags
        self.raw = raw
