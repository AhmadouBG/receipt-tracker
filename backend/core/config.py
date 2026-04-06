
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession



# Define the async engine using the aiosqlite dialect
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)