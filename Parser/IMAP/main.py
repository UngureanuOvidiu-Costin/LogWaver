import re
import gzip
import mysql.connector
from datetime import datetime
from typing import Iterator, Optional, List, Union
from pathlib import Path
from models import ImapLogEntry, MailboxActionEntry
from utils import insert_unparsed_log, parse_all_logs, process_log_file
from utils import insert_log_entry

ParsedLogEntry = Union[ImapLogEntry, MailboxActionEntry]


def main():
    db = mysql.connector.connect(
        host="localhost",
        user="myuser",
        password="mypassword",
        database="mydatabase"
    )
    cursor = db.cursor()

    log_dir = Path("/var/log/mail.log")
    BATCH_SIZE = 1000
    buffer: List[ParsedLogEntry] = []
    count = 0

    for entry in parse_all_logs(log_dir, cursor):
        if isinstance(entry, (ImapLogEntry, MailboxActionEntry)):
            buffer.append(entry)
        else:
            insert_unparsed_log(cursor, entry)

        if len(buffer) >= BATCH_SIZE:
            for e in buffer:
                insert_log_entry(cursor, e)
            db.commit()
            count += len(buffer)
            buffer.clear()

    if buffer:
        for e in buffer:
            insert_log_entry(cursor, e)
        db.commit()
        count += len(buffer)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
