# This is the main entry point of the FastAPI application.
# Equivalent to Spring Boot's @SpringBootApplication class with a main method
from app.db.db import db
from fastapi import FastAPI                     # FastAPI is like Spring Boot - used to build web APIs

from app.config.settings import settings
from app.routes import hello, users                    # Importing our custom routes module (like Controller package)
from app.config.settings import settings

# Creating the FastAPI app object
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Registering the hello route with the FastAPI app
# This is similar to adding @ComponentScan or @RequestMapping base paths
app.include_router(hello.router)
app.include_router(users.router)

print("📣 Hello router registered!")

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get("/health")
async def health():
    return {"status": "ok"}

# To run this app:
# uvicorn app.main:app --reload
# Think of uvicorn as a lightweight ASGI web server (like Tomcat or Jetty)
