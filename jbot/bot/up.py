import os
from asyncio import exceptions

import requests
from telethon import Button, events

from .update import botlog, version
from .. import BOT_SET, chat_id, JD_DIR, jdbot
from ..bot.utils import press_event
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/upbot$'))
async def myupbot(event):
    try:
        SENDER = event.sender.id
        buttons = [Button.inline("是", "yes"), Button.inline("取消", "cancel")]
        async with jdbot.conversation(SENDER, timeout=180) as conversation:
            msg = await conversation.send_message("前瞻计划及其不稳定，确定需要升级吗？", buttons=buttons)
            byte = await conversation.wait_event(press_event(SENDER))
            res = bytes.decode(byte.data)
            if res == "cancel":
                await jdbot.edit_message(msg, "取消升级")
                return
            else:
                await jdbot.delete_messages(chat_id, msg)
            conversation.cancel()
        msg = await jdbot.send_message(chat_id, "【前瞻计划】\n\n准备更新程序")
        url = "https://raw.githubusercontent.com/chiupam/JD_Diy/master/shell/bot_beta.sh"
        if '下载代理' in BOT_SET.keys() and str(BOT_SET['下载代理']).lower() != 'false' and 'github' in url:
            url = f'{str(BOT_SET["下载代理"])}/{url}'
        resp = requests.get(url).text
        if "#!/usr/bin/env bash" not in resp:
            await jdbot.edit_message(msg, "【前瞻计划】\n\n下载shell文件失败\n请稍后重试，或尝试关闭代理重启")
            return
        with open(f"{JD_DIR}/bot.sh", 'w+', encoding='utf-8') as f:
            f.write(resp)
        text = "【前瞻计划】\n\n更新过程中程序会重启，请耐心等待……\n为安全起见，关闭user监控，请使用 /user 手动开启！"
        await jdbot.edit_message(msg, text)
        os.system(f"bash {JD_DIR}/bot.sh")
    except exceptions.TimeoutError:
        await jdbot.edit_message(msg, '选择已超时，对话已停止，感谢你的使用')
    except Exception as e:
        await push_error(e)


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/ver$', incoming=True))
async def bot_ver(event):
    await jdbot.send_message(chat_id, f'当前版本\n{version}\n{botlog}')
