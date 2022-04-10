#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

from requests import get, post, put
from telethon import Button, events

from .. import chat_id, CONFIG_DIR, jdbot
from ..bot.utils import press_event, ql_token, row, rwcon, split_list, V4
from ..diy.utils import QL2, wskey, push_error


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^pin=.*;wskey=.*'))
async def myaddwskey(event):
    try:
        text = ""
        msg = await jdbot.send_message(chat_id, "获取到wskey，正在工作中……")
        messages = event.raw_text.split("\n")
        if V4:
            file = f"{CONFIG_DIR}/wskey.list"
        else:
            file = "/ql/db/wskey.list"
        if not os.path.exists(file):
            if V4 or QL2:
                configs = rwcon("str")
                if "wskey" not in configs:
                    sender = event.sender_id
                    async with jdbot.conversation(sender, timeout=120) as conv:
                        tip = "由于这是你第一次使用此功能，关于wskey的存储位置，请做出您的选择："
                        buttons = [
                            Button.inline("存储在config.sh中", data="config.sh"),
                            Button.inline("存储在wskey.list中", data="wskey.list"),
                            Button.inline('取消会话', data='cancel')
                        ]
                        msg = await jdbot.edit_message(msg, tip, buttons=split_list(buttons, row))
                        convdata = await conv.wait_event(press_event(sender))
                        res = bytes.decode(convdata.data)
                        if res == 'cancel':
                            await jdbot.edit_message(msg, '对话已取消')
                            return False
                        elif res == 'wskey.list':
                            os.system(f"touch {file}")
                        msg = await jdbot.edit_message(msg, f'你的选择是：存储在{res}中\n准备继续工作……')
            else:
                token = await ql_token()
                url = 'http://127.0.0.1:5600/open/envs'
                headers = {'Authorization': f'Bearer {token}'}
                body = {'searchValue': "JD_WSCK"}
                data = get(url, headers=headers, params=body).json()['data']
                if not data:
                    sender = event.sender_id
                    async with jdbot.conversation(sender, timeout=120) as conv:
                        tip = "由于这是你第一次使用此功能，关于wskey的存储位置，请做出您的选择："
                        buttons = [
                            Button.inline("存储在wskey.list中", data="wskey.list"),
                            Button.inline("存储在环境变量中", data="环境变量"),
                            Button.inline('取消会话', data='cancel')
                        ]
                        msg = await jdbot.edit_message(msg, tip, buttons=split_list(buttons, row))
                        convdata = await conv.wait_event(press_event(sender))
                        res = bytes.decode(convdata.data)
                        if res == 'cancel':
                            await jdbot.edit_message(msg, '对话已取消')
                            return False
                        elif res == 'wskey.list':
                            os.system(f"touch {file}")
                        msg = await jdbot.edit_message(msg, f'你的选择是：存储在{res}中\n准备继续工作……')
        if os.path.exists(file):
            for message in messages:
                ws = re.findall(r'(pin=.*)(wskey=[^;]*);*', message)[0]
                pin, key = ws[0], ws[1]
                message = pin + key + ";"
                pt_pin = re.findall(r'pin=(.*);', pin)[0]
                configs = wskey("str")
                if pin + "wskey" in configs:
                    configs = re.sub(f"{pin}wskey=.*;", message, configs)
                    text += f"更新wskey成功！pin为：{pt_pin}\n"
                else:
                    configs += message + "\n"
                    text += f"新增wskey成功！pin为：{pt_pin}\n"
                msg = await jdbot.edit_message(msg, text)
                wskey(configs)
        elif V4 or QL2:
            for message in messages:
                ws = re.findall(r'(pin=.*)(wskey=[^;]*);*', message)[0]
                pin, key = ws[0], ws[1]
                message = pin + key + ";"
                pt_pin = re.findall(r'pin=(.*);', pin)[0]
                configs = rwcon("str")
                if pin + "wskey" in configs:
                    configs = re.sub(f'{pin}wskey=.*;', message, configs)
                    text += f"更新wskey成功！pin为：{pt_pin}\n"
                elif V4 and f"pt_pin={pt_pin}" in configs:
                    configs = rwcon("list")
                    for config in configs:
                        if f"pt_pin={pt_pin}" in config:
                            line = configs.index(config)
                            num = re.findall(r'(?<=[Cc]ookie)[\d]+(?==")', config)[0]
                            configs.insert(line, f'wskey{num}="{message}"\n')
                            text += f"新增wskey成功！pin为：{pt_pin}\n"
                            break
                        elif "第二区域" in config:
                            await jdbot.send_message(chat_id, "请使用标准模板！")
                            return
                elif V4 and f"pt_pin={pt_pin}" not in configs:
                    configs, line, num = rwcon("list"), 0, 0
                    for config in configs:
                        if "pt_pin" in config and "##" not in config:
                            line = configs.index(config) + 1
                            num = int(re.findall(r'(?<=[Cc]ookie)[\d]+(?==")', config)[0]) + 1
                        elif "第二区域" in config:
                            break
                    configs.insert(line, f'Cookie{str(num)}="pt_key=xxxxxx;pt_pin={pt_pin};"\n')
                    configs.insert(line, f'wskey{str(num)}="{message}"\n')
                    text += f"新增wskey成功！pin为：{pt_pin} 但请在配置中输入cookie值！\n"
                else:
                    configs = rwcon("str")
                    configs += f"{message}\n"
                    text += f"新增wskey成功！pin为：{pt_pin}\n"
                msg = await jdbot.edit_message(msg, text)
                rwcon(configs)
        else:
            token = await ql_token()
            url = 'http://127.0.0.1:5600/open/envs'
            headers = {'Authorization': f'Bearer {token}'}
            for message in messages:
                ws = re.findall(r'(pin=.*)(wskey=[^;]*);*', message)[0]
                pin, key = ws[0], ws[1]
                message = pin + key + ";"
                pt_pin = re.findall(r'pin=(.*);', pin)[0]
                body = {'searchValue': pin + "wskey="}
                data = get(url, headers=headers, params=body).json()['data']
                if data:
                    try:
                        body = {"value": message, "name": "JD_WSCK", "_id": data[0]['_id']}
                    except KeyError:
                        body = {"value": message, "name": "JD_WSCK", "id": data[0]['id']}
                    put(url, headers=headers, json=body)
                    text += f"更新wskey成功！pin为：{pt_pin}\n"
                else:
                    body = [{"name": "JD_WSCK", "value": message}]
                    code = post(url, json=body, headers=headers).json()['code']
                    if code == 500:
                        post(url, headers=headers, json=body[0])
                    text += f"新增wskey成功！pin为：{pt_pin}\n"
                msg = await jdbot.edit_message(msg, text)
        if len(text) > 1:
            if os.path.exists("/jd/own/wskey_ptkey.py"):
                text += "\n将自动更新cookie列表，自行查看更新情况"
                os.system("python /jd/own/wskey_ptkey.py")
            elif os.path.exists("/jd/scripts/wskey_ptkey.py"):
                text += "\n将自动更新cookie列表，自行查看更新情况"
                os.system("python /jd/scripts/wskey_ptkey.py")
            elif os.path.exists("/ql/scripts/wskey_ptkey.py"):
                text += "\n将自动更新cookie列表，自行查看更新情况"
                os.system("task /ql/scripts/wskey_ptkey.py")
            elif os.path.exists("/ql/scripts/ql_pandaAPI_refreshCK.py") and not os.path.exists("/ql/db/wskey.list"):
                text += "\n将自动更新cookie列表，自行查看更新情况"
                os.system("task /ql/scripts/ql_pandaAPI_refreshCK.py")
            elif os.path.exists("/ql/raw/ql_pandaAPI_refreshCK.py") and not os.path.exists("/ql/db/wskey.list"):
                text += "\n将自动更新cookie列表，自行查看更新情况"
            elif os.path.exists("/ql/scripts/ql_pandaAPI_refreshCK.py") and os.path.exists("/ql/db/wskey.list"):
                text += "\n由于使用wskey.list存储，无法执行scripts目录下的ql_pandaAPI_refreshCK.py脚本"
            elif os.path.exists("/ql/raw/ql_pandaAPI_refreshCK.py") and os.path.exists("/ql/db/wskey.list"):
                text += "\n由于使用wskey.list存储，无法执行raw目录下的ql_pandaAPI_refreshCK.py脚本"
            if "自动更新" in text or "无法执行" in text:
                await jdbot.edit_message(msg, text)
    except Exception as e:
        await push_error(e)
        