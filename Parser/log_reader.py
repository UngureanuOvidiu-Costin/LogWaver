import os
import gzip
import glob
from typing import Iterator, List
from dotenv import load_dotenv

load_dotenv()


class LogFileReader:
    def __init__(self):
        self.log_path = os.getenv('LOG_PATH', '/var/log/mail.log')
        self.encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    def get_log_files(self) -> List[str]:
        log_dir = os.path.dirname(self.log_path)
        log_name = os.path.basename(self.log_path)

        files = []
        if os.path.exists(self.log_path):
            files.append(self.log_path)

        compressed_pattern = os.path.join(log_dir, f"{log_name}.*")
        compressed_files = glob.glob(compressed_pattern)

        compressed_files = [f for f in compressed_files if f.endswith('.gz')]
        compressed_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        return files + compressed_files

    def read_file_with_encoding(self, file_path: str) -> Iterator[str]:
        is_compressed = file_path.endswith('.gz')

        for encoding in self.encodings_to_try:
            try:
                if is_compressed:
                    with gzip.open(file_path, 'rt', encoding=encoding) as f:
                        for line in f:
                            yield line.strip()
                else:
                    with open(file_path, 'r', encoding=encoding) as f:
                        for line in f:
                            yield line.strip()
                return
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return

        print(f"Failed to read {file_path} with any encoding")

    def read_all_logs(self) -> Iterator[str]:
        log_files = self.get_log_files()

        for file_path in reversed(log_files[1:]):
            print(f"Reading {file_path}")
            for line in self.read_file_with_encoding(file_path):
                if line:
                    yield line

        if log_files:
            print(f"Reading {log_files[0]}")
            for line in self.read_file_with_encoding(log_files[0]):
                if line:
                    yield line
