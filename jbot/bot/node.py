from telethon import events

from .utils import execute, TASK_CMD
from .. import chat_id, jdbot
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern='/node'))
async def bot_node(event):
    """接收/node命令后执行程序"""
    try:
        msg_text = event.raw_text.split(' ')
        if isinstance(msg_text, list) and len(msg_text) == 2:
            text = ''.join(msg_text[1:])
        else:
            text = None
        if not text:
            res = '''请正确使用/node命令，如
    /node /abc/123.js 运行abc/123.js脚本
    /node /own/abc.js 运行own/abc.js脚本'''
            await jdbot.send_message(chat_id, res)
        else:
            await execute(chat_id, f'执行 {text} 命令', f'{TASK_CMD} {text}')
    except Exception as e:
        await push_error(e)
        