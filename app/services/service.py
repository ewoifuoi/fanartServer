import asyncio
from datetime import datetime

import PIL.Image
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import BackgroundTasks
from tortoise import Tortoise

from models.image import Image
from settings import TORTOISE_ORM
from utils.Log import Log, Error


scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=5, next_run_time=datetime.now())
async def service_check_compressed():
    files = await Image.filter(has_compressed=False)
    if not files:
        Log("所有图片文件已压缩")
        return

    tasks = []
    concurrent = 20
    semaphore = asyncio.Semaphore(concurrent)

    for file in files:
        tasks.append(check_compressed(file, semaphore))
    await asyncio.gather(*tasks)

    Log("所有图片文件已压缩")


async def check_compressed(file, semaphore):
    await semaphore.acquire()
    await Tortoise.init(config=TORTOISE_ORM)
    path = "../storage/img_compressed/"
    try:
        with PIL.Image.open(file.location) as img:
            new_width = 600
            new_height = round(600.0 * float(file.height) / float(file.width))
            resized_img = img.resize((new_width, new_height))
            resized_img.save(path + file.id, quality=100)
        file.has_compressed = True
        await file.save()
        Log(file.id + ": 压缩成功")
    except Exception as e:
        Error(file.id + " 文件压缩出错: " + str(e))
        return
    finally:
        await Tortoise.close_connections()
        semaphore.release()
        return