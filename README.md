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
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
nano .env  # To edit the log path
# Install docker and docker compose first: https://docs.docker.com/engine/install/ubuntu/
# This is just for an easy database setup
docker compose up -d
```

## How to use ?
- Connect to the database: `psql -h localhost -d postfix_logs -U postfix_user # default password is secure_password_123`
- View the tables: `\dt`
- View the columns of tabe `smtpd_logs`: `\d+ smtpd_logs`
- Check for spoofing: `select * from amavis_logs where sender <> from_address;`

## Email flow
smtpd -> qmgr -> smtp -> amavis(+spam assasin) -> smtpd -> qmgr -> smtp
