from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class SettingsError(ValueError):
    """Raised when settings.json is malformed."""


@dataclass(slots=True)
class PipelineSettings:
    java_path: str | None = None
    java_cli_jar: str | None = None
    minie_jar_path: str | None = None
    minie_url: str | None = None


def settings_path(workspace_dir: Path) -> Path:
    return workspace_dir / "settings.json"


def _optional_string(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise SettingsError(f"Setting '{key}' must be a string or null")
    return value


def load_settings(workspace_dir: Path) -> PipelineSettings:
    path = settings_path(workspace_dir)
    if not path.exists():
        return PipelineSettings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SettingsError(f"Cannot read settings file '{path}': {exc}") from exc
    if not isinstance(data, dict):
        raise SettingsError(f"Settings file '{path}' must contain a JSON object")
    return PipelineSettings(
        java_path=_optional_string(data, "java_path"),
        java_cli_jar=_optional_string(data, "java_cli_jar"),
        minie_jar_path=_optional_string(data, "minie_jar_path"),
        minie_url=_optional_string(data, "minie_url"),
    )


def save_settings(workspace_dir: Path, settings: PipelineSettings) -> None:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    path = settings_path(workspace_dir)
    temporary_path = path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(asdict(settings), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)
