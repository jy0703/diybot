from telethon import events

from .utils import execute, snode_btn
from .. import chat_id, JD_DIR, jdbot
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/snode'))
async def my_snode(event):
    """定义supernode文件命令"""
    try:
        SENDER = event.sender_id
        path = JD_DIR
        page = 0
        filelist = None
        async with jdbot.conversation(SENDER, timeout=60) as conv:
            msg = await conv.send_message('正在查询，请稍后')
            while path:
                path, msg, page, filelist = await snode_btn(conv, SENDER, path, msg, page, filelist)
        if filelist and filelist.startswith('CMD-->'):
            await execute(chat_id, '', filelist.replace('CMD-->', ''))
    except Exception as e:
        await push_error(e)
        