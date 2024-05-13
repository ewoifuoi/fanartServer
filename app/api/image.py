# api/users.py
import random

from fastapi import APIRouter, Form, BackgroundTasks
from starlette.responses import FileResponse, JSONResponse

import utils.pixiv_scraper as scraper
from models.image import Image, Tag
from utils.Log import Log

router = APIRouter()

@router.get("/random/1")
async def get_image():
    count = await Image.all().count()
    if count == 0:
        return {"message":"暂无图片文件"}
    random_index = random.randint(0, count - 1)
    img = await Image.all().offset(random_index).limit(1).first()
    image_path = f"../storage/img/{img.id}"
    return FileResponse(image_path)

@router.get("/random")
async def get_image():
    count = await Image.all().count()
    if count == 0:
        return {"message":"暂无图片文件"}
    random_index = random.randint(0, count - 1)
    img = await Image.all().offset(random_index).limit(1).first()
    image_path = f"../storage/img_compressed/{img.id}"
    return FileResponse(image_path)


@router.get("/{name}")
async def get_image(name: str):
    image_path = f"../storage/img_compressed/{name}"
    return FileResponse(image_path)

@router.post("/fetch_from_pixiv")
async def fetch_all_images_by_author_id(uid:str=Form(), background_tasks:BackgroundTasks=BackgroundTasks()):
    Log("成功接收请求")
    background_tasks.add_task(scraper.fetch_all_images_by_author_id, uid)
    return {"message":"请求成功"}

@router.get("/")
async def get_images_list():
    count = await Image.all().count()
    if count == 0:
        return {"message": "暂无图片文件"}
    res = []
    heights = []
    for i in range(20):
        random_index = random.randint(0, count - 1)
        image = await Image.all().offset(random_index).limit(1).first()
        src = 'http://124.221.8.18:8080/image/' + image.id
        tags = await Tag.filter(images=image)
        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)

        res.append({'src':src, 'tags':tag_names})
        heights.append(image.height)
    return {"image":res}


