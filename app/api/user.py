from fastapi import APIRouter, Form, BackgroundTasks
from starlette.responses import FileResponse, JSONResponse
from utils.SendMail import Mail

router = APIRouter()

@router.post("/testMail")
async def testMail(mail_to, name, link):
    mail = Mail()
    if mail.SendMail(mail_to, name, link):
        return {"code": 200, "msg": "发送邮件成功"}
    else:
        return {"code": 400, "msg": "发送邮件失败"}