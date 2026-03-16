# LogWaver
LogWaver is a Python tool for parsing and analyzing Postfix, IMAP, and Roundcube logs. It helps extract useful insights from mail server activity with a focus on simplicity and extensibility.

## Requirements:
- Ubuntu/Kali for easy setup with 2GB RAM
- 1 CPU, the more the merrier
- Storage: 30 GB for VM + 2 * size of logs
- docker compose (easy setup for database)

## How to get ?
```bash
sudo apt install -y libpq-dev python3-dev build-essential
wget https://github.com/UngureanuOvidiu-Costin/LogWaver/archive/main.zip
7z x main.zip
cd LogWaver-main/Parser
```
