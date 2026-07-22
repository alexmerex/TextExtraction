from pathlib import Path

import pytest

from text_extraction.config import PipelineConfig
from text_extraction.minie import (
    MinieNotConfiguredError,
    _resolve_minie_jar,
    split_sentences,
)


def test_split_sentences_handles_punctuation_and_lines() -> None:
    assert list(split_sentences("One sentence. Another one!\nLast one?")) == [
        "One sentence.",
        "Another one!",
        "Last one?",
    ]


def test_missing_environment_jar_is_reported(
    monkeypatch: pytest.MonkeyPatch, config: PipelineConfig
) -> None:
    monkeypatch.setenv("TEXT_EXTRACTION_MINIE_JAR", "missing.jar")

    with pytest.raises(MinieNotConfiguredError, match="TEXT_EXTRACTION_MINIE_JAR"):
        _resolve_minie_jar(config)


def test_environment_jar_takes_precedence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, config: PipelineConfig
) -> None:
    jar = tmp_path / "minie.jar"
    jar.write_bytes(b"PK-test")
    monkeypatch.setenv("TEXT_EXTRACTION_MINIE_JAR", str(jar))

    assert _resolve_minie_jar(config) == jar.resolve()
