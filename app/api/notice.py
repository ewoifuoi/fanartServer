from fastapi import APIRouter, Response, Request, HTTPException

from models.notice import Notice
from models.user import RegistrationRequest, User, Relationship

from utils.auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()

@router.get("/user")
@auth_handler.jwt_required
async def getUserNotices(request:Request):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    notices = await Notice.filter(UserID=userId, type=0)
    res = []
    for notice in notices:
        temp = {
            "content": notice.content,
            "date": notice.CreatedAt
        }
        res.append(temp)
    return res

@router.get("/illustration")
@auth_handler.jwt_required
async def getIllustrationNotices(request:Request):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    notices = await Notice.filter(UserID=userId, type=1)
    res = []
    for notice in notices:
        temp = {
            "content": notice.content,
            "date": notice.CreatedAt
        }
        res.append(temp)
    return res

@router.get("/hasNew")
@auth_handler.jwt_required
async def hasNewNotices(request:Request):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    notices = await Notice.filter(UserID=userId, isReaded=0).count()
    if notices > 0:
        return True
    else:
        return False
