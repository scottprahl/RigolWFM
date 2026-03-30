#!/usr/bin/env python3

"""Render Kaitai Struct `.ksy` schemas as Markdown or reStructuredText tables."""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit("PyYAML is required to read `.ksy` files. Install it in the active environment first.") from exc


def _compact_text(value: Any) -> str:
    """Collapse nested values into a readable one-line string."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ", ".join(part for item in value if (part := _compact_text(item)))
    if isinstance(value, dict):
        return ", ".join(f"{key}={_compact_text(item)}" for key, item in value.items())
    return re.sub(r"\s+", " ", str(value).strip())


def _heading(text: str, level: int, fmt: str) -> str:
    """Render a Markdown or reStructuredText heading."""
    if fmt == "markdown":
        return f"{'#' * level} {text}"

    adornments = {1: "=", 2: "-", 3: "~"}
    underline = adornments.get(level, "^") * len(text)
    return f"{text}\n{underline}"


def _markdown_cell(value: str) -> str:
    """Escape a Markdown table cell."""
    return value.replace("|", r"\|")


def _rst_cell(value: str) -> str:
    """Escape a reStructuredText grid-table cell."""
    return value.replace("|", r"\|")


def _wrap_lines(value: str, header: str) -> list[str]:
    """Wrap a table cell to a readable width."""
    max_widths = {
        "Key": 24,
        "Value": 64,
        "Field": 28,
        "Instance": 28,
        "Type": 24,
        "Details": 44,
        "Description": 72,
        "Name": 28,
    }
    width = max_widths.get(header, 60)
    return textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def _render_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a pipe table for Markdown."""
    lines = [
        "| " + " | ".join(_markdown_cell(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        wrapped = ["<br>".join(_wrap_lines(cell, headers[idx])) for idx, cell in enumerate(row)]
        lines.append("| " + " | ".join(_markdown_cell(cell) for cell in wrapped) + " |")
    return "\n".join(lines)


def _render_rst_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a grid table for reStructuredText."""
    wrapped_headers = [[header] for header in headers]
    wrapped_rows = [[_wrap_lines(cell, headers[idx]) for idx, cell in enumerate(row)] for row in rows]

    widths = [
        max(
            len(_rst_cell(cell))
            for group in [wrapped_headers[idx], *(row[idx] for row in wrapped_rows)]
            for cell in group
        )
        for idx, header in enumerate(headers)
    ]

    def border(char: str) -> str:
        return "+" + "+".join(char * (width + 2) for width in widths) + "+"

    def render_row(row_lines: list[list[str]]) -> list[str]:
        height = max(len(lines) for lines in row_lines)
        rendered: list[str] = []
        for line_index in range(height):
            cells = []
            for idx, lines in enumerate(row_lines):
                line = lines[line_index] if line_index < len(lines) else ""
                cells.append(f" {_rst_cell(line).ljust(widths[idx])} ")
            rendered.append("|" + "|".join(cells) + "|")
        return rendered

    lines = [border("-"), *render_row(wrapped_headers), border("=")]
    for row in wrapped_rows:
        lines.extend([*render_row(row), border("-")])
    return "\n".join(lines)


def _render_table(headers: list[str], rows: list[list[str]], fmt: str) -> str:
    """Render a table in the requested output format."""
    if not rows:
        return ""
    if fmt == "markdown":
        return _render_markdown_table(headers, rows)
    return _render_rst_table(headers, rows)


def _entry_type(entry: dict[str, Any], *, default: str = "") -> str:
    """Return a readable type string for a seq/param/instance entry."""
    if "type" in entry:
        return _compact_text(entry["type"])
    if "contents" in entry:
        return "literal"
    if "size" in entry or entry.get("size-eos"):
        return "bytes"
    if "value" in entry:
        return "computed"
    return default


def _entry_details(entry: dict[str, Any], keys: list[str]) -> str:
    """Collect non-type details into a compact summary string."""
    details: list[str] = []
    for key in keys:
        if key not in entry:
            continue
        value = entry[key]
        if key == "size-eos" and value is True:
            details.append("size=eos")
        elif isinstance(value, bool):
            details.append(f"{key}={'true' if value else 'false'}")
        else:
            details.append(f"{key}={_compact_text(value)}")
    return "; ".join(details)


def _field_rows(entries: list[dict[str, Any]]) -> list[list[str]]:
    """Build table rows for seq and params entries."""
    rows: list[list[str]] = []
    for entry in entries:
        rows.append(
            [
                _compact_text(entry.get("id")),
                _entry_type(entry, default="bytes"),
                _entry_details(
                    entry,
                    [
                        "contents",
                        "size",
                        "size-eos",
                        "enum",
                        "encoding",
                        "terminator",
                        "repeat",
                        "repeat-expr",
                        "repeat-until",
                        "if",
                        "pos",
                        "process",
                    ],
                ),
                _compact_text(entry.get("doc")),
            ]
        )
    return rows


def _instance_rows(instances: dict[str, dict[str, Any]]) -> list[list[str]]:
    """Build table rows for instances."""
    rows: list[list[str]] = []
    for name, entry in instances.items():
        rows.append(
            [
                name,
                _entry_type(entry, default="computed"),
                _entry_details(
                    entry,
                    ["value", "pos", "size", "size-eos", "repeat", "repeat-expr", "repeat-until", "if"],
                ),
                _compact_text(entry.get("doc")),
            ]
        )
    return rows


def _enum_rows(entries: dict[Any, Any]) -> list[list[str]]:
    """Build table rows for enum members."""
    return [[_compact_text(value), _compact_text(name)] for value, name in entries.items()]


def _append_section(parts: list[str], title: str, level: int, body: str, fmt: str, description: str = "") -> None:
    """Append a heading and optional description for a non-empty body."""
    if not body:
        return
    parts.append(_heading(title, level, fmt))
    if description:
        parts.append(description)
    parts.append(body)


def render_schema(schema: dict[str, Any], source: Path, fmt: str) -> str:
    """Render an already-loaded schema to Markdown or reStructuredText."""
    meta = schema.get("meta", {})
    title = _compact_text(meta.get("title") or meta.get("id") or source.name)

    parts = [_heading(title, 1, fmt)]
    source_markup = f"`{source}`" if fmt == "markdown" else f"``{source}``"
    parts.append(f"Source: {source_markup}")

    schema_doc = _compact_text(schema.get("doc"))
    if schema_doc:
        parts.append(schema_doc)

    metadata_rows = [[_compact_text(key), _compact_text(value)] for key, value in meta.items()]
    _append_section(parts, "Metadata", 2, _render_table(["Key", "Value"], metadata_rows, fmt), fmt)

    params = schema.get("params", [])
    _append_section(
        parts,
        "Parameters",
        2,
        _render_table(["Field", "Type", "Details", "Description"], _field_rows(params), fmt),
        fmt,
    )

    seq = schema.get("seq", [])
    _append_section(
        parts,
        "Top-Level Sequence",
        2,
        _render_table(["Field", "Type", "Details", "Description"], _field_rows(seq), fmt),
        fmt,
    )

    instances = schema.get("instances", {})
    _append_section(
        parts,
        "Top-Level Instances",
        2,
        _render_table(["Instance", "Type", "Details", "Description"], _instance_rows(instances), fmt),
        fmt,
    )

    for type_name, type_def in schema.get("types", {}).items():
        parts.append(_heading(f"Type: {type_name}", 2, fmt))
        type_doc = _compact_text(type_def.get("doc"))
        if type_doc:
            parts.append(type_doc)
        _append_section(
            parts,
            "Parameters",
            3,
            _render_table(["Field", "Type", "Details", "Description"], _field_rows(type_def.get("params", [])), fmt),
            fmt,
        )
        _append_section(
            parts,
            "Sequence",
            3,
            _render_table(["Field", "Type", "Details", "Description"], _field_rows(type_def.get("seq", [])), fmt),
            fmt,
        )
        _append_section(
            parts,
            "Instances",
            3,
            _render_table(
                ["Instance", "Type", "Details", "Description"],
                _instance_rows(type_def.get("instances", {})),
                fmt,
            ),
            fmt,
        )

    for enum_name, enum_values in schema.get("enums", {}).items():
        _append_section(
            parts,
            f"Enum: {enum_name}",
            2,
            _render_table(["Value", "Name"], _enum_rows(enum_values), fmt),
            fmt,
        )

    return "\n\n".join(parts) + "\n"


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path, help="Path to the `.ksy` file to summarize.")
    parser.add_argument(
        "--format",
        choices=("markdown", "rst"),
        default="markdown",
        help="Output format for the generated tables.",
    )
    parser.add_argument("-o", "--output", type=Path, help="Optional output file. Defaults to standard output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    args = build_parser().parse_args(argv)
    schema_path = args.schema

    with schema_path.open("r", encoding="utf-8") as infile:
        schema = yaml.safe_load(infile)

    if not isinstance(schema, dict):
        raise SystemExit(f"{schema_path} does not contain a top-level YAML mapping.")

    rendered = render_schema(schema, schema_path, args.format)
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
