# This is the main entry point of the FastAPI application.
# Equivalent to Spring Boot's @SpringBootApplication class with a main method
from contextlib import asynccontextmanager

from app.db.db import db
from fastapi import FastAPI                     # FastAPI is like Spring Boot - used to build web APIs

from app.config.settings import settings
from app.routes import hello, users                    # Importing our custom routes module (like Controller package)
from app.config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await db.connect()
    try:
        yield
    finally:
        # shutdown
        await db.disconnect()


# Creating the FastAPI app object
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,   # <-- use lifespan instead of on_event
)

# Registering the hello route with the FastAPI app
# This is similar to adding @ComponentScan or @RequestMapping base paths
app.include_router(hello.router)
app.include_router(users.router)

print("📣 Hello router registered!")

@app.get("/health")
async def health():
    return {"status": "ok"}

# To run this app:
# uvicorn app.main:app --reload
# Think of uvicorn as a lightweight ASGI web server (like Tomcat or Jetty)
