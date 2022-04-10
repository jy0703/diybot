#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re

import requests
from telethon import events

from .. import bot_id, chat_id, jdbot
from ..bot.utils import ql_token, rwcon, V4
from ..diy.utils import QL8, push_error


@jdbot.on(events.NewMessage(chats=chat_id, from_users=bot_id, pattern=r'.*cookie已失效.*'))
async def block(event):
    try:
        message = event.message.text.replace("\n", "")
        pt_pin = re.findall("cookie已失效.*京东账号\d+\s(.*)请.*", message)
        if not pt_pin:
            return
        msg = await jdbot.send_message(chat_id, "侦测到cookie失效通知，开始屏蔽账号")
        pt_pin = pt_pin[0]
        line, expired, blocks = None, None, []
        if V4:
            configs = rwcon("list")
            for config in configs:
                if pt_pin in config and "wskey" not in config:
                    expired = int(re.findall(r"[Cc]ookie(\d+)=.*", config)[0])
                    line = configs.index(config)
                    break
                elif "第二区域" in config:
                    await jdbot.edit_message(msg, "请使用标准模板！")
                    return
            for config in configs[line:]:
                if "TempBlockCookie" in config and " TempBlockCookie" not in config and "举例" not in config and ";;" not in configs[configs.index(config) + 1]:
                    line = configs.index(config)
                    blocks = re.findall(r'"([^"]*)"', config)[0]
                    if len(blocks) == 0:
                        blocks = []
                    elif " " in blocks:
                        blocks = list(map(int, blocks.split(" ")))
                    else:
                        blocks = [int(blocks)]
                    break
                elif "AutoDelCron" in config:
                    await jdbot.edit_message(msg, "无法找到 TempBlockCookie 目标字符串，请检查是否使用了标准配置模板")
                    return
            if expired in blocks:
                await jdbot.edit_message(msg, f"pin为{pt_pin}的账号先前已经被屏蔽，因此取消屏蔽！")
            else:
                blocks.append(expired)
                blocks = " ".join('%s' % _ for _ in sorted(blocks, reverse=False))
                configs[line] = f'TempBlockCookie="{blocks}"\n'
                rwcon(configs)
                await jdbot.edit_message(msg, f"pin为{pt_pin}的账号屏蔽成功！")
        elif QL8:
            token = await ql_token()
            url = 'http://127.0.0.1:5600/open/envs'
            headers = {'Authorization': f'Bearer {token}'}
            body = {"searchValue": f";pt_pin={pt_pin};"}
            datas = requests.get(url, headers=headers, json=body).json()['data']
            for data in datas:
                if pt_pin in data['value'] and "pt_key" in data['value']:
                    url = 'http://127.0.0.1:5600/open/envs/disable'
                    try:
                        requests.put(url, headers=headers, json=[data['_id']])
                    except KeyError:
                        requests.put(url, headers=headers, json=[data['id']])
                    await jdbot.edit_message(msg, f"pin为{pt_pin}的账号屏蔽成功！")
                    break
        else:
            token = await ql_token()
            url = 'http://127.0.0.1:5600/open/cookies'
            headers = {'Authorization': f'Bearer {token}'}
            datas = requests.get(url, headers=headers).json()['data']
            for data in datas:
                if pt_pin in data['value'] and "pt_key" in data['value']:
                    url = 'http://127.0.0.1:5600/open/cookies/disable'
                    try:
                        requests.put(url, headers=headers, json=[data['_id']])
                    except KeyError:
                        requests.put(url, headers=headers, json=[data['id']])
                    await jdbot.edit_message(msg, f"pin为{pt_pin}的账号屏蔽成功！")
                    break
    except Exception as e:
        await push_error(e)
        