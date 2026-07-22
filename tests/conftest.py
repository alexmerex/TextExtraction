from pathlib import Path

import pytest

from text_extraction.config import PipelineConfig


@pytest.fixture
def config(tmp_path: Path) -> PipelineConfig:
    return PipelineConfig(
        workspace_dir=tmp_path,
        content_file=tmp_path / "content.txt",
        content_after_coref_file=tmp_path / "content_afterChange.txt",
        triples_file=tmp_path / "triples.txt",
        language_info_file=tmp_path / "language_info.txt",
        java_cli_jar=tmp_path / "text-extraction-java.jar",
    )
