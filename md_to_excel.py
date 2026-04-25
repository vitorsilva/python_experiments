import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

DEFAULT_SHEET = "Requests"
DEFAULT_TITLE_COL = "User Story"


def try_parse_value(value: str):
    try:
        return datetime.strptime(value, "%Y.%m.%d").date()
    except ValueError:
        pass
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_markdown(text: str, title_col: str, prefix: str) -> pd.DataFrame:
    rows = []
    col_order = []
    current_row = None
    current_col = None
    content_lines = []

    def strip_prefix(s: str) -> str:
        return s[len(prefix):] if prefix and s.startswith(prefix) else s

    def flush_cell():
        nonlocal current_col, content_lines
        if current_row is not None and current_col is not None:
            raw = "\n".join(content_lines).strip()
            current_row[current_col] = None if raw == "N/A" else try_parse_value(raw)
        current_col = None
        content_lines = []

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#### "):
            flush_cell()
            col_name = strip_prefix(s[5:])
            current_col = col_name
            if col_name not in col_order:
                col_order.append(col_name)
        elif s.startswith("### "):
            flush_cell()
            if current_row is not None:
                rows.append(current_row)
            heading = strip_prefix(s[4:])
            current_row = {title_col: None if heading == "N/A" else try_parse_value(heading)}
        elif s.startswith("#"):
            pass
        elif s == "---":
            flush_cell()
        elif s and current_col is not None:
            content_lines.append(s)

    flush_cell()
    if current_row is not None:
        rows.append(current_row)

    ordered_cols = [title_col] + [c for c in col_order if c != title_col]
    return pd.DataFrame(rows, columns=ordered_cols)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Round-trip a structured Markdown file back to Excel."
    )
    parser.add_argument("file", type=Path, help="Path to the Markdown file")
    parser.add_argument(
        "--sheet",
        default=DEFAULT_SHEET,
        help='Sheet name in the output Excel file (default: "Requests")',
    )
    parser.add_argument(
        "--title-col",
        default=DEFAULT_TITLE_COL,
        help='Column name that ### headings map to (default: "User Story")',
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Prefix used in excel_to_md.py that should be stripped from headings (default: none)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output .xlsx path (default: same location as input with .xlsx extension)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.file.exists():
        sys.exit(f"Error: file not found: {args.file}")

    output_path = args.output or args.file.with_suffix(".xlsx")

    text = args.file.read_text(encoding="utf-8")
    df = parse_markdown(text, args.title_col, args.prefix)

    if df.empty:
        sys.exit(
            "Error: no rows found in markdown. "
            "Check that --title-col and --prefix match those used in excel_to_md.py."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, sheet_name=args.sheet, index=False)
    print(f"Written: {output_path} ({len(df)} rows, {len(df.columns)} columns)")


if __name__ == "__main__":
    main()
