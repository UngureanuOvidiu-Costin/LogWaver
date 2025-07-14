import gzip
from typing import Iterator, Union
from pathlib import Path
from models import ImapLogEntry, MailboxActionEntry
from authenticationParser import parse_imap_authentication
from mailBoxActionsParser import parse_imap_mailbox_actions


ParsedLogEntry = Union[ImapLogEntry, MailboxActionEntry]


def process_log_file(path: Path, cursor=None) -> Iterator[ParsedLogEntry]:
    open_fn = gzip.open if path.suffix == ".gz" else open
    with open_fn(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parsed = (
                parse_imap_authentication(line)
                or parse_imap_mailbox_actions(line)
            )
            if parsed:
                yield parsed
            elif cursor:
                insert_unparsed_log(cursor, line.strip())


def insert_unparsed_log(cursor, raw_line: str):
    cursor.execute("""
        INSERT INTO to_be_parsed (raw)
        VALUES (%s)
    """, (raw_line,))
            

def parse_all_logs(log_dir: Path, cursor) -> Iterator[ParsedLogEntry]:
    for file in sorted(log_dir.glob("imap.log*")):
        yield from process_log_file(file, cursor)

def insert_log_entry(cursor, entry: ParsedLogEntry):
    if isinstance(entry, ImapLogEntry):
        cursor.execute("""
            INSERT INTO imap_logs (timestamp, user, ip, action, raw)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            entry.timestamp,
            entry.user,
            entry.ip,
            entry.action,
            entry.raw
        ))

    elif isinstance(entry, MailboxActionEntry):
        cursor.execute("""
            INSERT INTO mailbox_actions (
                timestamp, user, action, box, uid,
                msgid, size, msg_from, subject, flags, raw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            entry.timestamp,
            entry.user,
            entry.action,
            entry.box,
            entry.uid,
            entry.msgid,
            entry.size,
            entry.msg_from,
            entry.subject,
            entry.flags,
            entry.raw
        ))

