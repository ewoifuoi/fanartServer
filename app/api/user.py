from fastapi import APIRouter, Form, BackgroundTasks
from starlette.responses import FileResponse, JSONResponse
from utils.SendMail import ZMailObject

router = APIRouter()

@router.post("/testMail")
async def testMail(mail_to):
    zmail = ZMailObject()
    zmail.sendMail(mail_to)

    return {"code": 0, "msg": "ok"}