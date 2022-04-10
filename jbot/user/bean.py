import os
import re
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from prettytable import PrettyTable
from telethon import events

from .beandata import get_bean_data, get_bean_datas
from .. import BOT_DIR, bot_id, chat_id, client, jdbot, LOG_DIR
from ..diy.utils import push_error

FONT_FILE = f'{BOT_DIR}/font/jet.ttf'


@client.on(events.NewMessage(from_users=chat_id, pattern=r'^/bean|^-b\s?(([ioa]\s?(\d+-+\d+|\d+)?)?|\d*)$'))
async def bot_bean(event):
    message = event.raw_text
    if "-b" in message:
        if 'i' in message:
            num = re.findall('(\d+.*)', message)
            num = f' {num[0]}' if num else ''
            message = f'/bean in{num}'
        elif 'o' in message:
            num = re.findall('(\d+.*)', message)
            num = f' {num[0]}' if num else ''
            message = f'/bean out{num}'
        elif 'a' in message:
            num = re.findall('(\d+.*)', message)
            num = f' {num[0]}' if num else ''
            message = f'/bean all{num}'
        elif re.search(f'\d', message):
            num = re.findall("\d+", message)[0]
            message = f'/bean {num}'
        else:
            message = '/bean 1'
    msg_text = message.split(' ', 1)
    if event.chat_id == bot_id:
        client_type = jdbot
        channel = chat_id
        msg = await jdbot.send_message(chat_id, '正在查询，请稍后')
    else:
        client_type = client
        channel = event.chat_id
        msg = await event.edit('正在查询，请稍后')
    try:
        if isinstance(msg_text, list) and len(msg_text) == 2:
            text = msg_text[-1]
        else:
            text = None
        BEAN_IMG, info = '', ''
        if text and re.search('^\d+$', text):
            res = await get_bean_data(int(text))
            if res['code'] != 200:
                await msg.delete()
                await client_type.send_message(channel, f'{str(res["data"])}')
            else:
                BEAN_IMG = creat_bean_count(res['data'][3], res['data'][0], res['data'][1], res['data'][2][1:])
                await msg.delete()
                await client_type.send_message(channel, f'您的账号{text}收支情况', file=BEAN_IMG)
        elif text and re.search('^(in|out|all)(\s?(\d+|\d+-\d+))?$', text):
            if ' ' in text and '-' in text:
                place = text.split(' ')[-1].split('-')
                x, y = int(place[0]) - 1, int(place[-1])
            elif ' ' in text:
                place = text.split(' ')
                x, y = None, int(place[-1])
            else:
                x, y = None, None
            if isinstance(x, int) and isinstance(y, int) and x >= y:
                await msg.delete()
                await client_type.send_message(channel, '查询失败，参数n-m有误，n需小于m')
                return
            res = await get_bean_datas(x, y)
            if res['code'] != 200:
                await msg.delete()
                await client_type.send_message(channel, f'{str(res["data"])}')
            else:
                if 'all' in text:
                    BEAN_IMG = creat_bean_counts(res['data'][3], res['data'][2], x if isinstance(x, int) else 0)
                    info = '总数'
                elif 'in' in text:
                    BEAN_IMG = creat_bean_counts(res['data'][3], res['data'][0], x if isinstance(x, int) else 0)
                    info = '收入'
                elif 'out' in text:
                    BEAN_IMG = creat_bean_counts(res['data'][3], res['data'][1], x if isinstance(x, int) else 0)
                    info = '支出'
            if BEAN_IMG and info:
                await msg.delete()
                order = f'{x + 1}-{y}' if isinstance(x, int) and isinstance(y, int) else f'1-{y}' if isinstance(y, int) else ''
                await client_type.send_message(channel, f'您的账号{order}近日{info}情况', file=BEAN_IMG)
        else:
            await msg.delete()
            await client_type.send_message(channel, f'请正确使用命令\n/bean n\n/bean all m|n-m\n/bean in m|n-m\n/bean out m|n-m\n n-m为第n-m个账号，不加数字为全部账号，单个数字为1-m')
        if isinstance(BEAN_IMG, list):
            for img in BEAN_IMG:
                try:
                    os.remove(img)
                except OSError:
                    pass
        elif BEAN_IMG:
            try:
                os.remove(BEAN_IMG)
            except OSError:
                pass
    except Exception as e:
        await push_error(e)


def creat_bean_count(date, beansin, beansout, beanstotal):
    tb = PrettyTable()
    tb.add_column('DATE', date)
    tb.add_column('BEANSIN', beansin)
    tb.add_column('BEANSOUT', beansout)
    tb.add_column('TOTAL', beanstotal)
    font = ImageFont.truetype(FONT_FILE, 18)
    im = Image.new("RGB", (500, 260), (244, 244, 244))
    dr = ImageDraw.Draw(im)
    dr.text((10, 5), str(tb), font=font, fill="#000000")
    BEAN_IMG = f'{LOG_DIR}/bot/bean-{uuid4()}.jpg'
    im.save(BEAN_IMG)
    return BEAN_IMG


def creat_bean_counts(date, beans, order):
    title = ['DATE']
    title.extend(date)
    beans = [beans[i:i + 30] for i in range(0, len(beans), 30)]
    BEAN_IMG_LIST = []
    loop = 0
    for bean in beans:
        tb = PrettyTable(title)
        for i in range(len(bean)):
            count = ['COUNT' + str(loop + i + order + 1)]
            count.extend(bean[i])
            tb.add_row(count)
        loop += 30
        length = 108 + 25 * len(bean)
        im = Image.new("RGB", (1250, length), (244, 244, 244))
        dr = ImageDraw.Draw(im)
        font = ImageFont.truetype(FONT_FILE, 20)
        dr.text((10, 5), str(tb), font=font, fill="#000000")
        BEAN_IMG = f'{LOG_DIR}/bot/bean-{uuid4()}.jpg'
        BEAN_IMG_LIST.append(BEAN_IMG)
        im.save(BEAN_IMG)
    return BEAN_IMG_LIST
