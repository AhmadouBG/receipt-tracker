from fastapi import WebSocket
from typing import List
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_event(self, event_type: str, data: dict):
        message = {"type": event_type, "data": data}
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    async def emit_receipt_parsed(self, receipt_data: dict):
        await self.send_event("receipt_parsed", receipt_data)

    async def emit_receipt_failed(self, receipt_id: str, error: str):
        await self.send_event("receipt_failed", {"receipt_id": receipt_id, "error": error})


manager = ConnectionManager()
