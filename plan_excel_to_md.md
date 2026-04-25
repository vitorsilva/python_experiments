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
  --prefix TEXT         String prepended to every heading value at all levels (default: "")
  --filter-col TEXT     Column used to filter rows (default: "Status")
  --exclude TEXT [...]  Values in filter-col that cause a row to be skipped,
                        case-insensitive (default: "cancelled" "close")
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
- `--prefix` string is prepended directly to every heading value at all levels (default: `""`)
- A `---` horizontal rule follows every heading at every level (`#`, `##`, `###`, `####`)
- Sub-section order follows the order columns are defined in `--columns`
- Empty/blank cells rendered as `N/A`
- The title column (`--title-col`) does NOT appear as a `####` sub-section

## Row Filtering

- Controlled by `--filter-col` (default: `"Status"`) and `--exclude` (default: `"cancelled" "close"`)
- Rows where the filter column value matches any excluded value are dropped before output
- Matching is **case-insensitive** and trims surrounding whitespace
- The filter column does **not** need to appear in `--columns`; it is used solely for filtering
- If the filter column is not found in the sheet a warning is printed to stderr and filtering is skipped

## Logic / Implementation Steps

1. Parse CLI arguments; apply defaults
2. Load the specified sheet from the Excel file using pandas
3. Validate that all requested columns exist in the sheet; exit with a clear error if not
4. If `--filter-col` exists in the sheet, drop rows whose filter-col value (case-insensitive) matches any value in `--exclude`; otherwise warn and continue
5. Exclude the title column from the sub-section columns list
6. Emit `# <prefix><title>` (title falls back to filename stem if `--title` not provided) then `---`
7. Emit `## <prefix><type>` then `---`
8. For each remaining row:
   a. Emit `### <prefix><title-col value>` (or `### <prefix>N/A` if blank) then `---`
   b. For each remaining column (in specified order):
      - Emit `#### <prefix><column name>`
      - Emit the cell value; format datetime values as `yyyy.mm.dd`; blanks as `N/A`
      - Emit `---`
9. Write the full markdown string to the output file

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

Filter rows by status (use defaults — drops "cancelled" and "close"):
```bash
python excel_to_md.py data/requests.xlsx
```

Custom filter column and excluded values:
```bash
python excel_to_md.py data/requests.xlsx --filter-col "Priority" --exclude "Low" "Medium"
```

Disable filtering entirely (pass an empty exclude list is not supported; use a value that won't appear):
```bash
python excel_to_md.py data/requests.xlsx --exclude "__none__"
```

With a heading prefix:
```bash
python excel_to_md.py data/requests.xlsx --prefix "A."
# headings become: # A.requests, ## A.Demand Planning, ### A.Story A, #### A.Status …
```

Full explicit call:
```bash
python excel_to_md.py data/requests.xlsx \
  --sheet "Requests" \
  --title "Q1 2024 Requests" \
  --type "Demand Planning" \
  --title-col "User Story" \
  --columns "User Story" "Objective and key results" "People and responsabilities" "Status" "Request date" "Wanted date" "Priority" "Observations" \
  --prefix "A." \
  --filter-col "Status" \
  --exclude "cancelled" "close" \
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
- [ ] `--prefix` string is prepended to every heading value at all levels; empty by default (no prefix)
- [ ] Rows where `--filter-col` value (case-insensitive) matches any `--exclude` value are dropped before output
- [ ] Filter column does not need to be in `--columns`
- [ ] If filter column is absent from the sheet a warning is printed and filtering is skipped
- [ ] A `---` horizontal rule follows every heading at levels `#`, `##`, `###` (before nested content)
- [ ] At `####` level the `---` comes **after** the cell content, not between the heading and content
