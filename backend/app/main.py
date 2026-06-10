from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.result import Result
from app.api.result_api import router as result_router
from app.api.admin_api import router as admin_router

from app.cache.redis_client import redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scalable Exam Result Platform",
    version="1.0.0"
)

app.include_router(result_router)
app.include_router(admin_router)

@app.get("/")
def home():
    return {
        "message": "Exam Result Platform API Running"
    }


# --------------------------------------
# Redis Cache Test Endpoint
# --------------------------------------
@app.get("/redis-test")
def redis_test():
    try:
        redis_client.set(
            "test",
            "redis working"
        )
        value = redis_client.get(
            "test"
        )
        return {
            "message": value
        }
    except Exception as e:

        return {
            "error": str(e)
        }

# --------------------------------------
# server info endpoint for load balancing testing
# --------------------------------------
import socket
@app.get("/server-info")
def server_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return {
        "hostname": hostname,
        "ip_address": ip_address
    }