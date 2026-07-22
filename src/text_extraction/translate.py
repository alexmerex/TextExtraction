from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

from .config import PipelineConfig

TranslatorFn = Callable[[str, str, str], str]
VIETNAMESE_CHARACTERS = frozenset(
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
)
TRANSLATION_CHUNK_SIZE = 4500


class TranslationError(RuntimeError):
    """Raised when the configured translation provider fails."""


def is_vietnamese(text: str) -> bool:
    return any(character in VIETNAMESE_CHARACTERS for character in text.casefold())


def _chunks(text: str, limit: int = TRANSLATION_CHUNK_SIZE) -> Iterator[str]:
    remaining = text.strip()
    while len(remaining) > limit:
        split_at = max(
            remaining.rfind("\n", 0, limit + 1),
            remaining.rfind(". ", 0, limit + 1),
            remaining.rfind(" ", 0, limit + 1),
        )
        if split_at <= 0:
            split_at = limit
        yield remaining[:split_at].strip()
        remaining = remaining[split_at:].lstrip()
    if remaining:
        yield remaining


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    if not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return "\n".join(translator.translate(chunk) for chunk in _chunks(text))
    except Exception as exc:  # provider exceptions are not part of a stable public API
        raise TranslationError(
            f"Translation from {source_lang} to {target_lang} failed: {exc}"
        ) from exc


def prepare_content(
    input_file: Path,
    config: PipelineConfig,
    *,
    source_language: str = "auto",
    translator: TranslatorFn = translate_text,
    log_fn: Callable[[str], None] | None = None,
) -> None:
    input_file = input_file.expanduser().resolve()
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    content = input_file.read_text(encoding="utf-8-sig")
    if not content.strip():
        raise ValueError(f"Input file is empty: {input_file}")
    if source_language not in {"auto", "en", "vi"}:
        raise ValueError("source_language must be one of: auto, en, vi")

    original_language = (
        "vi"
        if source_language == "vi" or (source_language == "auto" and is_vietnamese(content))
        else "en"
    )
    if original_language == "vi":
        if log_fn:
            log_fn("Detected Vietnamese content; translating to English")
        content = translator(content, "vi", "en")

    config.content_file.write_text(content, encoding="utf-8")
    config.language_info_file.write_text(original_language, encoding="utf-8")


def translate_triples_if_needed(
    config: PipelineConfig,
    *,
    translator: TranslatorFn = translate_text,
    log_fn: Callable[[str], None] | None = None,
) -> None:
    if not config.language_info_file.exists():
        return
    original_language = config.language_info_file.read_text(encoding="utf-8").strip()
    if original_language != "vi":
        return
    if not config.triples_file.exists():
        raise FileNotFoundError(f"Triples file not found: {config.triples_file}")

    triples = config.triples_file.read_text(encoding="utf-8")
    if not triples.strip():
        return
    if log_fn:
        log_fn("Translating triples back to Vietnamese")
    config.triples_file.write_text(translator(triples, "en", "vi"), encoding="utf-8")
