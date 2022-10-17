#!/usr/bin/env python 
# coding=utf-8

import asyncio
import aiohttp

async def post_images(session, file_url, img: bytes):
    data = aiohttp.FormData()
    data.add_field('file', img, content_type='multipart/form-data')
    async with session.post(file_url, data=data) as resp:
        msg = await resp.json()
        if msg['code'] == 0:
            file_id = msg['file']['id']
        else:
            print("文件上传错误。")
    return file_id


async def post(session, memo_url, text, file_ids: list):
    data = {
        "content": text,
        "file_ids": file_ids
        }
    async with session.post(memo_url, json=data) as resp:
        msg = await resp.json()
        if msg['code'] == 0:
            return msg['memo']['slug']
        else:
            print("发文错误", msg)


async def main(memo_url, text, *imgs):
    async with aiohttp.ClientSession() as session:
        if len(imgs) != 0 :
            file_ids = []
            for img in imgs[0]:
                file_id = await post_images(session, memo_url + 'file', img)
                file_ids.append(str(file_id))
            slug = await post(session, memo_url, text, file_ids)
        else:
            slug = await post(session, memo_url, text, [])
    return slug


if __name__ == '__main__':
    url = "https://flomoapp.com/iwh/Msdfasfsa/sadfsdfasdfasdfsa"
    content = "#test memo via python"
    print(asyncio.run(main(url, content)))
