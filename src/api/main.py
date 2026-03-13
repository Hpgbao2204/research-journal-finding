from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import settings
from src.api.endpoints import journals

def get_application() -> FastAPI:
    """Khởi tạo và cấu hình ứng dụng FastAPI"""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="Backend API for mapping Journal Data (SJR + Web of Science)."
    )

    # Cấu hình CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    application.include_router(
        journals.router, 
        prefix=f"{settings.API_V1_STR}/journals", 
        tags=["Journals"]
    )

    return application

app = get_application()

if __name__ == "__main__":
    import uvicorn
    # Hỗ trợ chạy trực tiếp bằng python src/api/main.py
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
