"""Format reports as text for the terminal and as Markdown for the build artifact."""

from __future__ import annotations

from design_review.domain.findings import Report
from design_review.domain.fitness import FitnessReport


def render_text(report: Report) -> str:
    """One line per finding, then the verdict."""
    lines = [
        f"{finding.severity.value.upper():7} {finding.code} {finding.subject}: {finding.message}"
        for finding in report.findings
    ]
    counts = f"{len(report.subjects)} documents checked, {len(report.errors)} errors, {len(report.warnings)} warnings"
    lines.append(f"{'OK' if report.ok else 'FAILED'}: {counts}")
    return "\n".join(lines)


def render_fitness(report: FitnessReport) -> str:
    """The fitness table: each scenario, what it measured, and whether it matched the review's expectation."""
    lines = ["thumbnails (95% of uploads within the target; capacity must also cover the average rate)"]
    for item in report.thumbnails:
        verdict = "PASS" if item.passed else "FAIL"
        match = "as expected" if item.as_expected else "UNEXPECTED"
        lines.append(
            f"  {item.scenario.name:8} {item.scenario.workers:3} workers  capacity {item.capacity:5.1f}/s  "
            f"average {item.average_rate:4.2f}/s  peak needs {item.workers_for_peak} workers  "
            f"wait at p{item.percentile:g} {item.wait_at_percentile:8.1f} s  {verdict}  ({match})"
        )
    lines.append("write order (a crash at any point must not lose an upload the seller was told about)")
    for verdict_item in report.durability:
        verdict = "PASS" if verdict_item.result.holds else "FAIL"
        match = "as expected" if verdict_item.as_expected else "UNEXPECTED"
        lines.append(
            f"  {verdict_item.scenario.name:8} {' > '.join(verdict_item.scenario.order)}  {verdict}  ({match})"
        )
        lines.extend(f"      lost: {violation}" for violation in verdict_item.result.violations)
        lines.extend(f"      orphan: {orphan}" for orphan in verdict_item.result.orphans)
    lines.append(
        "OK: every scenario gave the verdict the review expected"
        if report.ok
        else "FAILED: a scenario surprised the review"
    )
    return "\n".join(lines)


def render_markdown(report: Report, fitness: FitnessReport) -> str:
    """The report the CI run uploads: document findings, then the fitness functions."""
    verdict = "OK" if report.ok and fitness.ok else "FAILED"
    lines = [
        "# Design review report",
        "",
        f"**Verdict:** {verdict}",
        "",
        "## Documents checked",
        "",
        *[f"- `{subject}`" for subject in report.subjects],
        "",
        "## Findings",
        "",
    ]
    if report.findings:
        lines += ["| Severity | Code | Document | Message |", "| --- | --- | --- | --- |"]
        lines += [f"| {f.severity.value} | {f.code} | `{f.subject}` | {f.message} |" for f in report.findings]
    else:
        lines.append("None.")
    lines += ["", "## Fitness functions", "", "```text", render_fitness(fitness), "```", ""]
    return "\n".join(lines)
