import uvicorn
from fastapi import FastAPI, Request
from tortoise.contrib.fastapi import register_tortoise

from api import image, user
from services.service import scheduler
from settings import TORTOISE_ORM


app = FastAPI()

register_tortoise(
    app=app,
    config=TORTOISE_ORM
)
app.include_router(user.router, prefix="/user", tags=["用户系统"])
app.include_router(image.router, prefix="/image", tags=["图片爬虫部分"])


scheduler.start()

@app.middleware('http')
async def CORSMiddleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/")
def test():
    return "Hello World!"
