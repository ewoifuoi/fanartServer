import datetime
import secrets

from fastapi import APIRouter, Response, Request, HTTPException, Depends
from pydantic import BaseModel
from starlette.templating import Jinja2Templates
from models.user import RegistrationRequest, User
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
    return {'token': token}

@router.get("/refresh")
@auth_handler.jwt_required
async def refresh_token(request: Request):
    token_old = request.headers.get('Authorization')
    token_new = auth_handler.encode_token(auth_handler.decode_token(token_old))
    Log(f'获取新token：{token_new}')
    return {'token':token_new}
