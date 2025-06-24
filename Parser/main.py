import gzip
import os
import glob
from typing import Union, List, Dict, Generator


# TODO: make this possible to be passed as parameter
LOG_DIR = "/var/log/"

# TODO: make this possible to be passed as parameter, the users might want a limited area of logs
LOG_PATTERNS = ["mail.log", "imap.log"]

def open_log_file(filepath: str) -> Generator[str, None, None]:
    """
    Opens a plain or gzipped log file and yields lines.
    """
    if not isinstance(filepath, str):
        raise TypeError("Expected 'filepath' to be string.")

    if filepath.endswith(".gz"): 
        with gzip.open(filepath, "rt", encoding="utf-8", errors="ignore") as f:
            for line in f:
                yield line
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                yield line


def find_log_files(directory: str, patterns: List[str]) -> List[str]:
    """
    Finds logs files based on given patterns.
    """
    if not isinstance(directory, str):
        raise TypeError("Expected 'directory' to be a string.")
    if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
        raise TypeError("Expected 'patterns' to be a list of strings.")
    
    result = []
    for pattern in patterns:
        result.extend(glob.glob(os.path.join(directory, pattern)))
    return sorted(result)
