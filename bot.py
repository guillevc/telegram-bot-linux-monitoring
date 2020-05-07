#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from dotenv import load_dotenv
import os
import sh

load_dotenv()

TELEGRAM_BOT_AUTHENTICATION_TOKEN = os.getenv('TELEGRAM_BOT_AUTHENTICATION_TOKEN')
SECURITY_ALERTS_CHANNEL = os.getenv('TELEGRAM_SECURITY_ALERTS_CHANNEL')
SYSTEM_MONITORING_CHANNEL = os.getenv('TELEGRAM_SYSTEM_MONITORING_CHANNEL')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

update_id = None

def main():
    global update_id

    bot = telegram.Bot(TELEGRAM_BOT_AUTHENTICATION_TOKEN)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    bot.send_message(SECURITY_ALERTS_CHANNEL, system_summary())

    # while True:
    #     try:
    #         echo(bot)
    #     except NetworkError:
    #         sleep(1)
    #     except Unauthorized:
    #         # The user has removed or blocked the bot.
    #         update_id += 1

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

    message = f'''*SECURITY UPDATES AVAILABLE: {security_updates_count}
    more information
    '''

    return message

# def echo(bot):
#     """Echo the message the user sent."""
#     global update_id
#     # Request updates after the last update_id
#     for update in bot.get_updates(offset=update_id, timeout=10):
#         update_id = update.update_id + 1

#         if update.message:  # your bot can receive updates without messages
#             # Reply to the message
#             update.message.reply_text(update.message.text)
#             bot.send_message(SECURITY_ALERTS_CHANNEL, ' hey')

if __name__ == '__main__':
    main()
