from telethon import events

from .utils import execute
from .. import jdbot, START_CMD, chat_id, logger
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern='/cmd'))
async def my_cmd(event):
    """接收/cmd命令后执行程序"""
    logger.info(f'即将执行{event.raw_text}命令')
    msg_text = event.raw_text.split(' ')
    try:
        if isinstance(msg_text, list):
            text = ' '.join(msg_text[1:])
        else:
            text = None
        if START_CMD and text:
            info = f'执行 {text} 命令'
            await execute(chat_id, info, text)
            logger.info(text)
        elif START_CMD:
            msg = '请正确使用/cmd命令，如：\n/cmd date  # 系统时间\n不建议直接使用cmd命令执行脚本，请使用/node或/snode'
            await jdbot.send_message(chat_id, msg)
        else:
            await jdbot.send_message(chat_id, '未开启CMD命令，如需使用请修改配置文件')
        logger.info(f'执行{event.raw_text}命令完毕')
    except Exception as e:
        await push_error(e)
        