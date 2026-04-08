
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


DB_NAME = "receipts.db"
OLLAMA_HOST = "http://localhost:11434"     
OLLAMA_MODEL = "qwen2.5vl:3b" 
