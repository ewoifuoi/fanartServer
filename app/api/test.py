import os
import secrets

import aiohttp
import requests

from fastapi import APIRouter,HTTPException
from starlette.responses import FileResponse

from models.illustration import Illustration
from models.image import Image, Author, Author_User
from models.user import User
from utils.Log import Log, Error
from utils.auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()

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



@router.get("/get_avatar", description="获取指定昵称用户的头像")
async def get_avatar(name):
    user = await User.get_or_none(Name=name)
    if user is None:
        raise HTTPException(status_code=404,detail="用户不存在")
    return FileResponse(user.Avatar)


@router.get("/get_tags", description="获取标签")
async def get_tags():
    return

@router.delete("/check", description="检查文件系统是否完整")
async def check():
    file_count = 0;error_count = 0;delete_count = 0
    images = await Image.all()
    for image in images:
        if os.path.exists(image.location):
            Log(f"检测到文件: {image.id}")
        else:
            Error(f"检测到文件缺失:{image.id}")
    files = []
    for root , dirs,filenames in os.walk("../storage/img"):
        for filename in filenames:
            files.append(os.path.join(root, filename))

    for file in files:
        image = await Image.get_or_none(location=file)
        if image is None:
            error_count += 1
            Error(f"检测到非法文件: {file}")
            try:
                os.remove(file)
                delete_count += 1
                Log(f"正在删除文件:{file}")
            except Exception as e:
                Error(str(e))
        else:
            Log(f"检测到文件: {file}")
    files2 = []
    for root , dirs,filenames in os.walk("../storage/img_compressed"):
        for filename in filenames:
            files2.append(filename)

    for file in files2:
        image = await Image.get_or_none(id=file)
        if image is None or image.has_compressed==False:
            error_count += 1
            Error(f"检测到非法压缩文件: {file}")
            try:
                os.remove(f"../storage/img_compressed/{file}")
                delete_count += 1
                Log(f"正在删除文件:../storage/img_compressed/{file}")
            except Exception as e:
                Error(str(e))
        # Log(image.url)
    return {"msg":"服务器文件系统检查完成",
            "已检测图片文件总数": len(files)+len(files2),
            "非法图片文件数": error_count,
            "已清除图片文件数": delete_count}

@router.patch("/migrate/illustrations")
async def migrate_illustrations():
    images = await Image.all()
    for image in images:
        userID = await Author_User.filter(AuthorId=image.author).values('UserId')
        info = {
            'IllustrationID': image.id,
            'Title': image.title,
            'Description': '',
            'Location':image.location,
            'Height': image.height,
            'Width': image.width,
            'FileSize':'',
            'FileType':image.location,
            'LikeCount':likecount,
            'ViewCount':viewcount,
            'UserID': userID
        }
        await Illustration.create(**info)
        Log(f'成功迁移作品:{image.title}')

    return "迁移作品成功"

@router.patch("/migrate/users",description="用户迁移")
async def migrate_users():
    authors = await Author.all()
    for author in authors:
        Log(f"正在迁移画师:{author.uid}")
        try:
            await updateUser(author.uid)
        except Exception as e:
            Error(str(e))

    return "迁移用户成功"


