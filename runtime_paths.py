from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def configure_crewai_storage() -> None:
    """Keep CrewAI runtime storage inside the project when running in restricted environments."""
    workspace_appdata = BASE_DIR / ".crewai_appdata"
    os.environ["LOCALAPPDATA"] = str(workspace_appdata)
    os.environ["APPDATA"] = str(workspace_appdata)
    os.environ.setdefault("CREWAI_STORAGE_DIR", "ai-project-manager")
    try:
        import appdirs
    except ImportError:
        return

    def workspace_user_data_dir(
        appname: str | None = None,
        appauthor: str | None = None,
        version: str | None = None,
        roaming: bool = False,
    ) -> str:
        parts = [workspace_appdata]
        if appauthor:
            parts.append(Path(appauthor))
        if appname:
            parts.append(Path(appname))
        if version:
            parts.append(Path(version))
        return str(Path(*parts))

    appdirs.user_data_dir = workspace_user_data_dir
