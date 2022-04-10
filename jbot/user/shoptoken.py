#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re

from telethon import events

from .. import chat_id, client, jdbot
from ..bot.utils import V4, rwcon
from ..diy.utils import shoptokenIds, push_error


@client.on(events.NewMessage(chats=shoptokenIds, pattern=r'^export\sMyShopToken=(\".+?\"|\'.+?\')|^店铺签到检测.*'))
async def shoptoken(event):
    """
    添加删除店铺签到
    """
    try:
        message = event.message.text
        if "export" in message:
            msg = await jdbot.send_message(chat_id, '获取到到MyShopToken变量')
            name = message.split("=")[0]
            token = message.split("=")[1]
            value = re.findall(r'(?<=").*(?=")', token)[0]
            configs = rwcon("str")
            if "export MyShopToken" not in configs:
                if V4:
                    old = re.findall(r'\n## ↑+ 第五区域', configs)[0]
                    new = '\nexport MyShopToken1=""\n'
                    configs = re.sub(old, new + old, configs)
                else:
                    configs += 'export MyShopToken1=""\n'
            if "export SHOP_TOKENS" not in configs:
                if V4:
                    old = re.findall(r'\n## ↑+ 第五区域', configs)[0]
                    new = '\nexport SHOP_TOKENS="${MyShopToken1}"\n'
                    configs = re.sub(old, new + old, configs)
                else:
                    configs += 'export SHOP_TOKENS="${MyShopToken1}"\n'
            config = re.findall(r'export MyShopToken\d+="(.+)"', configs)
            if len(value) != 32:
                await jdbot.edit_message(msg, "获取到店铺签到，该变量不正确...")
                return
            elif configs.find(value) != -1:
                await jdbot.edit_message(msg, "获取到店铺签到，该变量已存在...")
                return
            elif len(config) >= 20:
                await jdbot.edit_message(msg, "获取到店铺签到，已满20个店铺变量，不进行新增...")
            elif len(config) == 0:
                configs = re.sub('export MyShopToken1=""', f'export MyShopToken1="{value}"', configs)
                info = f"新增店铺签到完成，当前店铺数量:{len(config) + 1}\n"
                end = f'```{name}="{value}"```'
                await jdbot.edit_message(msg, info + end)
            else:
                i = 0
                oldtext = ""
                for index in range(len(config)):
                    i += 1
                    oldtext += f'export MyShopToken{i}="{config[int(i) - 1]}"\n'
                config.insert(0, f'{value}')
                i = 0
                newtext = ""
                for index in range(len(config)):
                    i += 1
                    newtext += f'export MyShopToken{i}="{config[int(i) - 1]}"\n'
                configs = re.sub(oldtext, newtext, configs)
                if len(config) <= 20:
                    merge = re.findall(r'export SHOP_TOKENS="(.*)"', configs)[0]
                    end = f'export SHOP_TOKENS="{merge}&${{MyShopToken{len(config)}}}"'
                    configs = re.sub(r'export SHOP_TOKENS=".*"', end, configs)
                info = f"新增店铺签到完成，当前店铺数量:{len(config)}\n"
                end = f'```{name}="{value}"```'
                await jdbot.edit_message(msg, info + end)
            rwcon(configs)
        elif "店铺签到检测" in message:
            kv = message.replace("\n", "").split("。")
            chart = []
            check = []
            m = -1
            for _ in kv:
                m += 1
                check += re.findall(r"【店铺.*已签到.*", kv[m])
                chart += re.findall(f"【店铺(\d+)】签到活动已失效", kv[m])
            n = -1
            for _ in check:
                day = []
                n += 1
                try:
                    day += re.findall(f"签到(\d+)天,获得\d+豆；\s\s└已签到：(\d+)天", check[n])[0]
                except:
                    continue
                if int(day[1]) >= int(day[0]):
                    chart += re.findall(f"【店铺(\d+)】", check[n])
            charts = sorted(chart, key=int)
            p = -1
            for _ in charts:
                p += 1
                nums = charts[p]
                num = int(nums) - p
                configs = rwcon("str")
                config = re.findall(r'export MyShopToken\d+="(.+)"', configs)
                if config:
                    if len(config) == 1:
                        configs = re.sub(r'export MyShopToken1=".*"', r'export MyShopToken1=""', configs)
                        rwcon(configs)
                        info = f"监测到店铺{nums}签到已结束\n\n已经移除店铺{nums}，当前店铺数量: 0\n"
                        await jdbot.send_message(chat_id, info)
                        break
                    i = 0
                    oldtext = ""
                    for index in range(len(config)):
                        i += 1
                        oldtext += f'export MyShopToken{i}="{config[int(i) - 1]}"\n'
                    del config[int(num) - 1]
                    i = 0
                    newtext = ""
                    for index in range(len(config)):
                        i += 1
                        newtext += f'export MyShopToken{i}="{config[int(i) - 1]}"\n'
                    configs = re.sub(oldtext, newtext, configs)
                    if len(config) < 20:
                        configs = re.sub('&\${MyShopToken\d+}\"', '"', configs)
                    rwcon(configs)
                    info = f"监测到店铺{nums}签到已结束\n\n已经移除店铺{nums}，当前店铺数量:{len(config)}\n"
                    await jdbot.send_message(chat_id, info)
                else:
                    await jdbot.send_message(chat_id, 'config.sh文件内未找到店铺变量')
                    break
    except Exception as e:
        await push_error(e)
        