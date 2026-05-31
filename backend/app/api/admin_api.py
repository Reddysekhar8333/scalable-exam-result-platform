from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.result import Result
from app.services.csv_service import read_csv

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/upload-results")
async def upload_results(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    df = read_csv(file.file)

    inserted = 0

    for _, row in df.iterrows():

        result = Result(
            hall_ticket=row["hall_ticket"],
            student_name=row["student_name"],
            grade=row["grade"],
            total_marks=row["total_marks"]
        )

        db.add(result)
        inserted += 1

    db.commit()

    return {
        "message": "Results uploaded successfully",
        "records_inserted": inserted
    }