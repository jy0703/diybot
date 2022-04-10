#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import datetime
import os
import re

from .. import chat_id, jdbot, LOG_DIR, TOKEN

bot_id = int(TOKEN.split(":")[0])


async def execute(msg, info, exectext):
    """
    执行命令
    """
    try:
        info += f'\n\n📣开始执行脚本📣\n\n'
        msg = await msg.edit(info)
        try:
            from ..diy.diy import start
            await start()
        except:
            pass
        p = await asyncio.create_subprocess_shell(exectext, shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=os.environ)
        res_bytes, res_err = await p.communicate()
        try:
            from ..diy.diy import end
            await end()
        except ImportError:
            pass
        res = re.findall(r".*📣==============\n(.*)", res_bytes.decode('utf-8'), re.S)[0]
        if len(res) == 0:
            info += '\n已执行，但返回值为空'
            await msg.edit(info)
            return
        else:
            try:
                logtime = f'执行时间：' + re.findall(r'脚本执行- 北京时间.UTC.8.：(.*?)=', res, re.S)[0] + '\n'
                info += logtime
            except Exception as e:
                pass
            errinfo = '\n\n**——‼错误代码493，IP可能黑了‼——**\n' if re.search('Response code 493', res) else ''
            if len(info + res + errinfo) <= 4000:
                await msg.edit(info + res + errinfo)
            elif len(info + res + errinfo) > 4000:
                tmp_log = f'{LOG_DIR}/bot/{exectext.split("/")[-1].split(".js")[0].split(".py")[0].split(".sh")[0].split(".ts")[0].split(" ")[-1]}-{datetime.datetime.now().strftime("%H-%M-%S.%f")}.log'
                with open(tmp_log, 'w+', encoding='utf-8') as f:
                    f.write(res)
                await msg.delete()
                await jdbot.send_message(chat_id, f'{info}\n执行结果较长，请查看日志{errinfo}', file=tmp_log)
                os.remove(tmp_log)
    except:
        pass
    