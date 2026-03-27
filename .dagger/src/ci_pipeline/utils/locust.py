"""Utilities for processing locust test results and generating comparison reports."""

import csv
import io
from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import override


def _parse_locust_csv(csv_text: str) -> dict[str, str]:
    """Extracts the Aggregated row from a locust stats CSV string.

    Args:
        csv_text (str): Content of a locust *_stats.csv file.

    Returns:
        dict[str, str]: The aggregated row as a dict, or empty dict if not found.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        if row.get("Name") == "Aggregated":
            return dict(row)
    return {}


class IResultFormatter(ABC):
    """Interface for formatting locust test results."""

    @property
    @abstractmethod
    def header(self) -> str:
        """Returns the header string for the comparison table."""

    @property
    @abstractmethod
    def separator(self) -> str:
        """Returns the separator string for the comparison table."""

    @abstractmethod
    def row(
        self, label: str, current_value: str | None, baseline_value: str | None
    ) -> str:
        """Formats a single row of the comparison table."""


class TerminalResultFormatter(IResultFormatter):
    """Formats locust test results for terminal output."""

    cw: int
    vw: int

    def __init__(self, baseline_tag: str, cw: int = 20, vw: int = 16) -> None:
        """Creates a TerminalResultFormatter instance.

        Args:
            baseline_tag (str): The tag of the baseline image
                to include in the header.
            cw (int): Column width for the metric label column.
            vw (int): Column width for the value columns.
        """
        self.baseline_tag = baseline_tag
        self.cw = cw
        self.vw = vw

    @property
    @override
    def header(self) -> str:
        return (
            f"{'Metric':<{self.cw}} "
            f"| {'Current':>{self.vw}} "
            f"| {f'Baseline ({self.baseline_tag})':>{self.vw}}"
        )

    @property
    @override
    def separator(self) -> str:
        return "-" * len(self.header)

    @override
    def row(
        self, label: str, current_value: str | None, baseline_value: str | None
    ) -> str:
        def fmt(val: str | None) -> str:
            try:
                return f"{float(val):.1f}"  # type: ignore[arg-type]
            except (ValueError, TypeError):
                return "N/A"

        return (
            f"{label:<{self.cw}} "
            f"| {fmt(current_value):>{self.vw}} "
            f"| {fmt(baseline_value):>{self.vw}}"
        )


class MarkdownResultFormatter(IResultFormatter):
    """Formats locust test results for Markdown output."""

    def __init__(self, baseline_tag: str) -> None:
        """Creates a MarkdownResultFormatter instance.

        Args:
            baseline_tag (str): The tag of the baseline image
                to include in the header.
        """
        self.baseline_tag = baseline_tag

    @property
    @override
    def header(self) -> str:
        return f"| Metric | Current | Baseline ({self.baseline_tag}) |"

    @property
    @override
    def separator(self) -> str:
        return "|-|-:|-:|"

    @override
    def row(
        self, label: str, current_value: str | None, baseline_value: str | None
    ) -> str:
        def fmt(val: str | None) -> str:
            try:
                return f"{float(val):.1f}"  # type: ignore[arg-type]
            except (ValueError, TypeError):
                return "N/A"

        return f"| {label} | {fmt(current_value)} | {fmt(baseline_value)} |"


class OutputFormats(StrEnum):
    """Supported output formats of the performance comparison report."""

    TERMINAL = auto()
    MARKDOWN = auto()


def format_comparison(
    current_csv: str,
    baseline_csv: str,
    baseline_image: str,
    scenario_name: str,
    output_format: OutputFormats = OutputFormats.TERMINAL,
) -> str:
    """Formats a human-readable performance comparison from two locust CSV outputs.

    Args:
        current_csv (str): Locust stats CSV for the current branch.
        baseline_csv (str): Locust stats CSV for the baseline image.
        baseline_image (str): The baseline image identifier (used in the header).
        scenario_name (str): Scenario name to include in the output.
        output_format (Formats): The output format for the comparison table.

    Returns:
        str: A formatted comparison table.
    """
    current = _parse_locust_csv(current_csv)
    baseline = _parse_locust_csv(baseline_csv)
    baseline_tag = baseline_image.rsplit(":", maxsplit=1)[-1]

    if output_format == OutputFormats.MARKDOWN:
        formatter = MarkdownResultFormatter(baseline_tag)
    else:
        formatter = TerminalResultFormatter(baseline_tag, 20, 16)

    lines = [
        f"## Scenario: {scenario_name}",
        "",
        formatter.header,
        formatter.separator,
        formatter.row("p50 latency (ms)", current.get("50%"), baseline.get("50%")),
        formatter.row("p95 latency (ms)", current.get("95%"), baseline.get("95%")),
        formatter.row("p99 latency (ms)", current.get("99%"), baseline.get("99%")),
        formatter.row(
            "Requests/s", current.get("Requests/s"), baseline.get("Requests/s")
        ),
        formatter.row(
            "Failures",
            current.get("Failure Count", "N/A"),
            baseline.get("Failure Count", "N/A"),
        ),
    ]
    return "\n".join(lines)
