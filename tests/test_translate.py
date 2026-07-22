from pathlib import Path

import pytest

from text_extraction.config import PipelineConfig
from text_extraction.translate import (
    is_vietnamese,
    prepare_content,
    translate_triples_if_needed,
)


def test_detects_vietnamese_diacritics_without_mojibake() -> None:
    assert is_vietnamese("Tôi là người Việt Nam.")
    assert is_vietnamese("Đây là một câu tiếng Việt.")
    assert not is_vietnamese("This is an English sentence.")


def test_prepare_content_translates_vietnamese(tmp_path: Path, config: PipelineConfig) -> None:
    source = tmp_path / "input.txt"
    source.write_text("Tôi yêu Hà Nội.", encoding="utf-8")
    calls: list[tuple[str, str, str]] = []

    def fake_translate(text: str, source_lang: str, target_lang: str) -> str:
        calls.append((text, source_lang, target_lang))
        return "I love Hanoi."

    prepare_content(source, config, translator=fake_translate)

    assert config.content_file.read_text(encoding="utf-8") == "I love Hanoi."
    assert config.language_info_file.read_text(encoding="utf-8") == "vi"
    assert calls == [("Tôi yêu Hà Nội.", "vi", "en")]


def test_source_language_can_be_forced_for_unaccented_vietnamese(
    tmp_path: Path, config: PipelineConfig
) -> None:
    source = tmp_path / "input.txt"
    source.write_text("Toi yeu Ha Noi.", encoding="utf-8")

    prepare_content(
        source,
        config,
        source_language="vi",
        translator=lambda text, source, target: "I love Hanoi.",
    )

    assert config.language_info_file.read_text(encoding="utf-8") == "vi"


def test_prepare_content_rejects_empty_input(tmp_path: Path, config: PipelineConfig) -> None:
    source = tmp_path / "empty.txt"
    source.write_text("  ", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        prepare_content(source, config)


def test_translates_nonempty_triples_back_to_vietnamese(config: PipelineConfig) -> None:
    config.language_info_file.write_text("vi", encoding="utf-8")
    config.triples_file.write_text("Alice; likes; Bob", encoding="utf-8")

    translate_triples_if_needed(
        config,
        translator=lambda text, source, target: "Alice; thích; Bob",
    )

    assert config.triples_file.read_text(encoding="utf-8") == "Alice; thích; Bob"
