from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract relational triples from a text file")
    parser.add_argument("input_file", type=Path, help="UTF-8 input text file")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Directory for settings, intermediate files, and output",
    )
    parser.add_argument(
        "--source-language",
        choices=("auto", "en", "vi"),
        default="auto",
        help="Original input language (default: detect Vietnamese diacritics)",
    )
    parser.add_argument(
        "--skip-coref",
        action="store_true",
        help="Copy the prepared input directly to extraction without Java coreference",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        config = run_pipeline(
            args.input_file,
            args.workspace,
            log_fn=print,
            source_language=args.source_language,
            skip_coref=args.skip_coref,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from exc
    print(f"Triples written to: {config.triples_file}")


if __name__ == "__main__":
    main()
