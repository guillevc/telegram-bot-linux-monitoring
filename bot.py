#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
from dotenv import load_dotenv
import os
import sh
import ipaddress

load_dotenv()

TELEGRAM_BOT_AUTHENTICATION_TOKEN = os.getenv('TELEGRAM_BOT_AUTHENTICATION_TOKEN')
SECURITY_ALERTS_CHANNEL = os.getenv('TELEGRAM_SECURITY_ALERTS_CHANNEL')
SYSTEM_MONITORING_CHANNEL = os.getenv('TELEGRAM_SYSTEM_MONITORING_CHANNEL')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def main():
    bot = telegram.Bot(TELEGRAM_BOT_AUTHENTICATION_TOKEN)
    bot.send_message(SECURITY_ALERTS_CHANNEL, system_summary(), parse_mode=telegram.ParseMode.MARKDOWN)

    #last_log_week = sh.lastlog('-t 7').strip()
    #print(repr(last_log_week))
    #print(sh.grep(sh.lastlog('-t 7'), '-v', 'Latest'))
    #input()

    # listen to log files
    auth_log_path = '/var/log/auth.log'
    def on_log_auth_path_new_line(line):
        line = line.strip()
        print('new line detected in auth.log={}'.format())
    #auth_log_tail = sh.tail('-f', '-n 0', auth_log_path, _out=on_log_auth_path_new_line, _bg=True)

    #auth_log_tail.wait()

def system_summary():
    SECURITY_UPDATES_COUNT_COMMAND = 'apt list --upgradable 2>/dev/null | grep "\-security" | wc -l'

    security_updates_count = sh.bash('-c', SECURITY_UPDATES_COUNT_COMMAND)

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
            print(login_dict)
            last_week_logins_dict_list.append(login_dict)

    last_week_logins = ''
    for login_dict in last_week_logins_dict_list:
        last_week_logins += 'User: {}\n'.format(login_dict['user'])
        ip = login_dict['ip']
        if ip != None:
            last_week_logins += 'IP: {}\n'.format(ip)
        last_week_logins += 'Date: {}'.format(login_dict['date'])
    
    print(last_week_logins)

    return \
'''\
*SECURITY UPDATES AVAILABLE*: {}
*LAST WEEK LOGINS*:
{}
*MORE INFO*:\
'''.format(security_updates_count.strip(), last_week_logins)

if __name__ == '__main__':
    main()
