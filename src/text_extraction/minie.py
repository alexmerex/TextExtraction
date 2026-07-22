from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from .config import PipelineConfig
from .downloader import ensure_minie_jar


class MinieError(RuntimeError):
    """Base error for MinIE configuration and extraction failures."""


class MinieNotConfiguredError(MinieError):
    pass


def _resolve_minie_jar(
    config: PipelineConfig,
    log_fn: Callable[[str], None] | None = None,
) -> Path:
    env_jar = os.environ.get("TEXT_EXTRACTION_MINIE_JAR")
    candidates = [Path(env_jar).expanduser() if env_jar else None, config.minie_jar_path]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate.resolve()
    if env_jar:
        raise MinieNotConfiguredError(
            f"TEXT_EXTRACTION_MINIE_JAR does not point to a file: {env_jar}"
        )
    if config.minie_jar_path:
        raise MinieNotConfiguredError(f"MinIE jar not found: {config.minie_jar_path}")
    if config.minie_url:
        return ensure_minie_jar(config, log_fn=log_fn)
    raise MinieNotConfiguredError(
        "MinIE jar not configured. Set TEXT_EXTRACTION_MINIE_JAR, "
        "minie_jar_path, or minie_url in settings.json."
    )


def _load_java_classes(minie_jar: Path) -> tuple[Any, Any, Any]:
    # Pyjnius starts a JVM on first import. Its classpath must be configured first.
    os.environ["CLASSPATH"] = os.pathsep.join(
        value for value in (os.environ.get("CLASSPATH"), str(minie_jar)) if value
    )
    try:
        import jnius_config

        if not getattr(jnius_config, "vm_running", False):
            jnius_config.add_classpath(str(minie_jar))
        from jnius import autoclass
    except (ImportError, ValueError) as exc:
        raise MinieError(f"Unable to initialize Pyjnius: {exc}") from exc
    try:
        return (
            autoclass("de.uni_mannheim.utils.coreNLP.CoreNLPUtils"),
            autoclass("de.uni_mannheim.minie.MinIE"),
            autoclass("java.lang.String"),
        )
    except Exception as exc:
        raise MinieError(
            "The configured JAR does not contain MinIE and its runtime dependencies"
        ) from exc


def split_sentences(text: str) -> Iterator[str]:
    for sentence in re.split(r"(?<=[.!?])\s+|[\r\n]+", text.strip()):
        if sentence := sentence.strip():
            yield sentence


def extract_triples(
    config: PipelineConfig,
    log_fn: Callable[[str], None] | None = None,
) -> None:
    minie_jar = _resolve_minie_jar(config, log_fn=log_fn)
    if log_fn:
        log_fn(f"Using MinIE jar: {minie_jar}")
    CoreNLPUtils, MinIE, String = _load_java_classes(minie_jar)
    parser = CoreNLPUtils.StanfordDepNNParser()

    if not config.content_after_coref_file.is_file():
        raise FileNotFoundError(f"Coreference output not found: {config.content_after_coref_file}")
    sentences = list(split_sentences(config.content_after_coref_file.read_text(encoding="utf-8")))
    triples: list[str] = []
    for index, sentence in enumerate(sentences, start=1):
        try:
            minie = MinIE(String(sentence), parser, 2)
            for proposition in minie.getPropositions().elements():
                if proposition is not None:
                    triples.append(str(proposition.getTripleAsString()))
        except Exception as exc:
            raise MinieError(f"MinIE failed on sentence {index}: {sentence}") from exc
        if log_fn and (index % 5 == 0 or index == len(sentences)):
            log_fn(f"Processed {index}/{len(sentences)} sentences")

    config.triples_file.write_text("\n".join(triples), encoding="utf-8")
