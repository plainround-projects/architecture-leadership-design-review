# Regular expressions (the re module)

## What it is

A **regular expression** (regex) is a short pattern that describes a set of strings, like `^## (.+)$` for "a line
that starts with `## `". Python's standard `re` module compiles a pattern into an object you can use to **match** a
string, **search** inside it, **find all** matches or **split** it. Parentheses in a pattern make **groups** whose text
you can read back.

## Why this repository uses it

The documents are Markdown text with simple conventions (`## Heading`, `Label: text`, `Phase 3: name`). The
program recognizes them with a handful of regexes and turns them into typed values. The patterns are compiled once, as
module-level constants with a leading underscore.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/design_review/infrastructure/markdown.py` | Recognizes headings, code fences and header fields. |
| `src/design_review/domain/*.py` | Finds requirement IDs and numbers in the text. |

## How it works underneath

`re.compile(pattern)` turns the pattern into a small program for matching. `pattern.match(line)` tries to match from
the **start** of the string and returns a match object or `None`. `pattern.search(text)` looks anywhere. A match
object's `.group(1)` is the text of the first parenthesized part. The symbols used here:

| Symbol | Meaning |
| --- | --- |
| `^` and `$` | start and end of the text |
| `.` | any one character |
| `+`, `*`, `?` | one or more, zero or more, optional |
| `+?`, `.*?` | the same but **lazy**: as few characters as possible |
| `\d`, `\s` | a digit, a whitespace character |
| `[A-Z0-9]` | one character from a set |
| `( ... )` | a group to capture |
| `a|b` | a or b |
| `(?<=x)`, `(?=x)` | look-behind and look-ahead: x must come before or after, but is not part of the match |
| `\.` | a literal dot (a backslash cancels a symbol's meaning) |

A string written `r"..."` is a **raw string**: backslashes are kept as they are, which is what patterns need.

## Walkthrough of this repository's use

`src/design_review/infrastructure/markdown.py`:

````python
_HEADING2 = re.compile(r"^## (.+?)\s*$")
_FENCE = re.compile(r"^```")
_FIELD = re.compile(r"^(Author|Date|Reviewers|System|Requirements file):\s*(.*?)\s*$")
````

- `_HEADING2 = r"^## (.+?)\s*$"` matches a line such as `## Requirements` and captures `Requirements`. `^## ` is the fixed
  start; `(.+?)` is the heading text (lazy); `\s*$` allows spaces at the end.
- `_FENCE = r"^```"` matches a line that starts with three backticks: the start or end of a code block in Markdown.
  The code uses it to skip diagrams when it reads a proposal.
- `_FIELD` matches the header lines `Author: ...`, `Date: ...`, `Reviewers: ...`, `System: ...` and
  `Requirements file: ...`. The `|` separates the allowed labels; `(.*?)` captures the rest of the line.

`src/design_review/infrastructure/markdown.py`:

```python
def _header_fields(sections: dict[str, list[str]]) -> dict[str, str]:
    """`Author:`, `Date:` and the other header fields, read only from the lines before the first heading."""
    return {m.group(1): m.group(2) for line in sections[""] if (m := _FIELD.match(line))}
```

Here the pattern is used with `.match(line)` inside a dictionary comprehension. The match is stored in `m` and used
twice (`m.group(1)` is the label, `m.group(2)` the value). It only reads the lines before the first heading.

Other patterns of the same kind appear in the domain files, for example the requirement IDs `R1`, `R2` and the
`ITEM` pattern for checklist lines. Each is a module constant so it is compiled once.

## Try it yourself

```bash
.venv/bin/python -c "from design_review.infrastructure.markdown import _FIELD; m = _FIELD.match('Author: Sam Lee'); print(m.group(1), '|', m.group(2))"
```
Prints `Author | Sam Lee`.

```bash
.venv/bin/python -c 'from design_review.infrastructure.markdown import _HEADING2, _FENCE; print(bool(_HEADING2.match("## Requirements")), bool(_FENCE.match(chr(96) * 3 + "mermaid")), bool(_HEADING2.match("# Title")))'
```
Prints `True True False`: a second-level heading matches, a code fence matches (`chr(96)` is the backtick character, so
`chr(96) * 3` is three of them), a first-level heading does not.

```bash
.venv/bin/python -c "import re; print(re.findall(r'\\bR\\d+\\b', 'R1 and R12, but not XR3'))"
```
Prints `['R1', 'R12']`: `\b` marks a word boundary.

```bash
grep -n "re.compile" src/design_review/infrastructure/markdown.py src/design_review/domain/*.py | cut -c1-110
```
Lists every compiled pattern in the code.

## Mistakes people make

- **Forgetting `r` before the string**, so `\d` is read as a plain `d` with a warning.
- **Greedy matching** that grabs too much: `.+` versus `.+?`.
- **Using `match` when `search` is needed** (`match` only matches at the start).
- **Parsing nested structure with a regex.** Here the patterns recognize single lines, and the code groups lines itself.
- **Not escaping user text** when it is placed inside a pattern. `re.escape` does that (used in the field parser).

## Check yourself

1. What does `_FENCE` match?
   **Answer:** A line that starts with three backticks, a code fence.
2. Why is `\\s*$` at the end of the heading pattern?
   **Answer:** To allow trailing spaces before the end of the line.
3. What does `m.group(2)` return for `_FIELD`?
   **Answer:** The text after the label and colon.
4. Why are the patterns module constants?
   **Answer:** They are compiled once at import, not at every line.
5. What does `\\b` mean?
   **Answer:** A word boundary, the edge between a word character and a non-word character.

## Further reading

- `re` (Python 3.12): <https://docs.python.org/3.12/library/re.html>
- Regular Expression HOWTO: <https://docs.python.org/3.12/howto/regex.html>
