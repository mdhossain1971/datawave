import asyncpg
from app.config.settings import settings

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=settings.database_url)
        await self.create_table();

    async def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query)

    async def disconnect(self):
        await self.pool.close()

db=Database()