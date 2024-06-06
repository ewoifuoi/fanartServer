import datetime
import os
import secrets
import shutil
import uuid

import PIL.Image
from fastapi import APIRouter, Response, Request, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from starlette.responses import FileResponse
from starlette.templating import Jinja2Templates

from models.illustration import Illustration, Favorite, Like
from models.image import Image
from models.notice import Notice
from models.user import RegistrationRequest, User, Relationship
from services.service import service_check_compressed
from utils.Log import Log, Error
from utils.SendMail import Mail
from utils.auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()

@router.post("/testMail", description="用于测试邮件服务")
async def testMail(mail_to, name, link):
    mail = Mail()
    if mail.SendMail(mail_to, name, link):
        return {"code": 200, "msg": "发送邮件成功"}
    else:
        return {"code": 400, "msg": "发送邮件失败"}

class RegisterRequest(BaseModel):
    email: str
    name: str
    pwd: str

@router.post("/register", description="前端注册接口")
async def register(request: RegisterRequest):
    mail = Mail()
    id = secrets.token_urlsafe()
    link = f"http://124.221.8.18:8080/user/register/{id}"

    isExisted = await User.get_or_none(Email=request.email)
    if isExisted:
        return Response("该邮箱已被占用",status_code=422 )

    if mail.SendMail(request.email, request.name, link):
        try:
            old = await RegistrationRequest.get_or_none(email=request.email)
            if old:
                old.id = id
                old.password = request.pwd
                old.name = request.name
                old.link = link
                await old.save()
            else:
                await RegistrationRequest.create(
                    id=id,
                    email=request.email,
                    password=request.pwd,
                    name=request.name,
                    link=link
                )
        except Exception as e:
            Error(f"操作数据库错误{e}")
            return Response("注册失败",status_code=422 )

        return {"code": 200, "msg": "注册成功"}
    else :
        return Response("注册失败",status_code=422 )

@router.get("/register/{uid}", description="验证邮件链接接口")
async def checkRegister(uid):
    templates = Jinja2Templates(directory="templates")
    # 首先验证邮箱激活链接是否过期
    info = await RegistrationRequest.get_or_none(id=uid)
    if info is None :
        return templates.TemplateResponse("verification_failed1.html", {"request": {"uid": uid}})
    period = (datetime.datetime.now(datetime.timezone.utc) - info.timestamp).total_seconds()
    if  period > 86400: # 该验证链接已过期
        await info.delete()
        return templates.TemplateResponse("verification_failed2.html", {"request": {"uid": uid}})
    else :
        ## 用户注册逻辑
        user_info = {
            "UserID": info.id,
            "Password": auth_handler.get_password_hash(info.password),
            "Name": info.name,
            "Avatar": "../storage/avatar/default_avatar.png",
            "Email": info.email,
        }
        try:
            await User.create(**user_info)
            await info.delete()

        except Exception as e:
            return Response({"msg": str(e)}, status_code=422 )
        return templates.TemplateResponse("verification.html", {"request": {"uid": uid}})

class UserLogin(BaseModel):
    email: str
    pwd: str

@router.post("/login")
async def login(request: Request, user:UserLogin):
    user_db = await User.get_or_none(Email=user.email)
    if not user_db:
        raise HTTPException(status_code=401,detail="用户邮箱不存在")
    if not auth_handler.verify_password(user.pwd, user_db.Password):
        raise HTTPException(status_code=401,detail="邮箱或密码错误")
    token = auth_handler.encode_token(user_db.UserID)
    Log(f'用户登录成功, 签发token: {token}')
    return {'token': token,'username':user_db.Name,'email':user_db.Email, 'uid':user_db.UserID}

@router.get("/refresh")
@auth_handler.jwt_required
async def refresh_token(request: Request):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    user_db = await User.get_or_none(UserID=userId)
    if not user_db:
        raise HTTPException(status_code=404,detail="用户不存在")
    token = auth_handler.encode_token(userId)
    Log(f'获取新token：{token}')
    return {'token': token,'username':user_db.Name,'email':user_db.Email, 'uid':user_db.UserID}

