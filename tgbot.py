#!/usr/bin/env python 
# coding=utf-8

import shelve
import asyncio
import config

from aiohttp import web
from telebot.async_telebot import AsyncTeleBot, types
from telebot.asyncio_filters import IsReplyFilter, SimpleCustomFilter, TextStartsFilter
from flomoapi import main


API_TOKEN = config.API_TOKEN    #'563623xxxx:AAGg6Fg_sEm1u5sZ1Twg-lhhm2K-xxxxxg'
MODE = config.MODE
WEBHOOK_HOST = config.WEBHOOK_HOST     #'https://bot.tg.com'
WEBHOOK_PORT = config.WEBHOOK_PORT    #8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = config.WEBHOOK_LISTEN    #'127.0.0.1'  # In some VPS you may need to put here the IP addr
WEBHOOK_URL_BASE = "https://{}".format(WEBHOOK_HOST)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)
ADMIN_ID = config.ADMIN_ID


bot = AsyncTeleBot(API_TOKEN)


#Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = types.Update.de_json(request_body_dict)
        asyncio.ensure_future(bot.process_new_updates([update]))
        return web.Response()
    else:
        return web.Response(status=403)


async def shutdown(app):
    await bot.remove_webhook()
    await bot.close_session()

async def setup():
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    await bot.remove_webhook()
    # Set webhook

    await bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
    app = web.Application()
    app.router.add_post('/{token}/', handle)
    app.on_cleanup.append(shutdown)
    return app


# 自定义过滤图片是否是一个组
class IsMediaGroup(SimpleCustomFilter):
    key = 'is_media_group'
    @staticmethod
    async def check(message):
        try:
            return message.media_group_id is not None or message.reply_to_message.media_group_id is not None
        except:
            return False


@bot.message_handler(commands=['start', 'help'])
async def send_auth(message):
    await bot.reply_to(message, '''
        不保存任何信息，但需要绑定flomo api用于推送。  
        实现了文字、单张图文和多张图文的功能，日志功能有时间再说了。
        
        简单使用教程：
        https://telegra.ph/Flomo-Tg-Bot%E6%9C%BA%E5%99%A8%E4%BA%BA-10-13
        ''')


@bot.message_handler(commands=['bind'])
async def bind(message):
   markup = types.ForceReply(selective=False)
   await bot.send_message(message.chat.id, "请输入Flomo api.", reply_markup=markup)


@bot.message_handler(commands=['unbind'])
async def bind(message):
    with shelve.open('info.db', flag='c', protocol=None, writeback=True) as f:
        if str(message.chat.id) in f.keys():
            del f[str(message.chat.id)]
            await bot.reply_to(message, f'{message.chat.id}已经解绑，建议您去flomo后台重置api！')
        else:
            await bot.reply_to(message, f'{message.chat.id}未找到您的绑定信息！')


@bot.message_handler(is_reply=True, text_startswith='https://flomoapp.com')
async def save_info(message):
    if message.text.startswith("https://flomoapp.com"):
        with shelve.open('info.db', flag='c', protocol=None, writeback=False) as f:
            f[str(message.chat.id)] = message.text
        await bot.reply_to(message, f'{message.chat.id}绑定{message.text}成功！')
    if ADMIN_ID != '':
        try:
            await bot.send_message(ADMIN_ID, f'{message.chat.id}注册')
        except ValueError as e:
            print(e)
    else:
        await bot.reply_to(message, "请输入正确的flomo api")


@bot.message_handler(is_reply=False, content_types=['text'])
async def send_memo_by_words(message):
    with shelve.open('info.db', flag='c', protocol=None, writeback=False) as f:
        if str(message.chat.id) in f.keys():
            url = f[str(message.chat.id)]
        else:
            await bot.reply_to(message, "未绑定flomo api，请先绑定后再使用。")
            return
    try:
        slug = await main(str(url), message.text)
        memo_url = "https://v.flomoapp.com/mine/?memo_id=" + slug
        await bot.reply_to(message, memo_url)
    except Exception as e:
        await bot.reply_to(message, f"出错了，重来吧！{e}")


@bot.message_handler(content_types=['photo'], is_media_group=False)
async def send_memo_by_words_and_img(message):
    with shelve.open('info.db', flag='c', protocol=None, writeback=False) as f:
        if str(message.chat.id) in f.keys():
            url = f[str(message.chat.id)]
        else:
            await bot.reply_to(message, "未绑定flomo api，请先绑定后再使用。")
            return

    file_path = await bot.get_file(message.photo[-1].file_id)
    downloaded_file = await bot.download_file(file_path.file_path)
    images = [downloaded_file]
    try:
        slug = await main(str(url), message.caption, images)
        memo_url = "https://v.flomoapp.com/mine/?memo_id=" + slug
        await bot.reply_to(message, memo_url)
    except Exception as e:
        print("出错了")
        await bot.reply_to(message, f"出错了，重来吧！{e}")


group_id = {}
@bot.message_handler(content_types=['photo'], is_media_group=True)
async def get_photos(message):
    media_group_id = message.media_group_id
    file_id = await bot.get_file(message.photo[-1].file_id)
    group_id.setdefault(media_group_id, []).append(file_id.file_path)
    # markup = types.ForceReply(selective=False)
    # await bot.send_message(message.chat.id, "请输入Memo", reply_markup=markup)
    await bot.reply_to(message, file_id.file_path)

@bot.message_handler(content_types=['text', 'photo'], is_reply=True, is_media_group=True)
async def send_memo_by_words_and_photos(message):
    media_group_id = message.reply_to_message.media_group_id
    with shelve.open('info.db', flag='c', protocol=None, writeback=False) as f:
        if str(message.chat.id) in f.keys():
            url = f[str(message.chat.id)]
        else:
            await bot.reply_to(message, "未绑定flomo api，请先绑定后再使用。")
            return

    images = []
    for file_path in group_id[media_group_id]:
        downloaded_file = await bot.download_file(file_path)
        images.append(downloaded_file)

    try:
        slug = await main(url, message.text, images)
        memo_url = "https://v.flomoapp.com/mine/?memo_id=" + slug
        await bot.reply_to(message, memo_url)
        del group_id[media_group_id]
    except Exception as e:
        print("出错了")
        await bot.reply_to(message, f"出错了，重来吧！{e}")



bot.add_custom_filter(IsReplyFilter())
bot.add_custom_filter(IsMediaGroup())
bot.add_custom_filter(TextStartsFilter())
# 轮询

#


if __name__ == '__main__':
    if MODE == 'webhook':
        # Start aiohttp server
        web.run_app(
            setup(),
            host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT
        )
    elif MODE == 'polling':
        asyncio.run(bot.remove_webhook())
        asyncio.run(bot.polling())
    else:
        pass