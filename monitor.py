#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
from dotenv import load_dotenv
import os
import sh
import ipaddress
import argparse
import sys

load_dotenv()

ERROR_AUTH_LOG_LINES_TOKENS = ['invalid user', 'connection closed']

TELEGRAM_BOT_AUTHENTICATION_TOKEN = os.getenv('TELEGRAM_BOT_AUTHENTICATION_TOKEN')
SECURITY_ALERTS_CHANNEL = os.getenv('TELEGRAM_SECURITY_ALERTS_TARGET')
SYSTEM_MONITORING_CHANNEL = os.getenv('TELEGRAM_SYSTEM_REPORTS_TARGET')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='System monitoring via Telegram', add_help=True)
    parser.add_argument('--send-report', action='store_true', help='sends week use summary to TELEGRAM_SYSTEM_REPORTS_TARGET')
    parser.add_argument('--listen-auth-log', action='store_true', help='listens to login attempts on /var/log/auth.log and sends reports to TELEGRAM_SECURITY_ALERTS_TARGET')
    args = parser.parse_args()

    bot = telegram.Bot(TELEGRAM_BOT_AUTHENTICATION_TOKEN)

    if args.send_report:
        bot.send_message(SYSTEM_MONITORING_CHANNEL, get_system_summary_str(), parse_mode=telegram.ParseMode.MARKDOWN)
    elif args.listen_auth_log:
        # listen to log files
        auth_log_path = '/var/log/auth.log'
        def on_log_auth_path_new_line(line):
            line = line.strip()
            print('new line detected in auth.log={}'.format(line))
            if any(token in line.lower() for token in ERROR_AUTH_LOG_LINES_TOKENS):
                bot.send_message(SECURITY_ALERTS_CHANNEL, get_security_alert_str(line), parse_mode=telegram.ParseMode.MARKDOWN)
        auth_log_tail = sh.tail('-f', '-n 0', auth_log_path, _out=on_log_auth_path_new_line, _bg=True)
        auth_log_tail.wait()
    else:
        parser.print_usage()
        sys.exit(1)

def get_security_alert_str(text):
    return '⚠️📢 `{}`'.format(text)

def get_last_week_logins():
    last_week_logins_dict_list = []
    for line in sh.lastlog('-t 7'):
        line = line.strip().split()
        if line[0] != 'Username':
            login_dict = dict()
            login_dict['user'] = line[0]
            try:
                ipaddress.ip_address(line[2])
                login_dict['ip'] = line[2]
                login_dict['date'] = ' '.join(line[3:])
            except ValueError:
                login_dict['ip'] = None
                login_dict['date'] = ' '.join(line[2:])
            last_week_logins_dict_list.append(login_dict)
    return last_week_logins_dict_list

def get_system_summary_str():
    SECURITY_UPDATES_COUNT_COMMAND = 'apt list --upgradable 2>/dev/null | grep "\-security" | wc -l'

    security_updates_count = sh.bash('-c', SECURITY_UPDATES_COUNT_COMMAND)

    last_week_logins = get_last_week_logins()
    last_week_logins_str = ''
    for i, login_dict in enumerate(last_week_logins):
        last_week_logins_str += 'User: {}\n'.format(login_dict['user'])
        ip = login_dict['ip']
        if ip != None:
            last_week_logins_str += 'IP: {}\n'.format(ip)
        last_week_logins_str += 'Date: {}\n'.format(login_dict['date'])
        if i < len(last_week_logins) - 1:
            last_week_logins_str += '--\n'

    available_space_str = ''
    for i, line in enumerate(sh.df('-h', '--total')):
        line = line.strip().split()
        if line[0] != 'Filesystem':
            if line[5] == '-':
                line[5] = 'TOTAL'
            available_space_str += '{} {}\n'.format(line[4], line[5])

    uptime_str = sh.uptime('-p')

    return \
'''\
⏳🖥️ *UPTIME*: {}

🔔📋 *SECURITY UPDATES AVAILABLE*: {}

💻 *LAST WEEK LOGINS*
`{}`

💽 *% DISK USAGE*
`{}`\
'''.format(uptime_str.strip(), security_updates_count.strip(), last_week_logins_str.strip(), available_space_str.strip())

if __name__ == '__main__':
    main()
