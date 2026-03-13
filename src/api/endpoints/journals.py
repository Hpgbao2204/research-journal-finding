from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.api.db.database import get_db
from src.api.models.journal import Journal
from src.api.schemas.journal import PaginatedJournalsResponse

router = APIRouter()

@router.get("/filters")
def get_filter_options(db: Session = Depends(get_db)):
    """
    Lấy danh sách động các Publishers và trích xuất các chuyên ngành (Categories)
    được phân cách bởi dấu chấm phẩy trong DB.
    """
    # Lấy danh sách Publishers (top 100 có nhiều journal nhất)
    publishers = db.query(Journal.Publisher, func.count(Journal.id).label('total')) \
                   .filter(Journal.Publisher != "Unknown Publisher") \
                   .group_by(Journal.Publisher) \
                   .order_by(func.count(Journal.id).desc()) \
                   .limit(100).all()
    publisher_list = [p.Publisher for p in publishers if p.Publisher]

    # Để xử lý Category phức tạp: ta trả về một danh sách các subject phổ biến hardcode mở rộng
    # (Vì tách ; và gom nhóm on-the-fly SQL qua hàng chục nghìn dòng hơi nặng cho SQLite)
    popular_categories = [
        "Computer Science", "Artificial Intelligence", "Computer Networks", "Information Systems",
        "Software", "Mathematics", "Medicine", "Engineering", "Electrical", "Mechanical",
        "Business", "Economics", "Physics", "Chemistry", "Social Sciences",
        "Materials Science", "Biology", "Environmental", "Nursing", "Dentistry"
    ]

    return {
        "publishers": sorted(publisher_list),
        "categories": sorted(popular_categories)
    }

@router.get("/", response_model=PaginatedJournalsResponse)
def get_journals(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách các tạp chí với hỗ trợ phân trang.
    """
    offset = (page - 1) * limit
    total = db.query(Journal).count()
    journals = db.query(Journal).offset(offset).limit(limit).all()
    
    return PaginatedJournalsResponse(
        total=total,
        page=page,
        limit=limit,
        data=journals
    )

@router.get("/search", response_model=PaginatedJournalsResponse)
def search_journals(
    keyword: Optional[str] = Query(None, description="Search term in Title"),
    category: Optional[str] = Query(None, description="Filter by Category"),
    rank: Optional[str] = Query(None, description="Filter by SJR Rank (e.g., Q1, Q2)"),
    publisher: Optional[str] = Query(None, description="Filter by Publisher"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm tạp chí theo tên, lĩnh vực, rank, hoặc nhà xuất bản.
    """
    query = db.query(Journal)
    
    if keyword:
        # Sử dụng ilike để tìm kiếm không phân biệt chữ hoa, chữ thường
        query = query.filter(Journal.Title.ilike(f"%{keyword}%"))
    if category:
        query = query.filter(Journal.Subject_Area_Category.ilike(f"%{category}%"))
    if rank:
        query = query.filter(Journal.SJR_Rank.ilike(f"%{rank}%"))
    if publisher:
        query = query.filter(Journal.Publisher.ilike(f"%{publisher}%"))
        
    total = query.count()
    offset = (page - 1) * limit
    journals = query.offset(offset).limit(limit).all()
    
    return PaginatedJournalsResponse(
        total=total,
        page=page,
        limit=limit,
        data=journals
    )
