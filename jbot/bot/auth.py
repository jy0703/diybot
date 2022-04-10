import json
import re
import time

import requests
from telethon import events

from .utils import AUTH_FILE
from .. import chat_id, jdbot
from ..diy.utils import push_error


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/auth'))
async def bot_ql_login(event):
    try:
        if not AUTH_FILE:
            await jdbot.send_message(chat_id, '此命令仅支持青龙')
            return
        res = ql_login()
        if res == 'two-factor':
            async with jdbot.conversation(event.sender_id, timeout=100) as conv:
                loop = 3
                info = '两步验证已启用'
                while loop:
                    loop -= 1
                    msg = await conv.send_message(f'{info}\n请输入6位数字验证码：')
                    code = await conv.get_response()
                    if re.search('^\d{6}$', code.raw_text):
                        res = ql_login(code.raw_text)
                        if res == '验证失败':
                            await msg.delete()
                            info = res
                            continue
                        break
                    else:
                        await msg.delete()
                        info = '输入错误'
                        continue
                else:
                    res = '验证未通过，取消登录'
        await jdbot.send_message(chat_id, res)
    except Exception as e:
        await push_error(e)
        

def ql_login(code: str = None):
    try:
        with open(AUTH_FILE, 'r', encoding='utf-8') as f:
            auth = json.load(f)
        token = auth['token']
        if token and len(token) > 10:
            url = "http://127.0.0.1:5600/api/crons"
            params = {
                't': int(round(time.time() * 1000)),
                'searchValue': ''
            }
            headers = {
                'Authorization': f'Bearer {token}'
            }
            res = requests.get(url, params=params, headers=headers).text
            if res.find('code":200') > -1:
                return '当前登录状态未失效\n无需重新登录'
        if code:
            url = 'http://127.0.0.1:5600/api/user/two-factor/login'
            data = {
                'username': auth['username'],
                'password': auth['password'],
                'code': code
            }
            res = requests.put(url, json=data).json()
        else:
            url = 'http://127.0.0.1:5600/api/user/login'
            data = {
                'username': auth['username'],
                'password': auth['password']
            }
            res = requests.post(url, json=data).json()
        if res['code'] == 200:
            return '自动登录成功，请重新执行命令'
        if res['code'] == 420:
            return 'two-factor'
        return res['message']
    except Exception as e:
        return '自动登录出错：' + str(e)
    