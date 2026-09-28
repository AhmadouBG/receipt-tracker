from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from .api.receipts import router as receipts_router
except ImportError:
    from api.receipts import router as receipts_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React
    # dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(receipts_router, prefix="/api")