from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from .api.receipts import router as receipts_router
from .core.websocket import manager

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React
    # dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

app.include_router(receipts_router, prefix="/api")