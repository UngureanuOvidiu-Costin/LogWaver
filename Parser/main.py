import sys
from dotenv import load_dotenv
from Postfix.AMAVIS.parser import parse_amavis_log_line
from Postfix.SMTP.parser import parse_smtp_log_line
from Postfix.models import QmgrLog, SmtpdLog, AmavisLog, SmtpLog
from database import DatabaseManager
from log_reader import LogFileReader
from parsers import parse_smtpd_log_line, parse_postfix_log_line


def main():
    load_dotenv()
    processed_count = int(0)

    db_manager = DatabaseManager()
    log_reader = LogFileReader()

    try:
        with open("unparsed.txt", "wt", encoding='utf-8') as unparsed_file:
            db_manager.create_tables()

            for line in log_reader.read_all_logs():
                if "roundcube" not in line and "SSL_" not in line:
                    try:
                        log_entry = parse_postfix_log_line(line)

                        if log_entry is None:
                            unparsed_file.write(line + "\n")
                            print(line)
                        else:
                            db_manager.add_to_buffer(log_entry)
                            processed_count += 1
                            if processed_count % 10000 == 0:
                                print(f"Processed {processed_count} log entries...")
                    except Exception as e:
                        unparsed_file.write(f"Error processing line: {e} | Line: {line}\n")


            print("Flushing remaining buffers...")
            db_manager.flush_all_buffers()

            print(f"Processing complete!")
            print(f"Processed: {processed_count} log entries")

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        print("Flushing buffers before exit...")
        db_manager.flush_all_buffers()
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        db_manager.flush_all_buffers()
        sys.exit(1)


if __name__ == "__main__":
    main()