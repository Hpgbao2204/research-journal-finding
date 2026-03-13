from typing import List, Optional
from pydantic import BaseModel

class JournalBase(BaseModel):
    Title: str
    ISSN: str
    SJR_Rank: str
    Subject_Area_Category: str
    Publisher: str

class JournalResponse(JournalBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True

class PaginatedJournalsResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[JournalResponse]
