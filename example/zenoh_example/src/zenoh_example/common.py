import os
from pathlib import Path
import zenoh

def get_config_path() -> Path:
    """設定ファイルのパスを取得する"""
    return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "roboapp"

def create_zenoh_session() -> zenoh.Session:
    return zenoh.open(zenoh.Config.from_file(get_config_path() / "zenoh.json5"))

