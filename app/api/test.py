
from fastapi import APIRouter,HTTPException
from starlette.responses import FileResponse
from models.user import User

router = APIRouter()

@router.get("/get_avatar", description="获取指定昵称用户的头像")
async def get_avatar(name):
    user = await User.get_or_none(Name=name)
    if user is None:
        raise HTTPException(status_code=404,detail="用户不存在")
    return FileResponse(user.Avatar)