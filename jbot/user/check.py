from asyncio import sleep

from telethon import events

from .. import chat_id, client, jdbot
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r"^/check$"))
async def check(event):
    try:
        if client.is_connected():
            await event.reply("`user成功连接Telegram服务器！`")
            await sleep(5)
            await event.delete()
        else:
            await event.reply("`user无法连接Telegram服务器！`")
    except Exception as e:
        await push_error(e)
