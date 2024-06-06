from typing import List

from fastapi import FastAPI, Request, WebSocket, APIRouter, WebSocketDisconnect

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