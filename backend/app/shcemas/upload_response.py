from pydantic import BaseModel


class UploadResponse(BaseModel):
    inserted: int
    duplicates: int
    errors: list[str]