import asyncpg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.db import db
from app.kafka.kafka_producer import publish_user_created

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

@router.post("/users")
async def create_user(user: UserCreate):
    query = "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id"
    async with db.pool.acquire() as conn:
        try:
            user_id = (await conn.fetchval(query, user.name, user.email))
            publish_user_created(user_id, user.name, user.email)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return {"id": user_id, "name": user.name, "email": user.email}

@router.get("/users")
async def list_users():
    query = "SELECT id, name, email FROM users"
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query)
    return [dict(row) for row in rows]

