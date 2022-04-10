#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import os

import requests

from .. import bot_id, chat_id, CONFIG_DIR
from ..bot.utils import add_cron_V4, cron_manage_QL, mycron, press_event, QL, ql_token, V4

with open(f"{CONFIG_DIR}/diybotset.json", 'r', encoding='utf-8') as f:
    diybotset = json.load(f)
my_chat_id = int(diybotset['my_chat_id'])


def myids(values: str = None, *test_id):
    if values:
        value = eval(values)
        if isinstance(value, int):
            ids = [value]
        else:
            ids = list(value)
        ids.extend(list(test_id))
    else:
        ids = list(test_id)
    return ids


myzdjr_chatIds = myids(diybotset['myzdjr_chatId'], my_chat_id)

myjoinTeam_chatIds = myids(diybotset['myjoinTeam_chatId'], my_chat_id)

shoptokenIds = myids(diybotset['shoptokenId'], my_chat_id, bot_id)

listenerIds = myids(diybotset['listenerId'], my_chat_id)

QL8, QL2 = False, False
if os.path.exists('/ql/config/env.sh'):
    QL8 = True
else:
    QL2 = True


# 读写wskey.list
def wskey(arg):
    if V4:
        file = f"{CONFIG_DIR}/wskey.list"
    else:
        file = "/ql/db/wskey.list"
    if arg == "str":
        with open(file, 'r', encoding='utf-8') as f1:
            wskey = f1.read()
        return wskey
    elif arg == "list":
        with open(file, 'r', encoding='utf-8') as f1:
            wskey = f1.readlines()
        return wskey
    elif "wskey" in arg and "pin" in arg:
        with open(file, 'w', encoding='utf-8') as f1:
            f1.write(arg)


# user.py调用
def getbean(i, cookie, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Cookie": cookie,
    }
    result, o = '', '-->'
    try:
        res = requests.get(url=url, headers=headers).json()
        if res['code'] == '0':
            followDesc = res['result']['followDesc']
            if followDesc.find('成功') != -1:
                try:
                    for n in range(len(res['result']['alreadyReceivedGifts'])):
                        redWord = res['result']['alreadyReceivedGifts'][n]['redWord']
                        rearWord = res['result']['alreadyReceivedGifts'][n]['rearWord']
                        result += f"{o}获得{redWord}{rearWord}"
                except:
                    giftsToast = res['result']['giftsToast'].split(' \n ')[1]
                    result = f"{o}{giftsToast}"
            elif followDesc.find('已经') != -1:
                result = f"{o}{followDesc}"
        else:
            result = f"{o}Cookie 可能已经过期"
    except Exception as e:
        if str(e).find('(char 0)') != -1:
            result = f"{o}无法解析数据包"
        else:
            result = f"{o}访问发生错误：{e}"
    return f"\n账号{str(i).zfill(2)}{result}"


# 修改原作者的 cronup() 函数便于我继续进行此功能的编写
async def mycronup(jdbot, conv, resp, filename, msg, SENDER, markup, path):
    try:
        cron = mycron(resp)
        msg = await jdbot.edit_message(msg, f"这是我识别的定时\n```{cron}```\n请问是否需要修改？", buttons=markup)
    except:
        msg = await jdbot.edit_message(msg, f"我无法识别定时，将使用默认定时\n```0 0 * * *```\n请问是否需要修改？", buttons=markup)
    convdata3 = await conv.wait_event(press_event(SENDER))
    res3 = bytes.decode(convdata3.data)
    if res3 == 'confirm':
        await jdbot.delete_messages(chat_id, msg)
        msg = await conv.send_message("请回复你需要设置的 cron 表达式，例如：0 0 * * *")
        cron = await conv.get_response()
        cron = cron.raw_text
        msg = await jdbot.edit_message(msg, f"好的，你将使用这个定时\n```{cron}```")
        await asyncio.sleep(1.5)
    await jdbot.delete_messages(chat_id, msg)
    if QL:
        crondata = {"name": f'{filename.split(".")[0]}', "command": f'task {path}/{filename}', "schedule": f'{cron}'}
        token = await ql_token()
        cron_manage_QL('add', crondata, token)
    else:
        add_cron_V4(f'{cron} mtask {path}/{filename}')
    info = '添加定时任务成功'
    msg = await jdbot.send_message(chat_id, info)
    return msg, info


async def push_error(e):
    """
    推送错误消息
    """
    title = "【💥错误💥】\n\n"
    name = f"文件名：{os.path.split(__file__)[-1].split('.')[0]}\n"
    function = f"函数名：{e.__traceback__.tb_frame.f_code.co_name}\n"
    details = f"\n错误详情：第 {str(e.__traceback__.tb_lineno)} 行\n"
    tip = "\n建议百度/谷歌进行查询"
    push = f"{title}{name}{function}错误原因：{str(e)}{details}{traceback.format_exc()}{tip}"
    await jdbot.send_message(chat_id, push)
    logger.error(f"错误 {str(e)}")
