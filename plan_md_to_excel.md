# Plan: md_to_excel.py

## Purpose
Round-trip a structured Markdown file (produced by excel_to_md.py) back to an Excel file,
reconstructing rows and columns from the heading/content structure.

## Dependencies
- `pandas` — DataFrame construction and Excel output
- `openpyxl` — Excel backend for pandas
- `argparse` — CLI interface (stdlib)
- `datetime` — date string parsing (stdlib)

## CLI Interface

```
python md_to_excel.py <file> [options]

positional:
  file                  Path to the Markdown file

options:
  --sheet TEXT          Sheet name in the output Excel file (default: "Requests")
  --title-col TEXT      Column name that ### headings map to (default: "User Story")
  --prefix TEXT         Prefix used in excel_to_md.py, stripped from all headings (default: "")
  --output FILE         Output .xlsx path (default: same dir/name as input, .xlsx extension)
```

## Markdown Structure Assumptions
The parser expects the format produced by excel_to_md.py:

```
# <prefix><document title>

---

## <prefix><type>

---

### <prefix><row title value>      ← one per data row
---
#### <prefix><column name>         ← one per column
<cell content>
---
...
### <prefix><next row title value>
...
```

## Parsing Algorithm (state machine)

1. Read markdown line by line
2. Skip `#` and `##` headings — document title and type are not reconstructed
3. On a `### ` line: flush and save current cell and row (if any); start a new row dict
   with the stripped heading value mapped to `--title-col`
4. On a `#### ` line: flush and save current cell (if any); start collecting content for
   the new column (strip prefix from the column name)
5. On a `---` line: flush and save current cell (saves buffered content into current row)
6. On any other non-blank line: if inside a `####` section, append to the content buffer
7. After the last line: flush final cell; save final row

## Type Restoration
Values are restored from their formatted string representation:
- `yyyy.mm.dd` string → `datetime.date`
- Pure integer string → `int`
- Pure float string → `float`
- `N/A` → `None` (becomes an empty cell in Excel)
- Anything else → `str`

## Column Order
Output Excel columns follow the order columns first appear in the markdown:
`[title_col] + [other columns in order of first appearance in #### headings]`

## Logic / Implementation Steps

1. Parse CLI arguments; apply defaults
2. Check input file exists; exit with a clear error if not
3. Parse the markdown into a list of row dicts using the state machine above
4. Derive column order from `####` headings (first appearance, preserving order)
5. Build a DataFrame with columns in that order
6. Exit with a clear error if no rows were parsed (likely wrong `--prefix` or wrong file)
7. Write DataFrame to Excel: sheet name from `--sheet`, no row index
8. Print confirmation with row and column count

## Error Handling
- File not found: clear error message, exit
- No rows parsed: suggest checking `--prefix` and `--title-col`, exit

## Example Calls

Default (sheet "Requests", title col "User Story", no prefix):
```bash
python md_to_excel.py data/requests.md
# → writes data/requests.xlsx
```

With prefix to strip:
```bash
python md_to_excel.py data/requests.md --prefix "A."
```

Custom sheet and title column:
```bash
python md_to_excel.py data/requests.md --sheet "Q2 Requests" --title-col "Objective and key results"
```

Full explicit call:
```bash
python md_to_excel.py data/requests.md \
  --sheet "Requests" \
  --title-col "User Story" \
  --prefix "A." \
  --output output/reconstructed.xlsx
```

## Validation Checklist
- [ ] Each `###` section produces exactly one row
- [ ] `###` heading value maps to `--title-col`
- [ ] `####` heading names become column names (prefix stripped)
- [ ] Column order in output matches order of first appearance in markdown
- [ ] `N/A` values become empty cells (`None`)
- [ ] `yyyy.mm.dd` strings are restored to `datetime.date`
- [ ] Integer and float strings are restored to their numeric types
- [ ] `--prefix` is stripped from both `###` and `####` headings
- [ ] Output defaults to same dir/name as input with `.xlsx` extension
- [ ] Output sheet name is set by `--sheet`
- [ ] Missing input file produces a clear error message
- [ ] Empty parse result produces a clear error message
