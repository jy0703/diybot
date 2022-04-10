#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import os
import re
import time
from asyncio import exceptions

import requests
from telethon import events

from .. import chat_id, jdbot, QL_SQLITE_FILE
from ..bot.utils import get_cks, QL, ql_token, rwcon, V4
from ..diy.utils import QL8, push_error


async def checkCookie(cookie):
    url = "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion"
    headers = {
        "Host": "me-api.jd.com",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "User-Agent": "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "Accept-Language": "zh-cn",
        "Referer": "https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&",
        "Accept-Encoding": "gzip, deflate, br"
    }
    try:
        res = requests.get(url, headers=headers)
        await asyncio.sleep(2)
        data = res.json()
        if data['retcode'] == "1001":
            return False
        else:
            nickname = data['data']['userInfo']['baseInfo']['nickname']
            return nickname
    except Exception as e:
        await jdbot.send_message(chat_id, f"此cookie无法完成检测，请自行斟酌！\n\n{cookie}\n\n错误：{e}")
        return True


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/checkcookie$'))
async def mycheckcookie(event):
    try:
        msg = await jdbot.send_message(chat_id, "正在检测 cookie 过期情况……")
        text, o, res = '检测结果\n\n', '\n\t   └ ', ""
        expireds, valids, changes, removes = [], [], [], []
        if V4:
            cookies = await get_cks()
            for cookie in cookies:
                cknum = cookies.index(cookie) + 1
                check = await checkCookie(cookie)
                if check:
                    res += f"账号{cknum}-{check}有效\n"
                else:
                    res += f"账号{cknum}已过期\n"
                    expireds.append(cknum)
                msg = await jdbot.edit_message(msg, res)
            await asyncio.sleep(2)
        elif QL8:
            token = await ql_token()
            headers = {'Authorization': f'Bearer {token}'}
            url = 'http://127.0.0.1:5600/open/envs'
            body = {'searchValue': 'JD_COOKIE'}
            datas = requests.get(url, params=body, headers=headers).json()['data']
            for data in datas:
                cookie = data['value']
                if "&" in cookie:
                    cookies = cookie.split("&")
                    len_cooke = len(cookies)
                    for ck in cookies:
                        check = await checkCookie(ck)
                        if check:
                            res += f"{check} Cookie：{ck} 有效\n"
                        else:
                            res += f"Cookie：{ck} 已过期\n"
                            cookies.remove(ck)
                            removes.append(ck)
                        msg = await jdbot.edit_message(msg, res)
                        await asyncio.sleep(1)
                    if len(cookies) != len_cooke:
                        try:
                            changes.append([data['remarks'] if 'remarks' in data.keys() else '未备注', '&'.join(cookies), data['_id']])
                        except KeyError:
                            changes.append([data['remarks'] if 'remarks' in data.keys() else '未备注', '&'.join(cookies), data['id']])
                else:
                    cknum = datas.index(data) + 1
                    check = await checkCookie(cookie)
                    if check:
                        res += f"账号{cknum}-{check}有效\n"
                        try:
                            valids.append([data['_id'], data['remarks'] if 'remarks' in data.keys() else '未备注', cknum])
                        except KeyError:
                            valids.append([data['id'], data['remarks'] if 'remarks' in data.keys() else '未备注', cknum])
                    else:
                        res += f"账号{cknum}已过期\n"
                        try:
                            expireds.append([data['_id'], cknum])
                        except KeyError:
                            expireds.append([data['id'], cknum])
                    msg = await jdbot.edit_message(msg, res)
                    await asyncio.sleep(1)
        else:
            token = await ql_token()
            headers = {'Authorization': f'Bearer {token}'}
            url = 'http://127.0.0.1:5600/open/cookies'
            body = {'t': int(round(time.time() * 1000))}
            datas = requests.get(url, params=body, headers=headers).json()['data']
            valids = []
            for data in datas:
                cknum = datas.index(data) + 1
                check = await checkCookie(data['value'])
                if check:
                    res += f"账号{cknum}-{check}有效\n"
                    try:
                        valids.append([data['_id'], data['nickname'], cknum])
                    except KeyError:
                        valids.append([data['id'], data['nickname'], cknum])
                else:
                    res += f"账号{cknum}已过期\n"
                    try:
                        expireds.append([data['_id'], cknum])
                    except KeyError:
                        expireds.append([data['id'], cknum])
                msg = await jdbot.edit_message(msg, res)
                await asyncio.sleep(1)
        if V4:
            configs = rwcon("list")
            for config in configs:
                i = configs.index(config)
                if config.find("TempBlockCookie") != -1 and config.find("##") == -1 and configs[i + 1].find(";") == -1:
                    line = configs.index(config)
                    Temp = configs[line][:-1]
                    configs[line] = f"{Temp}program\n"
                    configs = ''.join(configs)
                    break
            n = " ".join('%s' % expired for expired in expireds)
            configs = re.sub(r'TempBlockCookie=".*"program', f'TempBlockCookie="{n}"', configs, re.M)
            text += f'【屏蔽情况】{o}TempBlockCookie="{n}"\n'
            rwcon(configs)
            await jdbot.edit_message(msg, text)
        elif QL:
            token = await ql_token()
            headers = {'Authorization': f'Bearer {token}'}
            if expireds:
                text += f'【禁用情况】\n'
                for expired in expireds:
                    if QL8:
                        url = 'http://127.0.0.1:5600/open/envs/disable'
                        body = [f"{expired[0]}"]
                        r = requests.put(url, json=body, headers=headers)
                        if r.ok:
                            text += f'账号{expired[1]}：{o}禁用成功，记得及时更新\n'
                        else:
                            text += f'账号{expired[1]}：{o}禁用失败，请手动禁用\n'
                    else:
                        url = 'http://127.0.0.1:5600/open/cookies/disable'
                        body = [f"{expired[0]}"]
                        r = requests.put(url, json=body, headers=headers)
                        if r.ok:
                            text += f'账号{expired[1]}：{o}禁用成功，记得及时更新\n'
                        else:
                            text += f'账号{expired[1]}：{o}禁用失败，请手动禁用\n'
                text += '\n'
            if valids:
                text += f'【启用情况】\n'
                for valid in valids:
                    if QL8:
                        url = 'http://127.0.0.1:5600/open/envs/enable'
                        body = [f"{valid[0]}"]
                        r = requests.put(url, json=body, headers=headers)
                        if r.ok:
                            text += f'账号{valid[2]} - {valid[1]}：{o}启用成功\n'
                        else:
                            text += f'账号{valid[2]} - {valid[1]}：{o}启用失败，请手动启用\n'
                    else:
                        url = 'http://127.0.0.1:5600/open/cookies/enable'
                        body = [f"{valid[0]}"]
                        r = requests.put(url, json=body, headers=headers)
                        if r.ok:
                            text += f'账号{valid[2]} - {valid[1]}：{o}启用成功\n'
                        else:
                            text += f'账号{valid[2]} - {valid[1]}：{o}启用失败，请手动启用\n'
                text += '\n'
            if changes:
                text += f'【更新情况】\n'
                for change in changes:
                    url = 'http://127.0.0.1:5600/open/envs'
                    if os.path.exists(QL_SQLITE_FILE):
                        body = {
                            "name": "JD_COOKIE",
                            "remarks": change[0],
                            "value": change[1],
                            "id": change[2]
                        }
                    else:
                        body = {
                            "name": "JD_COOKIE",
                            "remarks": change[0],
                            "value": change[1],
                            "_id": change[2]
                        }
                    r = requests.put(url, json=body, headers=headers)
                    if r.ok:
                        removes = ' '.join(removes)
                        text += f'更新JD_COOKIE：{o}{body["value"]}\n移除的COOKIE：{o}{removes}\n\n'
                    else:
                        text += f'更新JD_COOKIE：{o}更新失败，请手动更新\n'
            await jdbot.edit_message(msg, text)
    except exceptions.TimeoutError:
        await jdbot.send_message(chat_id, '选择已超时，对话已停止，感谢你的使用')
    except Exception as e:
        await push_error(e)
        