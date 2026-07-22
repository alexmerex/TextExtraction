from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

from .config import PipelineConfig
from .minie import extract_triples
from .translate import prepare_content, translate_triples_if_needed


class JavaCorefError(RuntimeError):
    """Raised when the Java coreference stage cannot be executed."""


def run_pipeline(
    input_file: Path,
    workspace_dir: Path,
    log_fn: Callable[[str], None] | None = None,
    *,
    source_language: str = "auto",
    skip_coref: bool = False,
) -> PipelineConfig:
    workspace_dir = workspace_dir.expanduser().resolve()
    workspace_dir.mkdir(parents=True, exist_ok=True)
    config = PipelineConfig.from_workspace(workspace_dir)

    _log(log_fn, "Preparing content")
    prepare_content(input_file, config, source_language=source_language, log_fn=log_fn)
    if skip_coref:
        _log(log_fn, "Skipping Java coreference")
        shutil.copyfile(config.content_file, config.content_after_coref_file)
    else:
        _log(log_fn, "Running Java coreference")
        _run_java_coref(config, log_fn=log_fn)
    _log(log_fn, "Extracting triples with MinIE")
    extract_triples(config, log_fn=log_fn)
    _log(log_fn, "Translating triples if needed")
    translate_triples_if_needed(config, log_fn=log_fn)
    return config


def _run_java_coref(
    config: PipelineConfig,
    log_fn: Callable[[str], None] | None = None,
) -> None:
    if not config.java_cli_jar.is_file():
        raise JavaCorefError(
            f"Java CLI jar not found: {config.java_cli_jar}. "
            "Build it with: cd java && ./gradlew shadowJar"
        )
    java_bin = config.java_path or "java"
    _log(log_fn, f"Using Java binary: {java_bin}")
    command = [
        java_bin,
        "-jar",
        str(config.java_cli_jar),
        "coref",
        "--workspace",
        str(config.workspace_dir),
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
    except FileNotFoundError as exc:
        raise JavaCorefError(f"Java executable not found: {java_bin}") from exc
    except subprocess.TimeoutExpired as exc:
        raise JavaCorefError("Java coreference timed out after 10 minutes") from exc
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or str(exc)).strip()
        raise JavaCorefError(f"Java coreference failed: {details}") from exc
    if result.stdout.strip():
        _log(log_fn, result.stdout.strip())
    if not config.content_after_coref_file.is_file():
        raise JavaCorefError("Java coreference finished without creating its output file")


def _log(log_fn: Callable[[str], None] | None, message: str) -> None:
    if log_fn:
        log_fn(message)
