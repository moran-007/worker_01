import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
BACKUP_DIR = BASE_DIR / "backups"
UPLOAD_DIR = DATA_DIR / "uploads"
COURSEWARE_UPLOAD_DIR = UPLOAD_DIR / "courseware"
SCRATCH_UPLOAD_DIR = UPLOAD_DIR / "scratch"
MATERIAL_UPLOAD_DIR = UPLOAD_DIR / "materials"

DATABASE_PATH = DATA_DIR / "attendance.db"
DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "sqlite").lower()

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "worker")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "123456")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "class_worker")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://127.0.0.1:5173/")

UPLOAD_MAX_BYTES = int(os.environ.get("UPLOAD_MAX_BYTES", str(50 * 1024 * 1024)))
ALLOWED_UPLOAD_EXTENSIONS = {
    ".csv",
    ".doc",
    ".docx",
    ".gif",
    ".jpg",
    ".jpeg",
    ".md",
    ".mp3",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".sb2",
    ".sb3",
    ".sprite2",
    ".sprite3",
    ".svg",
    ".wav",
    ".xlsx",
    ".xlsm",
    ".zip",
}

HYDRO_BASE_URL = os.environ.get("HYDRO_BASE_URL", "")
HYDRO_INTEGRATION_MODE = os.environ.get("HYDRO_INTEGRATION_MODE", "embedded").lower()
SCRATCH_EDITOR_URL = os.environ.get("SCRATCH_EDITOR_URL", "http://127.0.0.1:8601/")
SCRATCH_OJ_API_URL = os.environ.get("SCRATCH_OJ_API_URL", "http://127.0.0.1:3000/")
SCRATCH_EDITOR_PROJECT_DIR = os.environ.get(
    "SCRATCH_EDITOR_PROJECT_DIR",
    r"E:\moran_project\OJ_text\uploads\editor-projects",
)
