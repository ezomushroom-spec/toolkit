from __future__ import annotations

import argparse
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[4]
ARCHIVE_ROOT = ROOT / "archive" / "snapshots"
EXCLUDED_DIRS = {"venv", "node_modules", "__pycache__", "build", "dist"}
EXCLUDED_FILE_PATTERNS = ["*.log"]
EXCLUDED_NAME_PATTERNS = ["*_profile"]


def is_excluded_dir(path: Path) -> bool:
    return path.name in EXCLUDED_DIRS or any(fnmatch(path.name, pattern) for pattern in EXCLUDED_NAME_PATTERNS)


def is_excluded_file(path: Path) -> bool:
    return any(fnmatch(path.name, pattern) for pattern in EXCLUDED_FILE_PATTERNS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a lightweight zip snapshot for a project.")
    parser.add_argument("--project", required=True, help="Absolute or relative path to the project folder.")
    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    if not project_path.exists() or not project_path.is_dir():
        raise SystemExit(f"project directory not found: {project_path}")

    project_name = project_path.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = ARCHIVE_ROOT / project_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_zip = output_dir / f"{timestamp}.zip"

    with ZipFile(output_zip, "w", compression=ZIP_DEFLATED) as zf:
        for path in project_path.rglob("*"):
            rel = path.relative_to(project_path)
            if any(is_excluded_dir(parent) for parent in path.parents if parent != project_path):
                continue
            if path.is_dir() and is_excluded_dir(path):
                continue
            if path.is_file():
                if is_excluded_file(path):
                    continue
                if any(fnmatch(parent.name, pattern) for parent in path.parents for pattern in EXCLUDED_NAME_PATTERNS):
                    continue
                zf.write(path, arcname=str(rel))

    print(output_zip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