@router.get("/avatar", description="用户获取自己头像")
@auth_handler.jwt_required
async def avatar(request:Request):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    user = await User.get_or_none(UserID=userId)
    if not user:
        raise HTTPException(status_code=404,detail="用户不存在")
    return FileResponse(user.Avatar)

@router.get("/avatar/{uid}",description="获取用户头像")
async def avatar(uid, request:Request):
    user = await User.get_or_none(UserID=uid)
    if not user:
        raise HTTPException(status_code=404,detail="用户不存在")
    return FileResponse(user.Avatar)

@router.get("/profile/{uid}", description="获取用户主页信息")
async def profile(uid,request:Request):
    user = await User.get_or_none(UserID=uid)
    if not user:
        raise HTTPException(status_code=404,detail="用户不存在")
    username = user.Name
    email = user.Email
    illuts = await Illustration.filter(UserID=user)
    likecount = 0;followers = 0;following = 0;workscount = 0
    for illut in illuts:
        likecount += illut.LikeCount
    followings = await Relationship.filter(UserID=user).count()
    followers = await Relationship.filter(FollowedUserID=user).count()
    workscount = await Illustration.filter(UserID=user).count()
    return {
        "username":username,
        "email":email,
        "workscount":workscount,
        "followerscount":followers,
        "followingcount":followings,
        "likecount": likecount
    }

@router.get("/hasWatched/{uid}", description="查询是否已关注")
@auth_handler.jwt_required
async def hasWatched(request:Request,uid):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)

    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    userB = await User.get_or_none(UserID=uid)
    if not userB:
        raise HTTPException(status_code=404, detail="用户不存在")

    relations = await Relationship.filter(UserID=userA,FollowedUserID=userB).count()
    print(relations)
    if relations > 0:
        return True
    else:
        return False

@router.get("/follow/{uid}", description="关注用户")
@auth_handler.jwt_required
async def follow(request:Request,uid):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    userB = await User.get_or_none(UserID=uid)
    if not userB:
        raise HTTPException(status_code=404, detail="用户不存在")
    try:
        await Relationship.create(UserID=userA,FollowedUserID=userB)
    except Exception as e:
        Error(f"关注用户失败{str(e)}")
    try:
        await Notice.create(UserID=userB, content=f"用户 {userA.Name} 关注了你")
    except Exception as e:
        Error(str(e))


@router.get("/unfollow/{uid}", description="关注用户")
@auth_handler.jwt_required
async def unfollow(request:Request,uid):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    userB = await User.get_or_none(UserID=uid)
    if not userB:
        raise HTTPException(status_code=404, detail="用户不存在")

    relation = await Relationship.filter(UserID=userA, FollowedUserID=userB).first()

    if relation is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    try:
        await relation.delete()
        return Response(status_code=200)
    except Exception as e:
        Error(f"取消关注失败{str(e)}")
        raise HTTPException(status_code=502, detail="取消关注失败")

@router.get("/followings/{uid}", description="获得关注列表")
async def followings(request:Request,uid):
    rf = await Relationship.filter(UserID_id=uid)
    res = []
    for following in rf:
        user = await User.get_or_none(UserID=following.FollowedUserID_id)
        if user is None:
            continue
        temp = {
            "uid": user.UserID,
            "name":user.Name,
            "email":user.Email,
            "avatar":f"http://124.221.8.18:8080/user/avatar/{user.UserID}"
        }
        res.append(temp)
    return res

@router.get("/followers/{uid}", description="获得粉丝列表")
async def followers(request:Request,uid):
    rf = await Relationship.filter(FollowedUserID_id=uid)
    res = []
    for follower in rf:
        user = await User.get_or_none(UserID=follower.UserID_id)
        if user is None:
            continue
        temp = {
            "uid": user.UserID,
            "name":user.Name,
            "email":user.Email,
            "avatar":f"http://124.221.8.18:8080/user/avatar/{user.UserID}"
        }
        res.append(temp)
    return res

@router.get("/favorite/{illustid}", description="收藏插画")
@auth_handler.jwt_required
async def favorite(request:Request, illustid:str):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    illust = await Illustration.filter(IllustrationID=illustid).first()
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")

    try:
        await Favorite.create(UserID=userA, IllustrationId=illust)
    except Exception as e:
        Error(str(e))

    try:
        await Notice.create(UserID=illust.UserID, content=f"用户 {illust.UserID.Name} 收藏了你的作品 {illust.Title}", type=1)
    except Exception as e:
        Error(str(e))
    return Response(status_code=200)

