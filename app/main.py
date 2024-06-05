import uvicorn
from fastapi import FastAPI, Request, Response
from tortoise.contrib.fastapi import register_tortoise

from api import image, user, test, search, notice
from services.service import scheduler
from settings import TORTOISE_ORM


app = FastAPI()

register_tortoise(
    app=app,
    config=TORTOISE_ORM
)
app.include_router(test.router,prefix="/test", tags=["系统测试"])
app.include_router(search.router, prefix="/search", tags=["检索部分"])
app.include_router(user.router, prefix="/user", tags=["用户系统"])
app.include_router(image.router, prefix="/image", tags=["图片爬虫部分"])
app.include_router(notice.router, prefix="/notice", tags=["通知系统"])

scheduler.start()

@app.middleware('http')
async def CORSMiddleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

@app.get("/")
def test():
    return "Hello World!"
