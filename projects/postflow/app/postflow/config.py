from pathlib import Path


APP_NAME = "PostFlow"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DATA_DIR = PROJECT_ROOT / "runtime"
DB_PATH = APP_DATA_DIR / "postflow.db"
STYLE_PATH = PROJECT_ROOT / "app" / "postflow" / "assets" / "styles" / "app.qss"
