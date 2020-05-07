#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
from dotenv import load_dotenv
import os
import sh

load_dotenv()

TELEGRAM_BOT_AUTHENTICATION_TOKEN = os.getenv('TELEGRAM_BOT_AUTHENTICATION_TOKEN')
SECURITY_ALERTS_CHANNEL = os.getenv('TELEGRAM_SECURITY_ALERTS_CHANNEL')
SYSTEM_MONITORING_CHANNEL = os.getenv('TELEGRAM_SYSTEM_MONITORING_CHANNEL')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def main():
    bot = telegram.Bot(TELEGRAM_BOT_AUTHENTICATION_TOKEN)

    bot.send_message(SECURITY_ALERTS_CHANNEL, system_summary(), parse_mode=telegram.ParseMode.MARKDOWN)

    print(sh.last())

    # listen to log files
    auth_log_path = '/var/log/auth.log'
    def on_log_auth_path_new_line(line):
        line = line.strip()
        logger.info(f'new line detected in auth.log={line}')
    auth_log_tail = sh.tail('-f', '-n 0', auth_log_path, _out=on_log_auth_path_new_line, _bg=True)

    auth_log_tail.wait()

def system_summary():
    SECURITY_UPDATES_COUNT_COMMAND = 'apt list --upgradable 2>/dev/null | grep "\-security" | wc -l'

    security_updates_count = sh.bash('-c', SECURITY_UPDATES_COUNT_COMMAND)

    return \
f'''\
*SECURITY UPDATES AVAILABLE*: {security_updates_count.strip()}
*aaa*: bbb
more information
a
c
d\
'''

if __name__ == '__main__':
    main()
