"""Utilities for processing pytest-cov output and generating coverage reports."""

import re
from enum import StrEnum, auto


class CoverageFormats(StrEnum):
    """Supported output formats of the coverage report."""

    TERMINAL = auto()
    MARKDOWN = auto()


def _parse_coverage_output(output: str) -> tuple[str, list[tuple[str, str]]]:
    """Parses the terminal output of pytest with --cov flags.

    Args:
        output (str): Raw stdout from pytest with --cov=src --cov-report=term-missing.

    Returns:
        tuple[str, list[tuple[str, str]]]: A (total_pct, below_100) pair where
            total_pct is the overall coverage percentage string and below_100 is a
            list of (module_name, coverage_pct) tuples for modules below 100%.
    """
    total_pct = "N/A"
    below_100: list[tuple[str, str]] = []

    row_pattern = re.compile(r"^(\S.+?)\s{2,}\d+\s+\d+\s+(\d+%)")

    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("TOTAL"):
            m = re.search(r"(\d+%)", stripped)
            if m:
                total_pct = m.group(1)
        else:
            m = row_pattern.match(stripped)
            if m:
                name = m.group(1).strip()
                pct = m.group(2)
                if pct != "100%":
                    below_100.append((name, pct))

    return total_pct, below_100


def format_coverage(
    raw_output: str, output_format: CoverageFormats = CoverageFormats.TERMINAL
) -> str:
    """Formats a pytest-cov terminal output into a human-readable coverage report.

    Args:
        raw_output (str): Raw stdout from pytest with --cov=src --cov-report=term-missing.
        output_format (CoverageFormats): The output format for the coverage report.

    Returns:
        str: A formatted coverage report.
    """
    total_pct, below_100 = _parse_coverage_output(raw_output)

    if output_format == CoverageFormats.MARKDOWN:
        return _format_markdown(total_pct, below_100)
    return _format_terminal(total_pct, below_100)


def _format_terminal(total_pct: str, below_100: list[tuple[str, str]]) -> str:
    lines = ["Coverage Report", "===============", "", f"Overall coverage: {total_pct}"]
    if below_100:
        lines += ["", "Modules below 100%:"]
        for name, pct in below_100:
            lines.append(f"  {name}  {pct}")
    return "\n".join(lines)


def _format_markdown(total_pct: str, below_100: list[tuple[str, str]]) -> str:
    lines = ["# Coverage Report", "", f"**Overall coverage: {total_pct}**"]
    if below_100:
        lines += [
            "",
            "## Modules below 100%",
            "",
            "| Module | Coverage |",
            "|--------|----------|",
        ]
        for name, pct in below_100:
            lines.append(f"| {name} | {pct} |")
    return "\n".join(lines)
