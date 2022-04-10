#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import re

from telethon import events

from .utils import execute
from .. import chat_id, jdbot, TOKEN, OWN_DIR, client
from ..bot.utils import TASK_CMD
from ..diy.utils import myzdjr_chatIds, push_error

bot_id = int(TOKEN.split(":")[0])


@client.on(events.NewMessage(chats=myzdjr_chatIds, pattern=r'export\s(jd_zdjr_activity|jd_joinTeam_activity|FAV|OPEN_CARD|addCart|luckDraw).*=(".*"|\'.*\')'))
async def activity(event):
    """
    监控运行变量
    """
    try:
        msg = await jdbot.send_message(chat_id, '监控到活动变量')
        group = f'[{event.chat.title}](https://t.me/c/{event.chat.id}/{event.message.id})'
        if "jd_zdjr_activity" in event.message.text:
            name = '组队瓜分京豆'
            cmd = f'{TASK_CMD} {OWN_DIR}/smiek_jd_zdjr.js now'
        else:
            await jdbot.delete_messages(chat_id, msg)
            return
        messages = event.message.raw_text.split("\n")
        invalid, unchange = False, True
        for message in messages:
            if "export " not in message:
                continue
            kv = re.sub(r'.*export ', '', message)
            key = kv.split("=")[0]
            value = re.findall(r'"([^"]*)"', kv)[0]
            if "zdjr" in key and len(value) != 32:
                invalid = True
            elif os.environ.get(key) != value:
                os.environ[key] = value
                unchange = False
        if invalid:
            await msg.edit(f"监控到 {group} 的 **{name}** 活动，变量不正确停止运行……")
            return
        elif unchange:
            await msg.edit(f"监控到 {group} 的 **{name}** 活动，变量已重复停止运行……")
            return
        else:
            info = f"监控到 {group} 的 **{name}** 活动"
            await execute(msg, info, cmd)
    except Exception as e:
        await push_error(e)
        