"""Print mechanical conformance facts for New-Prep stage files.

This is governance tooling, not curriculum content. It compares 00-MAP.md rows
with stage-file headings and prints a Markdown table for the section-8 ledger
and review baseline.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Sequence, TypedDict


ROOT = Path(__file__).resolve().parent
MAP = ROOT / "00-MAP.md"
STAGE_RE = re.compile(r"^(0[1-7]-Stage.*\.md)$")
STAGE_SECTION_RE = re.compile(r"^### Stage \d+ .*`([^`]+\.md)`")
STATUS_RE = re.compile(r"^\*\*Rules status:\*\*\s*(.+?)\s*$", re.MULTILINE)
C_HEADING_RE = re.compile(r"^## (C\d\..*)$", re.MULTILINE)
WHERE_RE = re.compile(r"\*\*Where we are:\*\*", re.IGNORECASE)
LABEL_RE = {
    "verify": re.compile(r"`verify`"),
    "typical": re.compile(r"`typical`"),
    "documented default": re.compile(r"`documented default`"),
    "example": re.compile(r"`example`"),
}
EXAMPLE_BLOCK_RE = re.compile(
    r"(?im)^\s*(?:#{2,6}\s+.*\bexample\b.*|[-*]?\s*\*\*.*\bexample\b.*\*\*)"
)
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
TOPIC_HEADING_RE = re.compile(r"^(#{2,3})\s+(\d+\.\d+(?:\.\d+)*)\b(.*)$", re.MULTILINE)
DIAMOND = "\u25c7"
LEGACY_STATUS = "legacy v1 shape, migration debt tracked in \u00a78"

LEGAL_STATUS = {
    "v2.0 reference",
    "v2.0 migrated",
    LEGACY_STATUS,
}


class TopicMeta(TypedDict):
    plus: bool
    diamond: bool
    tier: str


def stage_files() -> list[Path]:
    return sorted(p for p in ROOT.glob("0*-Stage*.md") if STAGE_RE.match(p.name))


def parse_map_stage_rows() -> dict[str, dict[str, TopicMeta]]:
    text = MAP.read_text(encoding="utf-8")
    rows_by_file: dict[str, dict[str, TopicMeta]] = {}
    current_file: str | None = None

    for line in text.splitlines():
        section_match = STAGE_SECTION_RE.match(line)
        if section_match:
            current_file = section_match.group(1)
            rows_by_file.setdefault(current_file, {})
            continue

        if current_file is None:
            continue
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        raw_topic, raw_tier = cells[0], cells[2]
        topic_match = re.search(r"(\d+\.\d+(?:\.\d+)*)", raw_topic)
        if not topic_match:
            continue
        topic = topic_match.group(1)
        rows_by_file[current_file][topic] = {
            "plus": "+" in raw_topic,
            "diamond": DIAMOND in raw_topic,
            "tier": re.sub(r"[*`\[\]]", "", raw_tier).strip(),
        }

    return rows_by_file


def topic_heading_index(text: str) -> dict[str, str]:
    headings: dict[str, str] = {}
    for match in TOPIC_HEADING_RE.finditer(text):
        topic = match.group(2)
        headings[topic] = match.group(3)
    return headings


def topic_sort_key(topic: str) -> tuple[int, ...]:
    return tuple(int(part) for part in topic.split("."))


def covered_by_map_topic(topic: str, map_rows: dict[str, TopicMeta]) -> bool:
    parts = topic.split(".")
    return any(".".join(parts[:i]) in map_rows for i in range(len(parts), 1, -1))


def example_table_header_count(text: str) -> int:
    lines = text.splitlines()
    count = 0
    for index, line in enumerate(lines[:-1]):
        if "|" not in line or not re.search(r"\bexample\b", line, re.IGNORECASE):
            continue
        if TABLE_SEPARATOR_RE.match(lines[index + 1]):
            count += 1
    return count


def label_counts(text: str) -> dict[str, int]:
    counts = {name: len(pattern.findall(text)) for name, pattern in LABEL_RE.items()}
    counts["example"] += len(EXAMPLE_BLOCK_RE.findall(text)) + example_table_header_count(text)
    return counts


def mismatches(text: str, map_rows: dict[str, TopicMeta]) -> list[str]:
    headings = topic_heading_index(text)
    problems: list[str] = []

    for topic in sorted(map_rows, key=topic_sort_key):
        meta = map_rows[topic]
        heading_tail = headings.get(topic)
        if heading_tail is None:
            if not meta["diamond"]:
                problems.append(f"{topic}: map topic absent from file")
            continue
        if meta["diamond"]:
            problems.append(f"{topic}: map marks \u25c7 not drafted, but file has a heading")
        if meta["plus"] and "`+`" not in heading_tail:
            problems.append(f"{topic}: map has +, heading missing `+`")
        if not meta["diamond"] and meta["tier"] and meta["tier"] not in heading_tail:
            problems.append(f"{topic}: heading missing tier {meta['tier']}")

    for topic in sorted(headings, key=topic_sort_key):
        if not covered_by_map_topic(topic, map_rows):
            problems.append(f"{topic}: file heading not present in this stage's map row")

    return problems


def tracked_legacy_issue(issue: str) -> bool:
    return "heading missing tier" in issue


def row_should_fail(status: str, status_valid: bool, issues: list[str], strict: bool) -> bool:
    if not status_valid:
        return True
    if strict:
        return bool(issues)
    if status != LEGACY_STATUS:
        return bool(issues)
    return any(not tracked_legacy_issue(issue) for issue in issues)


def build_report(strict: bool = False) -> tuple[int, str]:
    rows_by_file = parse_map_stage_rows()
    rc = 0
    lines: list[str] = []

    lines.append(
        "| File | Rules status | C headings | Where we are | verify labels | "
        "typical labels | default labels | example markers | Heading sync issues |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---|")
    for path in stage_files():
        text = path.read_text(encoding="utf-8")
        status_match = STATUS_RE.search(text)
        raw_status = status_match.group(1).strip() if status_match else "MISSING"
        status_valid = raw_status in LEGAL_STATUS
        status = raw_status if status_valid else f"{raw_status} (INVALID)"
        c_headings = ", ".join(h.split()[0] for h in C_HEADING_RE.findall(text)) or "none"
        where_count = len(WHERE_RE.findall(text))
        counts = label_counts(text)
        map_rows = rows_by_file.get(path.name, {})
        issues = mismatches(text, map_rows) if map_rows else ["no stage rows found in 00-MAP.md"]
        if row_should_fail(raw_status, status_valid, issues, strict):
            rc = 1
        issue_text = "<br>".join(issues[:8])
        if len(issues) > 8:
            issue_text += f"<br>... {len(issues) - 8} more"
        lines.append(
            f"| `{path.name}` | {status} | {c_headings} | {where_count} | "
            f"{counts['verify']} | {counts['typical']} | {counts['documented default']} | "
            f"{counts['example']} | {issue_text or 'ok'} |"
        )
    return rc, "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    output_path: Path | None = None
    strict = False

    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--strict":
            strict = True
            index += 1
        elif arg == "--output" and index + 1 < len(argv):
            output_path = Path(argv[index + 1])
            index += 2
        else:
            print("Usage: python stage_conformance_check.py [--strict] [--output PATH]", file=sys.stderr)
            return 2

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    rc, report = build_report(strict=strict)
    if output_path:
        output_path.write_text(report, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(report)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
