import argparse
import sys
from pathlib import Path

import pandas as pd

DEFAULT_SHEET = "Requests"
DEFAULT_TYPE = "Demand Planning"
DEFAULT_TITLE_COL = "User Story"
DEFAULT_COLUMNS = [
    "User Story",
    "Objective and key results",
    "People and responsabilities",
    "Status",
    "Request date",
    "Wanted date",
    "Priority",
    "Observations",
]


def format_value(value) -> str:
    if pd.isna(value):
        return "N/A"
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y.%m.%d")
    return str(value).strip() or "N/A"


def load_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {file_path}")
    except ValueError:
        try:
            xl = pd.ExcelFile(file_path)
            available = ", ".join(xl.sheet_names)
        except Exception:
            available = "unknown"
        sys.exit(f"Error: sheet '{sheet_name}' not found. Available sheets: {available}")
    return df


def validate_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        available = ", ".join(df.columns.tolist())
        sys.exit(
            f"Error: column(s) not found in sheet: {', '.join(missing)}\n"
            f"Available columns: {available}"
        )


def build_markdown(
    df: pd.DataFrame, filename: str, type_label: str, title_col: str, columns: list[str]
) -> str:
    sub_cols = [c for c in columns if c != title_col]
    lines = [f"# {filename}", "", "---", "", f"## {type_label}", "", "---", ""]

    for _, row in df.iterrows():
        title_value = format_value(row[title_col])
        lines.append(f"### {title_value}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for col in sub_cols:
            lines.append(f"#### {col}")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append(format_value(row[col]))
            lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an Excel sheet to a structured Markdown file."
    )
    parser.add_argument("file", type=Path, help="Path to the Excel file")
    parser.add_argument("--sheet", default=DEFAULT_SHEET, help='Sheet name (default: "Requests")')
    parser.add_argument(
        "--type",
        default=DEFAULT_TYPE,
        help='Label used as the ## grouping heading (default: "Demand Planning")',
    )
    parser.add_argument(
        "--title-col",
        default=DEFAULT_TITLE_COL,
        help='Column used as ### heading per row (default: "User Story")',
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        default=DEFAULT_COLUMNS,
        metavar="COL",
        help="Ordered list of columns to include (default: the 8 standard columns)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output .md file path (default: same location as input with .md extension)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_path = args.output or args.file.with_suffix(".md")

    df = load_sheet(args.file, args.sheet)

    all_cols = args.columns if args.title_col in args.columns else [args.title_col] + args.columns
    validate_columns(df, all_cols)

    markdown = build_markdown(df, args.file.stem, args.type, args.title_col, all_cols)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Written: {output_path}")


if __name__ == "__main__":
    main()
