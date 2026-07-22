from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def _configured_path(value: str | None, base_dir: Path) -> Path | None:
    if not value:
        return None
    path = Path(os.path.expandvars(os.path.expanduser(value)))
    return path if path.is_absolute() else (base_dir / path).resolve()


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    workspace_dir: Path
    content_file: Path
    content_after_coref_file: Path
    triples_file: Path
    language_info_file: Path
    java_cli_jar: Path
    minie_jar_path: Path | None = None
    minie_url: str | None = None
    java_path: str | None = None

    @classmethod
    def from_workspace(
        cls,
        workspace_dir: Path,
        *,
        project_root: Path | None = None,
    ) -> PipelineConfig:
        from .settings import load_settings

        workspace_dir = workspace_dir.expanduser().resolve()
        project_root = (project_root or PACKAGE_ROOT).resolve()
        settings = load_settings(workspace_dir)
        java_cli_jar = _configured_path(settings.java_cli_jar, workspace_dir)
        if java_cli_jar is None:
            java_cli_jar = project_root / "java" / "build" / "libs" / "text-extraction-java.jar"

        return cls(
            workspace_dir=workspace_dir,
            content_file=workspace_dir / "content.txt",
            content_after_coref_file=workspace_dir / "content_afterChange.txt",
            triples_file=workspace_dir / "triples.txt",
            language_info_file=workspace_dir / "language_info.txt",
            java_cli_jar=java_cli_jar,
            minie_jar_path=_configured_path(settings.minie_jar_path, workspace_dir),
            minie_url=settings.minie_url,
            java_path=settings.java_path,
        )
