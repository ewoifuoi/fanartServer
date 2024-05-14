from fastapi import APIRouter, Form, BackgroundTasks
from pydantic import BaseModel
from starlette.responses import FileResponse, JSONResponse

from utils.Log import Log
from utils.SendMail import Mail

router = APIRouter()

@router.post("/testMail")
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
@router.post("/register")
async def register(request: RegisterRequest):

    return {"code": 200, "msg": "注册成功"}

