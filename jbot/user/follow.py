#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re

from telethon import events

from .. import chat_id, jdbot, TOKEN, client
from ..bot.utils import V4, CONFIG_SH_FILE, get_cks, AUTH_FILE
from ..diy.utils import getbean, my_chat_id, push_error

bot_id = int(TOKEN.split(":")[0])


@client.on(events.NewMessage(chats=[-1001320212725, -1001630980165, my_chat_id]))
async def follow(event):
    try:
        url = re.findall(re.compile(r"[(](https://api\.m\.jd\.com.*?)[)]", re.S), event.message.text)
        if not url:
            return
        i = 0
        info = '关注店铺\n'
        for cookie in get_cks(CONFIG_SH_FILE if V4 else AUTH_FILE):
            i += 1
            info += getbean(i, cookie, url[0])
        await jdbot.send_message(chat_id, info)
    except Exception as e:
        await push_error(e)
        