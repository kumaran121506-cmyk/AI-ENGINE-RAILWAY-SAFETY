"""
WebSocket Endpoint & Connection Manager:
Broadcasts live train telemetry, collision prediction results, signal checks, and braking events.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import logging

logger = logging.getLogger("websocket_manager")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        data_str = json.dumps(message, default=str)
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_text(data_str)
            except Exception:
                disconnected_clients.append(connection)

        for client in disconnected_clients:
            self.disconnect(client)

manager = ConnectionManager()
ws_router = APIRouter()

@ws_router.websocket("/ws/live-monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep-alive or handle incoming control messages from web client
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({"status": "ACK", "echo": data}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
