import os
from pathlib import Path

class Settings:
    PROJECT_NAME: str = "Journal Finder API"
    API_V1_STR: str = "/api"
    # Lấy đường dẫn root từ file hiện tại (src/api/core/config.py)
    # parents[0]: core, parents[1]: api, parents[2]: src, parents[3]: root
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
    DB_PATH: Path = PROJECT_ROOT / "output" / "journals.db"
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"

settings = Settings()
