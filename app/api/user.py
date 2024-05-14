import datetime
import secrets
import uuid

from fastapi import APIRouter, Form, BackgroundTasks
from pydantic import BaseModel
from starlette.responses import FileResponse, JSONResponse

from models.user import RegistrationRequest
from utils.Log import Log, Error
from utils.SendMail import Mail
from models import user

router = APIRouter()

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
            return {"code":400, 'msg':"注册失败"}

        return {"code": 200, "msg": "注册成功"}
    else :
        return {'code': 400, 'msg': "注册失败"}
@router.get("/register/{uid}", description="验证邮件链接接口")
async def checkRegister(uid):

    # 首先验证邮箱激活链接是否过期
    info = await RegistrationRequest.get_or_none(id=uid)
    period = datetime.datetime.now() - info.timestamp



    return {"code": 200, "msg": period}
