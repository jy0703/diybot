#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from asyncio import sleep

from telethon import events

from .. import chat_id, client
from ..diy.utils import push_error


@client.on(events.NewMessage(from_users=chat_id, pattern=r"^user(\?|？)$"))
async def user(event):
    try:
        await event.edit(r'`监控已正常启动！`')
        await sleep(5)
        await event.delete()
    except Exception as e:
        await push_error(e)
