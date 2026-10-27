# Markdown (the document format)

## What it is

Markdown is a way to write formatted text in a plain text file. A line starting with `#` is a heading (more `#` means
a smaller heading), `- ` starts a bullet, `1. ` starts a numbered list, `|` draws a table, and three backticks around
lines mark a block of code. GitHub and most editors show it formatted; as plain text it is still easy to read.

## Why this repository uses it

The lesson's deliverables are documents. They are Markdown so they diff and review like code. The toolkit then reads
those same files, so the documents are not only written but **checked**: a rule fails when a required part is
missing.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `docs/proposals/*.md` | The system proposal. |
| `docs/requirements/*.md` | Numbers with a way to verify each, as a table. |
| `docs/reviews/*.md` | Review records, with findings tied to requirements. |
| `docs/checklists/design-checklist.md` | The reusable checklist. |
| `templates/review-template.md` | The empty review record. |
| `build/report.md` | The generated report. |

## How it works underneath

Markdown has no schema. This repository adds a small convention on top: second-level headings (`## Name`) mark
sections, `Label: text` lines hold fields, and tables hold lists of items. The parser reads the file as lines, groups
the lines under each heading, and picks out fields and rows with the regular expressions in `re.md`. It does not turn
Markdown into HTML; it only extracts the parts the rules need.

## Walkthrough of this repository's use

### A real document

`docs/requirements/uploads-nfrs.md`:

```markdown
# Requirements: photo uploads service

Date: 2026-10-22
Categories: throughput, latency, freshness, availability, durability, cost

## Requirements
| ID | Category | Requirement | Target | How to verify |
| --- | --- | --- | --- | --- |
| R1 | throughput | Peak throughput | 40 uploads a second | load test |
| R2 | latency | Upload p99 latency | under 3 seconds for a 5 MB photo | load test, then dashboard |
| R3 | freshness | Thumbnails ready | 95 percent within 30 seconds of upload | queue age metric |
| R4 | availability | Availability of the upload API | 99.9 percent a month (about 43 minutes of downtime) | uptime check |
| R5 | durability | Accepted uploads lost | 0 accepted uploads lost | storage replication setting, restore test |
```

- The first line is the document's title (`#`).
- The lines `Label: value` are **fields**. The parser reads them with a pattern for the known labels.
- Each `##` line starts a **section**. The checker knows which sections must exist.
- The table has a header row, a separator row (`| --- |`) and data rows. `table_rows` skips the separator.

### How the parser groups lines

`src/design_review/infrastructure/markdown.py`:

```python
def table_rows(lines: list[str]) -> list[dict[str, str]]:
    """The rows of the first Markdown table in the lines, keyed by the header cells."""
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
        elif rows:
            break
    if len(rows) < 3:
        return []
    header, body = rows[0], rows[2:]
    return [dict(zip(header, row, strict=False)) | dict.fromkeys(header[len(row) :], "") for row in body]
```

`table_rows` reads consecutive lines that start with `|`, cuts each into cells at the `|` signs, drops the separator row, and pairs the cells with the header names. `dict(zip(header, row, strict=False))` builds one dictionary per row; the `|` between two dictionaries merges them, filling cells missing from a short row with empty text.

Rule codes such as `ADR013` or `PLN002` come from the checks that read these files; the README lists them. The
integration test `tests/integration/test_done_when.py` damages a copy of a document on purpose and checks that
the matching code appears.

## Try it yourself

```bash
head -12 docs/requirements/uploads-nfrs.md
```
Shows the top of a real document in this repository.

```bash
make run
```
Reads every document and prints `OK: N documents checked, 0 errors, ...` (a warning line may appear).

An experiment on a copy, outside the repository:

```bash
rm -rf /tmp/doc-experiment && mkdir /tmp/doc-experiment && cp -r docs model /tmp/doc-experiment/
sed -i.bak 's/ = / is /' /tmp/doc-experiment/docs/reviews/review-2026-10-22-uploads-service.md
REVIEW_ROOT=/tmp/doc-experiment .venv/bin/design-review check | tail -3; echo "exit: ${PIPESTATUS[0]}"
```
The checker prints a finding with the code `REV004` (the review no longer shows its calculation) and the exit status is 1.

```bash
grep -c '^## ' docs/requirements/uploads-nfrs.md
```
Counts the sections of a document.

## Mistakes people make

- **Trailing spaces in Markdown** can mean a hard line break; `.editorconfig` leaves them alone in `*.md` for that reason.
- **Renaming a section heading** in a document, which makes the checker report it missing.
- **Editing generated files** (`docs/decision-log.md`, `build/report.md`) by hand. The next run overwrites them.
- **Mixing tabs and spaces in a table**, which breaks the cell split.

## Check yourself

1. What marks a section in these documents?
   **Answer:** A second-level heading, `## Name`.
2. How are fields written?
   **Answer:** As `Label: text` lines.
3. What does the second row of a Markdown table do?
   **Answer:** It separates the header from the data rows (`| --- |`); the parser skips it.
4. Why does the checker read Markdown instead of rendering it?
   **Answer:** It needs the parts (sections, fields, rows) to apply rules, not the look.
5. What does the integration test do to a document?
   **Answer:** It damages a copy of the document and checks that the matching rule code appears.

## Further reading

- CommonMark specification: <https://spec.commonmark.org/0.31.2/>
- GitHub Flavored Markdown (tables): <https://github.github.com/gfm/>
