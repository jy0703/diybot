#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
import os
import re
import time

from telethon import events

from .. import chat_id, jdbot, JD_DIR, TOKEN, client
from ..bot.utils import cmd
from ..diy.utils import my_chat_id, push_error

bot_id = int(TOKEN.split(":")[0])


@client.on(events.NewMessage(chats=[-1001159808620, my_chat_id], pattern=r".*京豆雨.*"))
async def red(event):
    """
    龙王庙京豆雨
    关注频道：https://t.me/longzhuzhu
    """
    try:
        file = "jredrain.sh"
        if not os.path.exists(f'{JD_DIR}/{file}'):
            cmdtext = f'cd {JD_DIR} && wget https://raw.githubusercontent.com/chiupam/JD_Diy/master/other/{file}'
            await cmd(cmdtext)
            if not os.path.exists(f'{JD_DIR}/{file}'):
                await jdbot.send_message(chat_id, f"【龙王庙】\n\n监控到RRA，但是缺少{file}文件，无法执行定时")
                return
        message = event.message.text
        RRAs = re.findall(r'RRA.*', message)
        Times = re.findall(r'开始时间.*', message)
        for RRA in RRAs:
            i = RRAs.index(RRA)
            cmdtext = f"/cmd bash {JD_DIR}/{file} {RRA}"
            Time_1 = Times[i].split(" ")[0].split("-")
            Time_2 = Times[i].split(" ")[1].split(":")
            Time_3 = time.localtime()
            year, mon, mday = Time_3[0], Time_3[1], Time_3[2]
            if int(Time_2[0]) >= 8:
                await client.send_message(bot_id, cmdtext, schedule=datetime.datetime(year, int(Time_1[1]), int(Time_1[2]), int(Time_2[0]) - 8, int(Time_2[1]), 0, 0))
            else:
                await client.send_message(bot_id, cmdtext, schedule=datetime.datetime(year, int(Time_1[1]), int(Time_1[2]) - 1, int(Time_2[0]) + 16, int(Time_2[1]), 0, 0))
            await jdbot.send_message(chat_id, f'监控到RRA：{RRA}\n预定时间：{Times[i].split("：")[1]}\n\n将在预定时间执行脚本，具体请查看当前机器人的定时任务')
    except Exception as e:
        await push_error(e)
        