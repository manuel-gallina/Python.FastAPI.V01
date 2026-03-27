"""Utilities for processing pytest-cov output and generating coverage reports."""

import re
from dataclasses import dataclass
from enum import StrEnum, auto


_FULL_COVERAGE_PCT = 100


class CoverageFormats(StrEnum):
    """Supported output formats of the coverage report."""

    TERMINAL = auto()
    MARKDOWN = auto()


@dataclass
class CoverageRow:
    """Holds parsed data for a single module coverage row."""

    name: str
    stmts: int
    miss: int
    branch: int
    brpart: int
    cover_pct: int
    cover_str: str


def _parse_coverage_output(output: str) -> tuple[str, list[CoverageRow]]:
    """Parses the terminal output of pytest with --cov-branch flags.

    Args:
        output (str): Raw stdout from pytest with --cov=src --cov-branch
            --cov-report=term-missing.

    Returns:
        tuple[str, list[CoverageRow]]: A (total_cover_str, below_100) pair
            where total_cover_str is the overall coverage percentage string
            and below_100 is a list of CoverageRow instances for modules
            below 100%, sorted by ascending cover_pct.
    """
    total_cover_str = "N/A"
    below_100: list[CoverageRow] = []

    # Matches: name  stmts  miss  branch  brpart  cover%  [missing...]
    row_pattern = re.compile(r"^(\S.+?)\s{2,}(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%")

    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("TOTAL"):
            m = re.search(r"(\d+%)", stripped)
            if m:
                total_cover_str = m.group(1)
        else:
            m = row_pattern.match(stripped)
            if m:
                cover_pct = int(m.group(6))
                if cover_pct < _FULL_COVERAGE_PCT:
                    below_100.append(
                        CoverageRow(
                            name=m.group(1).strip(),
                            stmts=int(m.group(2)),
                            miss=int(m.group(3)),
                            branch=int(m.group(4)),
                            brpart=int(m.group(5)),
                            cover_pct=cover_pct,
                            cover_str=f"{cover_pct}%",
                        )
                    )

    below_100.sort(key=lambda r: r.cover_pct)
    return total_cover_str, below_100


def format_coverage(
    raw_output: str, output_format: CoverageFormats = CoverageFormats.TERMINAL
) -> str:
    """Formats a pytest-cov terminal output into a human-readable coverage report.

    Args:
        raw_output (str): Raw stdout from pytest with --cov=src --cov-branch
            --cov-report=term-missing.
        output_format (CoverageFormats): The output format for the coverage report.

    Returns:
        str: A formatted coverage report.
    """
    total_cover_str, below_100 = _parse_coverage_output(raw_output)

    if output_format == CoverageFormats.MARKDOWN:
        return _format_markdown(total_cover_str, below_100)
    return _format_terminal(total_cover_str, below_100)


def _format_terminal(total_cover_str: str, below_100: list[CoverageRow]) -> str:
    lines = [
        "Coverage Report",
        "===============",
        "",
        f"Overall coverage: {total_cover_str}",
    ]
    if not below_100:
        return "\n".join(lines)

    col_name = max(len("Module"), *(len(r.name) for r in below_100))
    col_stmts = max(len("Stmts"), *(len(str(r.stmts)) for r in below_100))
    col_miss = max(len("Miss"), *(len(str(r.miss)) for r in below_100))
    col_branch = max(len("Branch"), *(len(str(r.branch)) for r in below_100))
    col_brpart = max(len("BrPart"), *(len(str(r.brpart)) for r in below_100))
    col_cover = max(len("Cover"), *(len(r.cover_str) for r in below_100))

    def fmt_row(row: CoverageRow) -> str:
        return (
            f"{row.name:<{col_name}}  "
            f"{row.stmts:>{col_stmts}}  "
            f"{row.miss:>{col_miss}}  "
            f"{row.branch:>{col_branch}}  "
            f"{row.brpart:>{col_brpart}}  "
            f"{row.cover_str:>{col_cover}}"
        )

    header = (
        f"{'Module':<{col_name}}  "
        f"{'Stmts':>{col_stmts}}  "
        f"{'Miss':>{col_miss}}  "
        f"{'Branch':>{col_branch}}  "
        f"{'BrPart':>{col_brpart}}  "
        f"{'Cover':>{col_cover}}"
    )
    lines += ["", "Modules below 100%:", "", header, "-" * len(header)]
    for r in below_100:
        lines.append(fmt_row(r))

    return "\n".join(lines)


def _format_markdown(total_cover_str: str, below_100: list[CoverageRow]) -> str:
    lines = ["# Coverage Report", "", f"**Overall coverage: {total_cover_str}**"]
    if below_100:
        lines += [
            "",
            "## Modules below 100%",
            "",
            "| Module | Stmts | Miss | Branch | BrPart | Cover |",
            "|--------|------:|-----:|-------:|-------:|------:|",
        ]
        for r in below_100:
            lines.append(
                f"| {r.name} | {r.stmts} | {r.miss}"
                f" | {r.branch} | {r.brpart} | {r.cover_str} |"
            )
    return "\n".join(lines)
