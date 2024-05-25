import os.path
from datetime import datetime

import aiohttp
import asyncio
import uuid
from tortoise import Tortoise

from models.image import Author, Image, Tag
from settings import TORTOISE_ORM
from utils.Log import Log, Error
from models.server import Cookie

import PIL.Image


stop_worker = False
count = 0
failed_list = []

proxy = 'http://127.0.0.1:7890'

headers = {
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Referer': 'https://www.pixiv.net/',
    'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

cookies = {}

async def check_cookies():
    cookie_raw="first_visit_datetime_pc=2024-01-20%2012%3A13%3A56; p_ab_id=5; p_ab_id_2=5; p_ab_d_id=159194759; yuid_b=ORNFVGA; __utmz=235335808.1705720468.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); privacy_policy_notification=0; a_type=0; privacy_policy_agreement=6; _im_vid=01HMJE3CFRM9JFN8QW164B2QGJ; login_ever=yes; cto_bundle=DFAPNl9IdTRVMEtRYWZkUTVONVZXamhlMElJNFQzbGJSTjRYcW5lcUw1byUyRktWQWVFYjFVViUyQjNvdzNKRGN4TFNWTDR4RG42OCUyQmNHOVN3VHQxRkd4NTdPNmhYTDFaQVR2Wk1IcXJXbGZBandUMm10b2h5MHhtdkdLb01jZTlPOUZBdGlSOGF5d0EzcmpsbTZmbkx6VkVTYyUyQmg4QSUzRCUzRA; cto_bidid=R13TiF9BM0tIdGFkaTJaaXVIWjhPJTJGakJVYVhOVGZQdDNoWG4lMkZmM2R0eWIxaURxJTJGUVpWOUE0OG9XRmxuaWRySmR2OTlLMFlSYnVQRU82empwZ1dLNE1VTzRZeHRneTFWN2wyQ0JuMTBnRUVOUXFZMCUzRA; _im_vid=01HMJE3CFRM9JFN8QW164B2QGJ; _im_uid.3929=i.rAX3czQIQDa_ySjpvevMKA; FCNEC=%5B%5B%22AKsRol-0aXCOebiYDcAJDKF3sy0FNGOXlUZZMiUedT7hnMpvY0TYdwmPz0I6-NQr5jNHdxj7vsSl0rG_7UQGFOSNlqQNFjW9b1GRbegIDUlFgFzsb4EpSYhw9vhaXV_ATwfH49slywotVmanUu4pwPSUP1TaE84iBQ%3D%3D%22%5D%5D; _gcl_au=1.1.1552814137.1713944632; cf_clearance=TlVF6Im3eJxLjd1iaPRltAQvpsaIZcT53VmlpMajog0-1715142914-1.0.1.1-i9C6QJS.9g.7veT4BmJgFj39JAzbBoYNoY6HxIVVzCIumKz2kAhC7wdqccazGbgvg3XICi6MgAbynh.fyiNYDw; device_token=4cc2d6e926c0007437ff863cbb31f246; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; _gid=GA1.2.756179219.1716530812; __cf_bm=2MkdKAL0A57wqhpVB9MACRUNU_L1OWV8YbyPCibZIfQ-1716622370-1.0.1.1-y26hM15xhZ4rNDN24i8CEFJA2rT87XQkpPCqd9DVAn0lP6Bowum1sQAJqACpWHdXOOHVUhQom6g_y_XTjQPpIdQ6itjYF4MC1t8Dm2mnn40; __utma=235335808.1136182024.1705720468.1716571507.1716622372.53; __utmc=235335808; cf_clearance=E47h3tpGighAUMSRXrhE0WPOn_Bsd_pAkzuM7LiuY5o-1716622372-1.0.1.1-ViP9YOQbxbY1TTLaewbE8f_eGO8k8ClRTZlpAjV1Z_eTDP85jIiu350G9rmGWj_0atyrWclthTXt1biffpukWw; __utmt=1; cc1=2024-05-25%2016%3A47%3A28; _gat_UA-1830249-3=1; PHPSESSID=106144205_YYrQnkH3cQdXTnhBysDszbE4jChw6GES; c_type=23; b_type=1; _ga_MZ1NL4PHH0=GS1.1.1716623254.11.1.1716623274.0.0.0; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=106144205=1^9=p_ab_id=5=1^10=p_ab_id_2=5=1^11=lang=zh=1; __utmb=235335808.22.10.1716622372; _ga_75BBYNYN9J=GS1.1.1716622374.67.1.1716623277.0.0.0; _ga=GA1.2.1136182024.1705720468"
    # Splitting the string by ';' to separate key-value pairs
    cookie_list = cookie_raw.split('; ')

    # Creating a dictionary to store key-value pairs

    # Looping through each key-value pair and adding it to the dictionary
    for item in cookie_list:
        key_value_pair = item.split('=')
        key = key_value_pair[0]
        value = '='.join(key_value_pair[1:])
        cookies[key] = value


async def fetch_all_images_by_author_id(uid):
    await check_cookies()
    global stop_worker, count, failed_list
    stop_worker = False
    count = 0
    failed_list = []
    await Tortoise.init(config=TORTOISE_ORM)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        await fetch_author(uid, session)

    await fetch(uid, session)


async def fetch_author(uid, session):
    url = f'https://www.pixiv.net/ajax/user/{uid}?full=1' # 请求完整用户信息
    tmp = await Author.filter(uid=uid).first()
    if tmp is None:
        Log("Author不存在")
        while 1 :
            try:
                async with session.get(url, headers=headers, cookies=cookies, proxy=proxy) as response:
                    json_data = await response.json()
                    name = json_data['body']['name']
                    await Author.create(uid=uid, name=name, source='Pixiv', lastUpdatedTime=datetime.now())
                Log("加入Author成功")
                return False
            except Exception as e:
                Error("查询Pixiv用户时出现未知错误" + str(e))
    else:
        Log("Author已存在")
        return True


async def fetch(uid, session):
    url = f"https://www.pixiv.net/ajax/user/{uid}/profile/all?lang=zh"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        while 1:
            try:
                async with session.get(url, headers=headers, cookies=cookies, proxy=proxy, ssl=False) as response:
                    json_data = await response.json()
                    img_id_list = list(json_data["body"]["illusts"].keys())
                break
            except Exception as e:
                Error("请求作者作品页发生错误" + str(e))
                continue
    tasks = []
    concurrent = 20
    semaphore = asyncio.Semaphore(concurrent)

    for item in img_id_list:
        tasks.append(work(semaphore, item))
    await asyncio.gather(*tasks)

    Log("----------------------重新请求失败队列-------------------------")
    global count
    while failed_list:
        item = failed_list.pop(0)
        if item['lives'] > 0:
            await reload(session, url=item['url'],lives=item['lives']-1, info=item['info'])
            Error("正在重新请求 : 剩余"+str(item['lives'] - 1)+"次")

    Log("成功写入文件: "+str(count)+" 个")


async def work(semaphore, uid):
    global failed_list
    async with semaphore:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            while 1:
                try:
                    async with session.get(f"https://www.pixiv.net/ajax/illust/{uid}/pages?lang=zh", headers=headers,
                                           cookies=cookies, proxy=proxy, ssl=False) as response:
                        target = (await response.json())['body']
                except Exception as e:
                    Error(f"网络错误: 请求作品详情失败: 作品id: {uid}, 错误信息: {e}")
                    continue

                info = {}
                try:
                    async with session.get(f"https://www.pixiv.net/ajax/illust/{uid}", headers=headers,
                                           cookies=cookies, proxy=proxy, ssl=False) as response:
                        json_data = await response.json()
                        if json_data['body']['illustTitle'] is not None : info['title'] = json_data['body']['illustTitle']
                        else : info['title'] = '无题'
                        try:
                            info['datetime'] = json_data['body']['uploadDate']
                            info['likeCount'] = json_data['body']['likeCount']
                            info['viewCount'] = json_data['body']['viewCount']

                            info['author_id'] = json_data['body']['userId']
                            info['source'] = 'Pixiv'
                            info['tags'] = []
                            for item in json_data['body']['tags']['tags']:
                                info['tags'].append(item['translation']['en'])


                            for item in json_data['body']['tags']['tags']:
                                info['tags'].append(item['translation']['en'])
                        except Exception:
                            pass
                except Exception as e:
                    Error(f"网络错误: 请求作品详情页失败: 作品id: {uid}, 错误信息: {e}")
                    continue

                for original_url in target:
                    url = original_url['urls']['original']
                    success = await fetch_single_image(session, url, info)

                    if not success:
                        failed_list.append({'url': url, 'lives': 5, 'info': info})
                        continue
                break


async def fetch_single_image(session, url, info):
    global count
    tmp = await Image.filter(url=url).first()
    if tmp :
        Log("Skipping: " + url)
        return True

    try:
        async with session.get(url, headers=headers, proxy=proxy, cookies=cookies, ssl=False) as response:
            data = await response.read()
    except Exception as e:
        Error("图片请求异常" + str(e))

    name = str(uuid.uuid4()) + url[-4:]
    path = "../storage/img/" + name
    if info['title'] is None or info['title'] == "":
        info['title'] = '无题'
    info['id'] = name
    info['location'] = path
    info['url'] = url

    try:
        with open(path, 'wb') as f:
            f.write(data)
            count += 1
            Log("写入成功: " + url)
    except Exception as e:
        Error("文件写入异常: " + str(e))
        return False

    try:
        with PIL.Image.open(path) as img:
            info['width'] = img.size[0]
            info['height'] = img.size[1]
    except Exception as e:
        Error("文件损坏: 正在重新下载" + str(e))
        return False

    if os.path.exists(path):
        try:
            image = await Image.create(id=info['id'], location=info['location'], width=info['width'], height=info['height'], has_compressed=False, url=info['url'], title=info['title'], likeCount=info['likeCount'], viewCount=info['viewCount'], datetime=info['datetime'], source=info['source'], author_id=info['author_id'])
            for tag_name in info['tags']:
                try:
                    tag_instance, created = await Tag.get_or_create(name=tag_name)
                except Exception as e:
                    Error("数据库写入异常: " + str(e))
                    return False
                await image.tags.add(tag_instance)

        except Exception as e:
            Error("数据库写入异常: " + str(e))
            return False
    else:
        Error("系统内部错误: 正在回滚")
        return False
    return True

async def reload(session, url, lives, info):
    global failed_list
    try:
        await fetch_single_image(session,url, info)
        return
    except Exception as e:
        Error("写入或请求失败:" + str(e))
        failed_list.append({'url': url, 'lives': lives, 'info': info})
        return False