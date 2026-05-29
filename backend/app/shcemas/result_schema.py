from pydantic import BaseModel

class ResultResponse(BaseModel):
    hall_ticket: str
    student_name: str
    grade: str
    total_marks: int

    class Config:
        from_attributes = True