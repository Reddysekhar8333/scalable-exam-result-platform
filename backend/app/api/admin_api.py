from fastapi import (APIRouter, UploadFile, File, Depends)
from sqlalchemy.orm import Session

# Database session dependency
from app.db.database import get_db
# Result table model
from app.models.result import Result
# CSV reader service
from app.services.csv_service import read_csv


# --------------------------------------------------
# Create router for all admin-related endpoints
# --------------------------------------------------
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# --------------------------------------------------
# Upload Result CSV Endpoint
# Exam board uploads a CSV file containing thousands of student results.
# --------------------------------------------------
@router.post("/upload-results")
async def upload_results(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # ----------------------------------------------
    # Read uploaded CSV into Pandas DataFrame
    # ----------------------------------------------
    df = read_csv(file.file)

    # ----------------------------------------------
    # Required columns validation
    # If exam board uploads wrong CSV structure, reject immediately.
    # ----------------------------------------------
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

    # ----------------------------------------------
    # Check duplicate hall tickets inside CSV
    # We should reject before DB insertion.
    # ----------------------------------------------
    duplicate_rows = df[
        df.duplicated(
            subset=["hall_ticket"]
        )
    ]
    if not duplicate_rows.empty:
        return {
            "status": "failed",
            "message": "Duplicate hall tickets found inside CSV",
            "duplicates": duplicate_rows[
                "hall_ticket"
            ].tolist()
        }

    # ----------------------------------------------
    # These help us generate upload report for the exam board.
    # ----------------------------------------------
    inserted = 0
    duplicates = 0
    errors = []

    # ----------------------------------------------
    # Process each row
    # ----------------------------------------------
    for _, row in df.iterrows():
        hall_ticket = str(row["hall_ticket"]).strip()
        student_name = str(row["student_name"]).strip()
        grade = str(row["grade"]).strip()
        marks = int(row["total_marks"])

        # ------------------------------------------
        # Marks Validation
        # ------------------------------------------
        if marks < 0 or marks > 600:

            errors.append(
                f"{hall_ticket}: Invalid marks"
            )
            continue
        # ------------------------------------------
        # Check whether hall ticket already exists in database.
        # Prevent duplicate student records.
        # ------------------------------------------
        existing_result = (
            db.query(Result)
            .filter(
                Result.hall_ticket
                == hall_ticket
            )
            .first()
        )
        if existing_result:

            duplicates += 1

            errors.append(
                f"{hall_ticket}: Already exists in database"
            )
            continue

        # ------------------------------------------
        # Create Result ORM object
        # ------------------------------------------
        result = Result(
            hall_ticket=hall_ticket,
            student_name=student_name,
            grade=grade,
            total_marks=marks
        )

        # ------------------------------------------
        # Stage for insertion
        # Not inserted immediately.
        # SQLAlchemy keeps it in session.
        # ------------------------------------------
        db.add(result)
        inserted += 1

    # ----------------------------------------------
    # Commit all successful records
    # ----------------------------------------------
    db.commit()

    # ----------------------------------------------
    # Return detailed upload report
    # ----------------------------------------------
    return {
        "status": "success",
        "inserted": inserted,
        "duplicates": duplicates,
        "errors": errors
    }