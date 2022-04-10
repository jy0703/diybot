#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telethon import events

from .. import chat_id, jdbot, LOG_DIR
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/?e$'))
async def getbotlog(event):
    try:
        file = f"{LOG_DIR}/bot/run.log"
        await jdbot.send_message(chat_id, "这是bot的运行日志，用于排查问题所在", file=file)
    except Exception as e:
        await push_error(e)