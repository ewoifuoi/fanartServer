import uvicorn
from fastapi import FastAPI, Request
from tortoise.contrib.fastapi import register_tortoise

from api.image import router
from services.service import scheduler
from settings import TORTOISE_ORM


app = FastAPI()

register_tortoise(
    app=app,
    config=TORTOISE_ORM
)
app.include_router(router, prefix="/image", tags=["图片爬虫部分"])

scheduler.start()

@app.middleware('http')
async def CORSMiddleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/")
def test():
    return "Hello World!"