@router.get("/unfavorite/{illustid}", description="取消收藏插画")
@auth_handler.jwt_required
async def unfavorite(request:Request, illustid:str):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    illust = await Illustration.filter(IllustrationID=illustid).first()
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")

    try:
        f = await Favorite.filter(UserID=userA, IllustrationId=illust).first()
        await f.delete()
    except Exception as e:
        Error(str(e))
    return Response(status_code=200)

@router.get("/check_favorite/{illustid}", description="检查是否已收藏插画")
@auth_handler.jwt_required
async def check_favorite(request:Request, illustid:str):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    illust = await Illustration.filter(IllustrationID=illustid).first()
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")

    f = await Favorite.filter(UserID=userA, IllustrationId=illust).first()
    if f is not None:
        return True
    else:
        return False

@router.get("/like/{illustid}", description="点赞插画")
@auth_handler.jwt_required
async def like(request:Request, illustid:str):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    illust = await Illustration.filter(IllustrationID=illustid).first()
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")

    try:
        await Like.create(UserID=userA, IllustrationId=illust)
    except Exception as e:
        Error(str(e))

    try:
        await Notice.create(UserID=illust.UserID, content=f"用户 {illust.UserID.Name} 赞了你的作品 {illust.Title}", type=1)
    except Exception as e:
        Error(str(e))
    return Response(status_code=200)

@router.get("/unlike/{illustid}", description="取消点赞插画")
@auth_handler.jwt_required
async def unlike(request:Request, illustid:str):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    illust = await Illustration.filter(IllustrationID=illustid).first()
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")

    try:
        f = await Like.filter(UserID=userA, IllustrationId=illust).first()
        await f.delete()
    except Exception as e:
        Error(str(e))
    return Response(status_code=200)

@router.get("/check_like/{illustid}", description="检查是否已点赞插画")
@auth_handler.jwt_required
async def check_like(request:Request, illustid:str):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    illust = await Illustration.filter(IllustrationID=illustid).first()
    if illust is None:
        raise HTTPException(status_code=404, detail="插画不存在")

    f = await Like.filter(UserID=userA, IllustrationId=illust).first()
    if f is not None:
        return True
    else:
        return False

@router.post("/upload", description="上传作品")
@auth_handler.jwt_required
async def upload(request:Request, file:UploadFile = File(...), title: str = Form(...), description: str = Form(), height: str = Form(...), width: str = Form(),filetype:str=Form(...), filesize: str =Form(...)):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")

    info = {}
    name = str(uuid.uuid4()) + '.' + filetype
    path1 = "../storage/img/" + name
    path2 = "../storage/img_compressed/" + name
    if title is None or title == "":
        info['Title'] = '无题'
    else:
        info['Title'] = title
    info['IllustrationID'] = name
    info['Location'] = path1
    info['Description'] = description
    info['Height'] = height
    info['Width'] = width
    info['FileSize'] = filesize
    info['FileType'] = filetype

    try:
        with open(path1, 'wb') as f:
            shutil.copyfileobj(file.file, f)
            Log("写入成功: " + path1)
        file.file.seek(0)
        with open(path2, 'wb') as ff:
            shutil.copyfileobj(file.file, ff)
            Log("写入成功: " + path2)
    except Exception as e:
        Error("文件写入异常: " + str(e))
        raise HTTPException(status_code=503, detail=str(e))

    try:
        with PIL.Image.open(path1) as img:
            Log('文件完整')
    except Exception as e:
        Error("文件损坏: 正在重新下载" + str(e))
        return False

    try:
        illust = await Illustration.create(
            IllustrationID=info['IllustrationID'],
            Title=info['Title'],
            Description=info['Description'],
            Location=info['Location'],
            Height=info['Height'],
            Width=info['Width'],
            FileSize=info['FileSize'],
            FileType=info['FileType'],
            UserID=userA
        )

    except Exception as e:
        Error("数据库写入异常: " + str(e))
        raise HTTPException(status_code=503, detail=str(e))


    return Response(status_code=200)