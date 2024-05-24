import os

from fastapi import APIRouter,HTTPException
from starlette.responses import FileResponse

from models.image import Image
from models.user import User
from utils.Log import Log, Error

router = APIRouter()

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
            pass
            # Log(f"检测到文件: {image.id}")
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
            # Log(f"检测到文件: {file}")
            pass
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