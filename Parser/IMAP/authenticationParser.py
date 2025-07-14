import re
from typing import Iterator, Optional, List, Union
from models import ImapLogEntry, MailboxActionEntry
from datetime import datetime


IMAP_REGEX_LOGIN_ATTEMPTS = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T[\d:.]+[+\-]\d{2}:\d{2})\s+\S+\s+dovecot: imap-login: '
    r'(?P<action_line>[^:]+):\s*(.*auth failed.*)?user=<(?P<user>[^>]+)>,.*?rip=(?P<rip>[\d\.]+)'
)

IMAP_LOGGED_OUT_REGEX = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T[\d:.]+[+-]\d{2}:\d{2})\s+mail dovecot: imap\((?P<user>[^)]+)\)(?:<[^>]+>)+: Disconnected: Logged out.*'
)

ParsedLogEntry = Union[ImapLogEntry, MailboxActionEntry]


def parse_imap_authentication(line: str) -> Optional[ParsedLogEntry]:

    match = IMAP_LOGGED_OUT_REGEX.search(line)
    if match:
        try:
            dt = datetime.fromisoformat(match.group("timestamp"))
        except ValueError:
            return None
        return ImapLogEntry(
            timestamp=dt,
            user=match.group("user"),
            ip="unknown",
            action="logout",
            raw=line.strip()
        )


    match = IMAP_REGEX_LOGIN_ATTEMPTS.search(line)
    if match:
        try:
            dt = datetime.fromisoformat(match.group("timestamp"))
        except ValueError:
            return None

        action_line = match.group("action_line").strip()
        if "auth failed" in line:
            action = "fail"
        elif action_line.lower() == "login":
            action = "login"
        elif action_line.lower() == "disconnected":
            action = "logout"
        elif action_line.lower() == "aborted login":
            action = "fail"
        else:
            action = "unknown"

        return ImapLogEntry(
            timestamp=dt,
            user=match.group("user"),
            ip=match.group("rip"),
            action=action,
            raw=line.strip()
        )
    return None
