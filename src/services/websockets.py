from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, deal_id: int):
        await websocket.accept()

        if deal_id not in self.active_connections:
            self.active_connections[deal_id] = []

        self.active_connections[deal_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, deal_id: int):
        if deal_id in self.active_connections:
            self.active_connections[deal_id].remove(websocket)

            if not self.active_connections[deal_id]:
                del self.active_connections[deal_id]

    async def broadcast_to_deal(self, deal_id: int, message: dict):
        if deal_id in self.active_connections:

            for connection in self.active_connections[deal_id]:
                await connection.send_json(message)

manager = ConnectionManager()

