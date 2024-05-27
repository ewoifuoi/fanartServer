import datetime
import secrets

from fastapi import APIRouter, Response, Request, HTTPException
from pydantic import BaseModel
from starlette.responses import FileResponse
from starlette.templating import Jinja2Templates

from models.illustration import Illustration
from models.user import RegistrationRequest, User, Relationship
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






