from typing import List

from fastapi import FastAPI, Request, WebSocket, APIRouter, WebSocketDisconnect, HTTPException
from fastapi.openapi.models import Response

from models.message import Message, MessageList
from models.user import User
from utils.auth import AuthHandler


class ConnectionManager: # 连接管理
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

router = APIRouter()
auth_handler = AuthHandler()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"User: {data}")
    except WebSocketDisconnect as e:
        manager.disconnect(websocket)
        await manager.broadcast(f"A user has left the chat. Code: {e.code}, Reason: {e.reason}")

@router.get("/list", description="获取用户聊天列表")
@auth_handler.jwt_required
async def get_message_list(request: Request):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")
    MessagesA = await MessageList.filter(owner=userA).all()
    MessagesB = await MessageList.filter(to_user=userA).all()
    res = []
    for message in MessagesA:
        user = await message.to_user
        temp = {
            "uid": user.UserID,
            "name":user.Name,
            "avatar":f"http://124.221.8.18:8080/user/avatar/{user.UserID}"
        }
        res.append(temp)

    for message in MessagesB:
        user = await message.owner
        temp = {
            "uid": user.UserID,
            "name":user.Name,
            "avatar":f"http://124.221.8.18:8080/user/avatar/{user.UserID}"
        }
        res.append(temp)
    return res

@router.get("/add/{uid}", description="添加用户聊天列表")
@auth_handler.jwt_required
async def get_message_list(request: Request, uid:str):
    token_old = request.headers.get('Authorization')
    userId = auth_handler.decode_token(token_old)['sub']
    userA = await User.get_or_none(UserID=userId)
    if not userA:
        raise HTTPException(status_code=404, detail="用户不存在")

    to_user = await User.get_or_none(UserID=uid)
    if not to_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    try:
        await MessageList.create(owner=userA, to_user=to_user)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    return Response(status_code=200)

