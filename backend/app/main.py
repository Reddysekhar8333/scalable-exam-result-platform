from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.result import Result
from app.api.result_api import router as result_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scalable Exam Result Platform",
    version="1.0.0"
)

app.include_router(result_router)


@app.get("/")
def home():
    return {
        "message": "Exam Result Platform API Running"
    }