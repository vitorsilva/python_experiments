# Plan: excel_to_md.py

## Purpose
Load an Excel file, extract specified columns from a given sheet, and generate a structured Markdown file from the data.

## Dependencies
- `pandas` — data loading and manipulation
- `openpyxl` — Excel backend for pandas
- `argparse` — CLI interface (stdlib)

## CLI Interface

```
python excel_to_md.py <file> [options]

positional:
  file                  Path to the Excel file

options:
  --sheet TEXT          Sheet name to read (default: "Requests")
  --title-col TEXT      Column used as the ## heading per row (default: "User Story")
  --columns TEXT [...]  Ordered list of columns to include (default: the 8 agreed columns)
  --output FILE         Output .md file path (default: same dir/name as input, .md extension)
```

### Default Columns (in order)
1. User Story
2. Objective and key results
3. People and responsabilities
4. Status
5. Request date
6. Wanted date
7. Priority
8. Observations

## Markdown Output Structure

```markdown
# filename_without_extension

## <title-col value for row 1>
### Objective and key results
...content...
### Status
...content...

## <title-col value for row 2>
### Objective and key results
...
```

- Top-level `#` heading: input filename without extension
- One `##` section per row, using the value from `--title-col`
- One `###` sub-section per remaining column (title column excluded)
- Sub-section order follows the order columns are defined in `--columns`
- Empty/blank cells rendered as `N/A`
- The title column (`--title-col`) does NOT appear as a `###` sub-section

## Logic / Implementation Steps

1. Parse CLI arguments; apply defaults
2. Load the specified sheet from the Excel file using pandas
3. Validate that all requested columns exist in the sheet; exit with a clear error if not
4. Exclude the title column from the sub-section columns list
5. For each row:
   a. Emit `## <title-col value>` (or `## N/A` if blank)
   b. For each remaining column (in specified order):
      - Emit `### <column name>`
      - Emit the cell value; format datetime values as `yyyy.mm.dd`; blanks as `N/A`
6. Write the full markdown string to the output file

## Date Handling
- Auto-detect datetime columns via pandas dtype (no manual flagging needed)
- Format: `yyyy.mm.dd` (e.g. `2024.03.15`)

## Error Handling
- File not found: clear error message, exit
- Sheet not found: clear error message listing available sheets, exit
- Column not found: clear error message listing available columns, exit

## Example Calls

Default run (all 8 columns, sheet "Requests", title "User Story"):
```bash
python excel_to_md.py data/requests.xlsx
# → writes data/requests.md
```

Different sheet:
```bash
python excel_to_md.py data/requests.xlsx --sheet "Q2 Requests"
```

Custom title column:
```bash
python excel_to_md.py data/requests.xlsx --title-col "Objective and key results"
```

Subset of columns in a specific order:
```bash
python excel_to_md.py data/requests.xlsx --columns "User Story" "Status" "Priority" "Observations"
```

Full explicit call:
```bash
python excel_to_md.py data/requests.xlsx \
  --sheet "Requests" \
  --title-col "User Story" \
  --columns "User Story" "Objective and key results" "People and responsabilities" "Status" "Request date" "Wanted date" "Priority" "Observations" \
  --output output/report.md
```

## Validation Checklist
- [ ] One `##` section per row
- [ ] Title column used as `##` heading, excluded from `###` sub-sections
- [ ] Sub-sections follow `--columns` order
- [ ] Empty cells render as `N/A`
- [ ] Datetime columns formatted as `yyyy.mm.dd`
- [ ] Top-level `#` heading is the input filename without extension
- [ ] Output file defaults to same directory and name as input with `.md` extension
- [ ] Missing file / sheet / column produces a clear error message
