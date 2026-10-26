"""`design-review check | fitness | report`. Wires the adapters into the use cases and owns the exit codes."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

from design_review.application.check_documents import check_documents, run_fitness_functions
from design_review.application.reporting import render_fitness, render_markdown, render_text
from design_review.domain.capacity import ModelError
from design_review.infrastructure.filesystem import FileSystemStore
from design_review.infrastructure.markdown import MarkdownDocumentReader
from design_review.infrastructure.model_toml import TomlModelSource
from design_review.infrastructure.settings import SettingsError, load_settings


def build_parser() -> argparse.ArgumentParser:
    """The command line: three subcommands."""
    parser = argparse.ArgumentParser(
        prog="design-review", description="Check a design review and its fitness functions."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="lint the requirements, the proposal, the review records and the checklist")
    commands.add_parser("fitness", help="run the capacity, queue and write-order fitness functions")
    commands.add_parser("report", help="write the Markdown report under REPORT_DIR")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command and return the exit code: 0 ok, 1 findings or a surprising scenario, 2 bad configuration."""
    args = build_parser().parse_args(argv)
    try:
        settings = load_settings(os.environ)
    except SettingsError as problem:
        print(f"configuration error: {problem}", file=sys.stderr)
        return 2
    store = FileSystemStore(settings.root)
    reader = MarkdownDocumentReader(store)
    try:
        if args.command == "check":
            report = check_documents(store, reader, settings.check)
            print(render_text(report))
            return 0 if report.ok else 1
        fitness = run_fitness_functions(TomlModelSource(store))
    except ModelError as problem:
        print(f"model error: {problem}", file=sys.stderr)
        return 2
    if args.command == "fitness":
        print(render_fitness(fitness))
        return 0 if fitness.ok else 1
    report = check_documents(store, reader, settings.check)
    store.write_text(f"{settings.report_dir}/report.md", render_markdown(report, fitness))
    print(f"wrote {settings.report_dir}/report.md")
    return 0 if report.ok and fitness.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
