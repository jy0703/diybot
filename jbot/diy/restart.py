#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

from telethon import events

from .. import chat_id, jdbot
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/restart$'))
async def myrestart(event):
    try:
        cmdtext = "if [ -d '/jd' ]; then cd /jd/jbot; pm2 start ecosystem.config.js; cd /jd; pm2 restart jbot; else " \
                  "ps -ef | grep 'python3 -m jbot' | grep -v grep | awk '{print $1}' | xargs kill -9 2>/dev/null; " \
                  "nohup python3 -m jbot >/ql/log/bot/bot.log 2>&1 & fi "
        await jdbot.send_message(chat_id, "重启程序")
        os.system(cmdtext)
    except Exception as e:
        await push_error(e)
        