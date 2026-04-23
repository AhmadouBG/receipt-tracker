from fastapi import WebSocket
from typing import List, Callable, Awaitable
import asyncio
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


UploadTask = dict

upload_queue: asyncio.Queue[UploadTask] = asyncio.Queue()
processing_worker_task: asyncio.Task | None = None


async def process_upload(task: UploadTask, processor: Callable[[UploadTask], Awaitable[UploadTask]]):
    try:
        result = await processor(task)
        if result.get("status") == "parsed":
            await manager.emit_receipt_parsed(result)
        else:
            await manager.emit_receipt_failed(result.get("receipt_id", "unknown"), result.get("error", "Unknown error"))
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        await manager.emit_receipt_failed(task.get("receipt_id", "unknown"), str(e))


async def queue_worker(processor: Callable[[UploadTask], Awaitable[UploadTask]]):
    while True:
        task = await upload_queue.get()
        await process_upload(task, processor)
        upload_queue.task_done()


def start_queue_worker(processor: Callable[[UploadTask], Awaitable[UploadTask]]):
    global processing_worker_task
    processing_worker_task = asyncio.create_task(queue_worker(processor))


async def enqueue_upload(task: UploadTask):
    await upload_queue.put(task)
