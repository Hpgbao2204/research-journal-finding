from sqlalchemy import Column, Integer, String
from src.api.db.database import Base

class Journal(Base):
    __tablename__ = "Journal"

    # SQLite có sẵn cột rowid cho các bảng không có khóa chính chuẩn
    id = Column("rowid", Integer, primary_key=True)
    Title = Column(String, index=True)
    ISSN = Column(String)
    SJR_Rank = Column(String)
    Subject_Area_Category = Column(String)
    Publisher = Column(String)
