from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_config_dir() -> Path:
    return get_project_root() / "config"


def get_assets_dir() -> Path:
    return get_project_root() / "assets"


def get_asset_path(filename: str) -> Path:
    return get_assets_dir() / filename


def get_legacy_project_root() -> Path:
    return Path(r"E:\自作アプリ集\ランチャー_v2")


def get_legacy_config_file() -> Path:
    return get_legacy_project_root() / "config" / "settings.json"
