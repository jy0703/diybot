import os
import traceback

from telethon import events

from .utils import log_btn
from .. import BOT_SET, ch_name, chat_id, JD_DIR, jdbot, LOG_DIR, logger
from ..diy.utils import push_error



@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/log$'))
async def bot_log(event):
    """定义日志文件操作"""
    try:
        SENDER = event.sender_id
        path = LOG_DIR
        page = 0
        filelist = None
        async with jdbot.conversation(SENDER, timeout=60) as conv:
            msg = await conv.send_message('正在查询，请稍后')
            while path:
                path, msg, page, filelist = await log_btn(conv, SENDER, path, msg, page, filelist)
    except Exception as e:
        await push_error(e)


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/e$'))
async def getbotlog(event):
    try:
        file = f"{LOG_DIR}/bot/run.log"
        await jdbot.send_message(chat_id, "Bot运行日志……", file=file)
    except Exception as e:
        await push_error(e)


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/getfile'))
async def bot_getfile(event):
    """定义获取文件命令"""
    try:
        SENDER = event.sender_id
        path = JD_DIR
        page = 0
        msg_text = event.raw_text.split(' ')
        if len(msg_text) == 2:
            text = msg_text[-1]
        else:
            text = None
        if text and os.path.isfile(text):
            await jdbot.send_message(chat_id, '请查收文件', file=text)
            return
        elif text and os.path.isdir(text):
            path = text
            filelist = None
        elif text:
            await jdbot.send_message(chat_id, '请确认它是目录还是文件')
            filelist = None
        else:
            filelist = None
        async with jdbot.conversation(SENDER, timeout=60) as conv:
            msg = await conv.send_message('正在查询，请稍后')
            while path:
                path, msg, page, filelist = await log_btn(conv, SENDER, path, msg, page, filelist)
    except Exception as e:
        await push_error(e)
        