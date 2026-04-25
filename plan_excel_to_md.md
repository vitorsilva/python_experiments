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
  --title TEXT          Text used as the # document heading (default: filename without extension)
  --type TEXT           Label used as the ## grouping heading (default: "Demand Planning")
  --title-col TEXT      Column used as the ### heading per row (default: "User Story")
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

---

## <type>

---

### <title-col value for row 1>

---

#### Objective and key results

---

...content...

#### Status

---

...content...

### <title-col value for row 2>

---

#### Objective and key results

---

...
```

- Top-level `#` heading: value from `--title` (default: input filename without extension)
- `##` heading: fixed label from `--type` (default: "Demand Planning"), emitted once
- `###` heading: one per row, value from `--title-col`
- `####` heading: one per remaining column (title column excluded)
- A `---` horizontal rule follows every heading at every level (`#`, `##`, `###`, `####`)
- Sub-section order follows the order columns are defined in `--columns`
- Empty/blank cells rendered as `N/A`
- The title column (`--title-col`) does NOT appear as a `####` sub-section

## Logic / Implementation Steps

1. Parse CLI arguments; apply defaults
2. Load the specified sheet from the Excel file using pandas
3. Validate that all requested columns exist in the sheet; exit with a clear error if not
4. Exclude the title column from the sub-section columns list
5. Emit `# <title>` (falls back to filename stem if `--title` not provided) then `---`
6. Emit `## <type>` then `---`
7. For each row:
   a. Emit `### <title-col value>` (or `### N/A` if blank) then `---`
   b. For each remaining column (in specified order):
      - Emit `#### <column name>` then `---`
      - Emit the cell value; format datetime values as `yyyy.mm.dd`; blanks as `N/A`
8. Write the full markdown string to the output file

## Date Handling
- Auto-detect datetime columns via pandas dtype (no manual flagging needed)
- Format: `yyyy.mm.dd` (e.g. `2024.03.15`)

## Error Handling
- File not found: clear error message, exit
- Sheet not found: clear error message listing available sheets, exit
- Column not found: clear error message listing available columns, exit

## Example Calls

Default run (all 8 columns, sheet "Requests", type "Demand Planning", title col "User Story", # heading = filename):
```bash
python excel_to_md.py data/requests.xlsx
# → writes data/requests.md
```

Custom document title:
```bash
python excel_to_md.py data/requests.xlsx --title "Q1 2024 Requests"
```

Different sheet:
```bash
python excel_to_md.py data/requests.xlsx --sheet "Q2 Requests"
```

Custom type label:
```bash
python excel_to_md.py data/requests.xlsx --type "Supply Planning"
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
  --title "Q1 2024 Requests" \
  --type "Demand Planning" \
  --title-col "User Story" \
  --columns "User Story" "Objective and key results" "People and responsabilities" "Status" "Request date" "Wanted date" "Priority" "Observations" \
  --output output/report.md
```

## Validation Checklist
- [ ] `##` type label emitted once, value from `--type` (default: "Demand Planning")
- [ ] One `###` section per row, using the title column value
- [ ] Title column used as `###` heading, excluded from `####` sub-sections
- [ ] Sub-sections (`####`) follow `--columns` order
- [ ] Empty cells render as `N/A`
- [ ] Datetime columns formatted as `yyyy.mm.dd`
- [ ] Top-level `#` heading uses `--title` value, falling back to filename without extension
- [ ] Output file defaults to same directory and name as input with `.md` extension
- [ ] Missing file / sheet / column produces a clear error message
- [ ] A `---` horizontal rule follows every heading at every level (`#`, `##`, `###`, `####`)
