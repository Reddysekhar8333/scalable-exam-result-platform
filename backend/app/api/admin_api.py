from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.result import Result
from app.services.csv_service import read_csv

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/upload-results")
async def upload_results( file: UploadFile = File(...), db: Session = Depends(get_db) ):
    # ----------------------------------
    # Read CSV
    # ----------------------------------
    df = read_csv(file.file)

    # ----------------------------------
    # Validate Required Columns
    # ----------------------------------
    required_columns = [
        "hall_ticket",
        "student_name",
        "grade",
        "total_marks"
    ]
    for column in required_columns:
        if column not in df.columns:
            return {
                "status": "failed",
                "message": f"Missing column: {column}"
            }

    # ----------------------------------
    # Detect Duplicates Inside CSV
    # ----------------------------------
    csv_duplicates = df[
        df.duplicated(
            subset=["hall_ticket"]
        )
    ]

    if not csv_duplicates.empty:
        return {
            "status": "failed",
            "message": "Duplicate hall tickets found inside CSV",
            "duplicates": csv_duplicates[
                "hall_ticket"
            ].tolist()
        }

    # ----------------------------------
    # Load Existing Hall Tickets  =>  ONE QUERY ONLY
    # ----------------------------------
    existing_hall_tickets = set( row[0] for row in db.query(Result.hall_ticket).all() )

    # ----------------------------------
    # Statistics
    # ----------------------------------
    inserted = 0
    duplicates = 0
    invalid_records = 0

    errors = []

    # ----------------------------------
    # Store Valid Objects Here  =>  Bulk Insert Later
    # ----------------------------------
    results_to_insert = []

    # ----------------------------------
    # Process Rows
    # ----------------------------------
    for _, row in df.iterrows():

        hall_ticket = str(row["hall_ticket"]).strip()
        student_name = str(row["student_name"]).strip()
        grade = str(row["grade"]).strip()

        try:
            marks = int(
                row["total_marks"]
            )
        except Exception:
            invalid_records += 1
            errors.append( f"{hall_ticket}: Invalid marks format" )
            continue

        # ----------------------------------
        # Marks Validation
        # ----------------------------------
        if marks < 0 or marks > 600:
            invalid_records += 1
            errors.append( f"{hall_ticket}: Invalid marks" )
            continue

        # ----------------------------------
        # Duplicate Check
        #
        # O(1) Set Lookup
        # ----------------------------------
        if hall_ticket in existing_hall_tickets:
            duplicates += 1
            errors.append(f"{hall_ticket}: Already exists")
            continue

        # ----------------------------------
        # Prepare Object
        #
        # No DB Insert Yet
        # ----------------------------------
        results_to_insert.append(
            Result(
                hall_ticket=hall_ticket,
                student_name=student_name,
                grade=grade,
                total_marks=marks
            )
        )

        inserted += 1

    # ----------------------------------
    # Bulk Insert
    # ----------------------------------
    if results_to_insert:
        db.bulk_save_objects(
            results_to_insert
        )
        db.commit()

    # ----------------------------------
    # Upload Report
    # ----------------------------------
    return {
        "status": "success",
        "inserted": inserted,
        "duplicates": duplicates,
        "invalid_records": invalid_records,
        "total_processed": len(df),
        "errors": errors
    }