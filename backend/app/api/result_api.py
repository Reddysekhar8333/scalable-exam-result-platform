from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.result import Result

import json
from app.cache.redis_client import redis_client

router = APIRouter(
    tags=["Results"]
)

@router.get("/results/{hall_ticket}")
def get_result( hall_ticket: str, db: Session = Depends(get_db) ):

    cache_key = f"result:{hall_ticket}"

    # Step 1: Check Redis (if student's result is cached)
    cached_result = redis_client.get(
        cache_key
    )
    if cached_result:
        return {
            "source": "redis",
            "data": json.loads(
                cached_result
            )
        }

    # Step 2: Query Database (if student's result is not in Redis)
    result = (
        db.query(Result)
        .filter(Result.hall_ticket == hall_ticket)
        .first()
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )
    response = {
        "hall_ticket": result.hall_ticket,
        "student_name": result.student_name,
        "grade": result.grade,
        "total_marks": result.total_marks
    }

    # Step 3: Save in Redis for 1 hour
    redis_client.setex(
        cache_key,
        3600, # Cache for 1 hour (3600 seconds)
        json.dumps(response)
    )

    return {
        "source": "mysql",
        "data": response
    }