async def updateUser(uid):
    author = await Author.get_or_none(uid=uid)
    user_temp = await Author_User.get_or_none(Author=author)
    if user_temp is not None:
        Log(f"Skipping 画师:{uid}")
        return

    cookies={}
    cookie_raw = "first_visit_datetime_pc=2024-01-20%2012%3A13%3A56; p_ab_id=5; p_ab_id_2=5; p_ab_d_id=159194759; yuid_b=ORNFVGA; __utmz=235335808.1705720468.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); privacy_policy_notification=0; a_type=0; privacy_policy_agreement=6; _im_vid=01HMJE3CFRM9JFN8QW164B2QGJ; login_ever=yes; cto_bundle=DFAPNl9IdTRVMEtRYWZkUTVONVZXamhlMElJNFQzbGJSTjRYcW5lcUw1byUyRktWQWVFYjFVViUyQjNvdzNKRGN4TFNWTDR4RG42OCUyQmNHOVN3VHQxRkd4NTdPNmhYTDFaQVR2Wk1IcXJXbGZBandUMm10b2h5MHhtdkdLb01jZTlPOUZBdGlSOGF5d0EzcmpsbTZmbkx6VkVTYyUyQmg4QSUzRCUzRA; cto_bidid=R13TiF9BM0tIdGFkaTJaaXVIWjhPJTJGakJVYVhOVGZQdDNoWG4lMkZmM2R0eWIxaURxJTJGUVpWOUE0OG9XRmxuaWRySmR2OTlLMFlSYnVQRU82empwZ1dLNE1VTzRZeHRneTFWN2wyQ0JuMTBnRUVOUXFZMCUzRA; _im_vid=01HMJE3CFRM9JFN8QW164B2QGJ; _im_uid.3929=i.rAX3czQIQDa_ySjpvevMKA; FCNEC=%5B%5B%22AKsRol-0aXCOebiYDcAJDKF3sy0FNGOXlUZZMiUedT7hnMpvY0TYdwmPz0I6-NQr5jNHdxj7vsSl0rG_7UQGFOSNlqQNFjW9b1GRbegIDUlFgFzsb4EpSYhw9vhaXV_ATwfH49slywotVmanUu4pwPSUP1TaE84iBQ%3D%3D%22%5D%5D; _gcl_au=1.1.1552814137.1713944632; cf_clearance=TlVF6Im3eJxLjd1iaPRltAQvpsaIZcT53VmlpMajog0-1715142914-1.0.1.1-i9C6QJS.9g.7veT4BmJgFj39JAzbBoYNoY6HxIVVzCIumKz2kAhC7wdqccazGbgvg3XICi6MgAbynh.fyiNYDw; device_token=4cc2d6e926c0007437ff863cbb31f246; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; _gid=GA1.2.756179219.1716530812; __cf_bm=2MkdKAL0A57wqhpVB9MACRUNU_L1OWV8YbyPCibZIfQ-1716622370-1.0.1.1-y26hM15xhZ4rNDN24i8CEFJA2rT87XQkpPCqd9DVAn0lP6Bowum1sQAJqACpWHdXOOHVUhQom6g_y_XTjQPpIdQ6itjYF4MC1t8Dm2mnn40; __utma=235335808.1136182024.1705720468.1716571507.1716622372.53; __utmc=235335808; cf_clearance=E47h3tpGighAUMSRXrhE0WPOn_Bsd_pAkzuM7LiuY5o-1716622372-1.0.1.1-ViP9YOQbxbY1TTLaewbE8f_eGO8k8ClRTZlpAjV1Z_eTDP85jIiu350G9rmGWj_0atyrWclthTXt1biffpukWw; __utmt=1; cc1=2024-05-25%2016%3A47%3A28; _gat_UA-1830249-3=1; PHPSESSID=106144205_YYrQnkH3cQdXTnhBysDszbE4jChw6GES; c_type=23; b_type=1; _ga_MZ1NL4PHH0=GS1.1.1716623254.11.1.1716623274.0.0.0; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=106144205=1^9=p_ab_id=5=1^10=p_ab_id_2=5=1^11=lang=zh=1; __utmb=235335808.22.10.1716622372; _ga_75BBYNYN9J=GS1.1.1716622374.67.1.1716623277.0.0.0; _ga=GA1.2.1136182024.1705720468"
    cookie_list = cookie_raw.split('; ')
    for item in cookie_list:
        key_value_pair = item.split('=')
        key = key_value_pair[0]
        value = '='.join(key_value_pair[1:])
        cookies[key] = value
    proxy = 'http://127.0.0.1:7890'
    url = f"https://www.pixiv.net/ajax/user/{uid}?full=1"
    avatar_link = ''
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url, headers=headers,cookies=cookies,proxy=proxy, ssl=False) as response:
            json_data = await response.json()
            avatar_link = json_data['body']['imageBig']
            Log(f"获得画师头像链接: {avatar_link}")
    userID = secrets.token_urlsafe()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(avatar_link, headers=headers,cookies=cookies,proxy=proxy, ssl=False) as response:
            data = await response.read()
            path = "../storage/avatar/" + userID +avatar_link[-4:]
            try:
                with open(path, 'wb') as f:
                    f.write(data)
                    Log("图像文件写入成功")
            except Exception as e:
                Error(f"文件写入异常:{str(e)}")
    pwd = "e9cee71ab932fde863338d08be4de9dfe39ea049bdafb342ce659ec5450b69ae"
    author = await Author.get_or_none(uid=uid)
    user_info = {
        "UserID":userID,
        "Password":auth_handler.get_password_hash(pwd),
        "Avatar":path,
        "Name":author.name,
        "Email": f"{author.uid}@pixiv.com"
    }
    try:
        user = await User.create(**user_info)
        await Author_User.create(Author=author, User=user)
        Log(f"画师迁移成功:{author.name}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
