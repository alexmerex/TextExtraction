from types import SimpleNamespace

import pytest

from text_extraction.config import PipelineConfig
from text_extraction.pipeline import JavaCorefError, _run_java_coref, run_pipeline


def test_java_coref_uses_configured_artifact_and_workspace(
    monkeypatch: pytest.MonkeyPatch, config: PipelineConfig
) -> None:
    config.java_cli_jar.write_bytes(b"jar")
    config.content_file.write_text("Alice said she left.", encoding="utf-8")
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        commands.append(command)
        config.content_after_coref_file.write_text("Alice said Alice left.", encoding="utf-8")
        return SimpleNamespace(stdout="done")

    monkeypatch.setattr("text_extraction.pipeline.subprocess.run", fake_run)
    _run_java_coref(config)

    assert commands[0] == [
        "java",
        "-jar",
        str(config.java_cli_jar),
        "coref",
        "--workspace",
        str(config.workspace_dir),
    ]


def test_java_coref_reports_missing_build(config: PipelineConfig) -> None:
    with pytest.raises(JavaCorefError, match="Build it with"):
        _run_java_coref(config)


def test_pipeline_can_skip_coreference(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    source = tmp_path / "source.txt"
    workspace = tmp_path / "workspace"
    source.write_text("Alice likes Bob.", encoding="utf-8")

    def fake_extract(config: PipelineConfig, log_fn=None) -> None:
        assert config.content_after_coref_file.read_text(encoding="utf-8") == "Alice likes Bob."
        config.triples_file.write_text("Alice; likes; Bob", encoding="utf-8")

    monkeypatch.setattr("text_extraction.pipeline.extract_triples", fake_extract)
    result = run_pipeline(source, workspace, skip_coref=True)

    assert result.triples_file.read_text(encoding="utf-8") == "Alice; likes; Bob"
