from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.result import Result

router = APIRouter(
    tags=["Results"]
)

@router.get("/results/{hall_ticket}")
def get_result( hall_ticket: str, db: Session = Depends(get_db) ):
    result = (
        db.query(Result)
        .filter(Result.hall_ticket == hall_ticket)
        .first()
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Result not found " \
            " Check the hall ticket number and try again."
        )
    return result