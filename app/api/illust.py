from fastapi import APIRouter, Response, Request, HTTPException

from models.illustration import Illustration
from models.notice import Notice
from models.user import RegistrationRequest, User, Relationship
from utils.auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()


@router.get("/author/{illust_id}")
async def get_author_info(request: Request, illust_id: str):
    illust = await Illustration.get_or_none(IllustrationID=illust_id)
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")
    author = await illust.UserID
    res = {
        "avatar_url": f"http://124.221.8.18:8080/user/avatar/{author.UserID}",
        "uid": author.UserID,
        "name": author.Name
    }
    return res

@router.get("/info/{illust_id}")
async def get_illust_info(request: Request, illust_id: str):
    illust = await Illustration.get_or_none(IllustrationID=illust_id)
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")
    res = {
        'Title': illust.Title,
        'Description': illust.Description,
        'Height': illust.Height,
        'Width': illust.Width,
        'Filesize' : illust.FileSize,
        'FileType': illust.FileType,
        'Datetime':illust.CreatedAt,
        'LikeCount': illust.LikeCount,
        'ViewCount': illust.ViewCount
    }
    return res
