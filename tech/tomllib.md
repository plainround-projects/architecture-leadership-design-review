# tomllib (reading the model file)

## What it is

`tomllib` is the standard Python module that reads TOML text (see `toml.md`). `tomllib.loads(text)` returns nested
dictionaries and lists; `tomllib.load(file)` does the same from a file opened in binary mode. It can only read TOML,
not write it.

## Why this repository uses it

The numbers of the lesson (`model/uploads.toml`) live in one file that is neither Python code nor a document, so they can be read
by the program, compared with the documents, and changed without touching the code. The reader checks every table and
value and fails with a clear message.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/design_review/infrastructure/model_toml.py` | `TomlModelSource.load` parses and validates the file. |
| `model/uploads.toml` | The input. |
| `src/design_review/application/ports.py` | `ModelSource`, the interface the use case sees. |
| `tests/unit/infrastructure/test_readers.py` | Feeds good and broken TOML text to the reader. |

## How it works underneath

`tomllib.loads` parses the text following the TOML 1.0 rules and builds Python objects: tables become `dict`, arrays
become `list`, integers `int`, decimals `float`, text `str`, `true`/`false` `bool`. A syntax error raises
`tomllib.TOMLDecodeError`. The reader then converts and checks each value, because TOML only guarantees syntax, not
meaning.

## Walkthrough of this repository's use

`model/uploads.toml`:

```toml
# The facts of the uploads proposal and the scenarios the review tries. Read by `design-review fitness`.
# `expect` is the verdict the review recorded for the scenario; the command fails when a scenario gives another one.

[load]
listings_per_week = 120000      # the setting: 120,000 listings a week
photos_per_listing = 10         # sellers upload up to 10 photos per listing
weekend_share = 0.70            # most of them between Friday evening and Sunday night
weekend_days = 2.5              # 216,000 seconds

[requirement]
peak_uploads_per_second = 40    # R1
thumbnail_percentile = 95       # R3: 95 percent ...
```

Comments start with `#`. `[load]` starts a table; `listings_per_week = 120000` is a key with an integer value;
`weekend_share = 0.70` is a float. The text after `#` on a value line is a comment.
`src/design_review/infrastructure/model_toml.py`:

```python
def _table(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ModelError(f"the model file has no [{key}] table")
    return value
```

`isinstance(value, dict)` checks that the key holds a table. A missing table raises the program's own error with the
table name, instead of a confusing `KeyError` later.

`src/design_review/infrastructure/model_toml.py`:

```python
        try:
            data = tomllib.loads(self._store.read_text(path))
        except tomllib.TOMLDecodeError as problem:
            raise ModelError(f"{path} is not valid TOML: {problem}") from None
        load_table, burst_table = _table(data, "load"), _table(data, "burst")
```

`tomllib.loads(self._store.read_text(path))` reads through the document store (so tests need no disk). A broken file is
reported as `<path> is not valid TOML: ...`. `from None` hides the library's own traceback.

`src/design_review/infrastructure/model_toml.py`:

```python
            load = LoadModel(
                listings_per_week=int(load_table["listings_per_week"]),
                photos_per_listing=int(load_table["photos_per_listing"]),
                weekend_share=float(load_table["weekend_share"]),
                weekend_days=float(load_table["weekend_days"]),
                peak_uploads_per_second=float(requirement["peak_uploads_per_second"]),
            )
            burst = BurstProfile(
```

`int(...)` and `float(...)` convert each value to the type the model expects. `LoadModel(...)` then validates the
ranges in its `__post_init__` (see `dataclasses.md`).

`model/uploads.toml`:

```toml
[thumbnails.draft1]             # the proposal: 1 worker
workers = 1
expect = "fail"

[thumbnails.floor]              # the sample record's "target 8 workers": covers the average, not the burst
workers = 8
expect = "fail"

[thumbnails.ceiling]            # the review's decision: autoscale on queue age, floor 8, ceiling 80
workers = 80
expect = "pass"
```

Tables with a dotted name, `[thumbnails.draft1]` and `[thumbnails.ceiling]`, become nested dictionaries: the key
`thumbnails` holds the keys `draft1`, `floor`, `ceiling`. The reader loops over them: each is a scenario with the number
of workers and the verdict the review expected (`expect`).

`model/uploads.toml`:

```toml
[durability.draft1]             # the response goes out once the file is stored, the row comes after
order = ["put_object", "respond", "write_row"]
expect = "fail"
```

A list of strings is the order in which the upload steps happen.

## Try it yourself

```bash
.venv/bin/python -c "import tomllib; d = tomllib.load(open('model/uploads.toml', 'rb')); print(list(d))"
```
Prints the top-level table names: `['load', 'requirement', 'service', 'burst', 'thumbnails', 'durability']`.

```bash
.venv/bin/python -c "import tomllib; print(tomllib.loads('x = 1\ny = [1, 2]'))"
```
Prints `{'x': 1, 'y': [1, 2]}`.

```bash
.venv/bin/python -c "import tomllib; tomllib.loads('x = ')" 2>&1 | tail -1
```
Prints a `TOMLDecodeError` that names the line and column.

```bash
.venv/bin/design-review fitness
```
Runs the code that uses the model; ends with an `OK:` line.

## Mistakes people make

- **Opening the file in text mode** for `tomllib.load`: it needs binary mode (`'rb'`).
- **Trusting the types.** TOML says `5` is an integer, but nothing says it is a sensible worker count. The reader
  checks ranges.
- **Hand-editing a number** without changing the document that quotes it. `check` compares them (rule codes in the README).
- **Expecting to write TOML** with `tomllib`. It only reads.

## Check yourself

1. What does `tomllib.loads` return for `[load]` followed by `a = 1`?
   **Answer:** `{'load': {'a': 1}}`.
2. Which exception is raised for invalid TOML?
   **Answer:** `tomllib.TOMLDecodeError`.
3. Why does the reader validate values after parsing?
   **Answer:** TOML only checks syntax, not that a value makes sense.
4. Why does `TomlModelSource` read through the document store?
   **Answer:** So tests can supply the text from memory.
5. How is a dotted table name like `[thumbnails.ceiling]` represented?
   **Answer:** As a nested dictionary: `thumbnails` holds `ceiling`.

## Further reading

- `tomllib` (Python 3.12): <https://docs.python.org/3.12/library/tomllib.html>
- TOML 1.0.0: <https://toml.io/en/v1.0.0>
