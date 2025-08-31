from fastapi import APIRouter
from app.service.greet_service import get_greeting

router = APIRouter()

@router.get("/hello")
def say_hello():
    return {"message": get_greeting()}