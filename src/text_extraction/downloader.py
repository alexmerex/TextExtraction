from __future__ import annotations

import shutil
import urllib.request
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

from .config import PipelineConfig


class DownloadError(RuntimeError):
    """Raised when the MinIE artifact cannot be downloaded safely."""


def ensure_minie_jar(
    config: PipelineConfig,
    log_fn: Callable[[str], None] | None = None,
) -> Path:
    if not config.minie_url:
        raise DownloadError("MinIE download URL is not configured")
    parsed_url = urlparse(config.minie_url)
    if parsed_url.scheme not in {"http", "https"}:
        raise DownloadError("MinIE URL must use http or https")

    target_dir = config.workspace_dir / ".text-extraction" / "artifacts"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "minie.jar"
    if target_path.is_file() and target_path.stat().st_size > 0:
        return target_path

    temporary_path = target_path.with_suffix(".jar.part")
    if log_fn:
        log_fn(f"Downloading MinIE jar from {config.minie_url}")
    try:
        request = urllib.request.Request(
            config.minie_url,
            headers={"User-Agent": "text-extraction/0.2"},
        )
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            temporary_path.open("wb") as output,
        ):
            shutil.copyfileobj(response, output)
        if temporary_path.stat().st_size == 0:
            raise DownloadError("Downloaded MinIE jar is empty")
        with temporary_path.open("rb") as jar_file:
            if jar_file.read(2) != b"PK":
                raise DownloadError("Downloaded file is not a valid JAR/ZIP archive")
        temporary_path.replace(target_path)
    except DownloadError:
        temporary_path.unlink(missing_ok=True)
        raise
    except Exception as exc:  # urllib exposes several unrelated exception types
        temporary_path.unlink(missing_ok=True)
        raise DownloadError(f"Failed to download MinIE jar: {exc}") from exc
    return target_path
