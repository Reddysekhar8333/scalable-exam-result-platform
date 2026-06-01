from sqlalchemy import Column, Integer, String

from app.db.database import Base


class Result(Base):
    __tablename__ = "results"

    id = Column( Integer, primary_key=True, index=True )
    hall_ticket = Column( String(50), unique=True, nullable=False, index=True )
    student_name = Column( String(100), nullable=False )
    grade = Column( String(5), nullable=False )
    total_marks = Column( Integer, nullable=False )
    