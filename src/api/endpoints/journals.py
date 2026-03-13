from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.api.db.database import get_db
from src.api.models.journal import Journal
from src.api.schemas.journal import PaginatedJournalsResponse

router = APIRouter()

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
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm tạp chí theo tên, lĩnh vực hoặc rank.
    """
    query = db.query(Journal)
    
    if keyword:
        # Sử dụng ilike để tìm kiếm không phân biệt chữ hoa, chữ thường
        query = query.filter(Journal.Title.ilike(f"%{keyword}%"))
    if category:
        query = query.filter(Journal.Subject_Area_Category.ilike(f"%{category}%"))
    if rank:
        query = query.filter(Journal.SJR_Rank.ilike(f"%{rank}%"))
        
    total = query.count()
    offset = (page - 1) * limit
    journals = query.offset(offset).limit(limit).all()
    
    return PaginatedJournalsResponse(
        total=total,
        page=page,
        limit=limit,
        data=journals
    )
