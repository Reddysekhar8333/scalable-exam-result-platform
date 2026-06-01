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
from app.cache.redis_client import redis_client


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/upload-results")
async def upload_results(file: UploadFile = File(...),db: Session = Depends(get_db)):
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
    # Check Duplicate Hall Tickets
    # Inside CSV
    # ----------------------------------
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

    # ----------------------------------
    # Extract Hall Tickets From CSV
    # ----------------------------------
    csv_hall_tickets = (
        df["hall_ticket"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    # ----------------------------------
    # Query ONLY Relevant Records
    # ----------------------------------
    existing_records = (
        db.query(Result)
        .filter(
            Result.hall_ticket.in_(
                csv_hall_tickets
            )
        )
        .all()
    )

    # ----------------------------------
    # Convert Existing Records
    # To Dictionary
    # ----------------------------------
    existing_map = {record.hall_ticket: record for record in existing_records}

    # ----------------------------------
    # Statistics
    # ----------------------------------
    inserted = 0
    updated = 0
    invalid_records = 0

    errors = []

    # ----------------------------------
    # Store New Records For Bulk Insert
    # ----------------------------------
    new_records = []

    # ----------------------------------
    # Store Updates For Bulk Update
    # ----------------------------------
    update_mappings = []

    # ----------------------------------
    # Process CSV
    # ----------------------------------
    for _, row in df.iterrows():
        hall_ticket = str(row["hall_ticket"]).strip()
        student_name = str(row["student_name"]).strip()
        grade = str(row["grade"]).strip()
        try:
            total_marks = int(row["total_marks"])
        except Exception:
            invalid_records += 1
            errors.append(f"{hall_ticket}: Invalid marks format")
            continue
        # ----------------------------------
        # Marks Validation
        # ----------------------------------
        if total_marks < 0 or total_marks > 600:
            invalid_records += 1
            errors.append(f"{hall_ticket}: Invalid marks")
            continue
        # ----------------------------------
        # Existing Record UPDATE
        # ----------------------------------
        if hall_ticket in existing_map:
            update_mappings.append({
                "id": existing_map[hall_ticket].id,
                "student_name": student_name,
                "grade": grade,
                "total_marks": total_marks
            })
            # Cache Invalidation
            redis_client.delete(f"result:{hall_ticket}")
            updated += 1
        # ----------------------------------
        # New Record INSERT
        # ----------------------------------
        else:
            new_records.append(
                Result(
                    hall_ticket=hall_ticket,
                    student_name=student_name,
                    grade=grade,
                    total_marks=total_marks
                )
            )
            inserted += 1

    # ----------------------------------
    # Bulk Insert
    # ----------------------------------
    if new_records:
        db.bulk_save_objects(new_records)

    # ----------------------------------
    # Bulk Update
    # ----------------------------------
    if update_mappings:
        db.bulk_update_mappings(Result, update_mappings)

    # ----------------------------------
    # Commit Everything
    # ----------------------------------
    db.commit()

    # ----------------------------------
    # Final Report
    # ----------------------------------
    return {
        "status": "success",
        "inserted": inserted,
        "updated": updated,
        "invalid_records": invalid_records,
        "total_processed": len(df),
        "errors": errors
    }