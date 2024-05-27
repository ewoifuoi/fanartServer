import math

from fastapi import APIRouter, HTTPException

from models.illustration import Illustration
from models.user import User

router = APIRouter()


@router.get("/works/{uid}", description="获取用户作品")
async def get_works(uid):
    user = await User.get_or_none(UserID=uid)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    works = await Illustration.filter(UserID=user)
    res = []
    for work in works:
        height = int(work.Height); width = int(work.Width)
        res.append(f"http://124.221.8.18:8080/image/{work.IllustrationID}")
    return res