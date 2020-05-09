## About
Send linux system reports &amp; security alerts via Telegram.

### System reports
This utility can generate and send system summary reports. Run with the `--send-report` flag.
```
⏳🖥️ UPTIME: up 2 hours, 42 minutes

🔔📋 SECURITY UPDATES AVAILABLE: 0

💻 LAST WEEK LOGINS
User: root
Date: Sat May 9 19:54:49 +0200 2020
--
User: cto
IP: 10.0.2.2
Date: Sat May 9 22:06:17 +0200 2020
--
User: dba
IP: 10.0.2.2
Date: Thu May 7 20:27:06 +0200 2020
--
User: db
Date: Sat May 2 22:55:33 +0200 2020

💽 % DISK USAGE
0% /dev
73% /
1% /tmp
42% /var
30% /boot
11% /home
25% TOTAL
```
### Security alerts
Listens to changes in `/var/log/auth.log` and detects failed attempts to log in the machine. Run with the `--listen-auth-log` flag.
```
⚠️📢 May 10 00:16:29 debian sshd[1386]: Invalid user unknown-user from 10.0.2.2 port 10484
```

## Requirements
Python 3 >= version specified in `runtime.txt`

## Usage
Set the following environment variables. You can set these variables creating a `.env` file; check `.env.example`.
* `TELEGRAM_BOT_AUTHENTICATION_TOKEN`: authentication token of the desired Telegram bot. [You don't have one?](https://core.telegram.org/bots/api#authorizing-your-bot)
* `TELEGRAM_SECURITY_ALERTS_TARGET`: target of the security alerts.
* `TELEGRAM_SYSTEM_REPORTS_TARGET`: target of the system reports.

Install `requirements.txt` dependencies and run `monitor.py` with the desired flag.
```
usage: monitor.py [-h] [--send-report] [--listen-auth-log]

System monitoring via Telegram

optional arguments:
  -h, --help         show this help message and exit
  --send-report      sends week use summary to TELEGRAM_SYSTEM_MONITORING_TARGET
  --listen-auth-log  listens to authentication errors on /var/log/auth.log and sends reports to TELEGRAM_SECURITY_ALERTS_TARGET
```
