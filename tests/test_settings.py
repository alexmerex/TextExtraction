import json
from pathlib import Path

import pytest

from text_extraction.config import PipelineConfig
from text_extraction.settings import (
    PipelineSettings,
    SettingsError,
    load_settings,
    save_settings,
)


def test_settings_round_trip(tmp_path: Path) -> None:
    expected = PipelineSettings(
        java_path="custom-java",
        java_cli_jar="tools/coref.jar",
        minie_jar_path="tools/minie.jar",
        minie_url="https://example.test/minie.jar",
    )
    save_settings(tmp_path, expected)

    assert load_settings(tmp_path) == expected


def test_invalid_settings_have_a_clear_error(tmp_path: Path) -> None:
    (tmp_path / "settings.json").write_text("[]", encoding="utf-8")

    with pytest.raises(SettingsError, match="JSON object"):
        load_settings(tmp_path)


def test_config_resolves_artifacts_independently_from_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = tmp_path / "project"
    workspace.mkdir()

    config = PipelineConfig.from_workspace(workspace, project_root=project)

    assert config.java_cli_jar == project / "java" / "build" / "libs" / "text-extraction-java.jar"


def test_non_string_setting_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "settings.json").write_text(json.dumps({"java_path": 123}), encoding="utf-8")

    with pytest.raises(SettingsError, match="java_path"):
        load_settings(tmp_path)
