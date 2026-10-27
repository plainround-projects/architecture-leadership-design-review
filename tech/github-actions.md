# GitHub Actions

## What it is

**Continuous integration (CI)** means that a server runs your checks automatically each time you push code, so a
break is found in minutes. **GitHub Actions** is GitHub's CI service. A **workflow** is a YAML file in
`.github/workflows/`. It names the events that start it and the **jobs** to run. A **job** is a list of **steps**
that run on a fresh virtual machine (a **runner**).

## Why this repository uses it

The README promises that `make check`, `make audit` and `make run` pass. CI is the independent witness: it
builds from a clean checkout, so "works on my machine" cannot hide a missing file or an unpinned tool.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| .github/workflows/ci.yml | The only workflow. |
| `Makefile` | The workflow calls `make check`, `make audit` and `make run`. |
| `build/report.md` | Uploaded by the last step as a downloadable artifact named `report`. |

## How it works underneath

1. You push a commit (or open a pull request). GitHub reads every file in `.github/workflows/`.
2. For each workflow whose `on:` matches the event, GitHub starts a runner: a clean Ubuntu machine.
3. The steps run in order. A step is either `uses:` (run a packaged action from another repository, pinned by a
   tag like `@v4`) or `run:` (run a shell command). A step that exits non-zero fails the job and stops it.
4. The runner starts empty each time: no `.venv`, no `.env`. Every run proves the repository builds from scratch.
5. An **artifact** is a file the job saves so you can download it later.

## Walkthrough of this repository's use

`.github/workflows/ci.yml`:

```yaml
name: ci

on: [push, pull_request]

jobs:
  check:
    name: Format, lint, types, import rules, document checks, tests with coverage, dependency audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: make check
      - run: make audit
```

- `name: ci`: the label shown in GitHub.
- `on: [push, pull_request]`: run on every push and on every pull request.
- `jobs:` / `check:` starts one job named `check`. Its `name:` is the long title shown in the interface.
- `runs-on: ubuntu-latest`: the kind of machine.
- `actions/checkout@v4`: downloads the repository's files onto the runner. Without it the machine has no code.
- `actions/setup-python@v5` with `python-version: "3.12"`: installs Python 3.12 (the lowest version the project
  supports, which also matches the lock file's `--python-version 3.12`). The quotes make YAML read `3.12` as text, not
  the number 3.12 (which would lose the trailing zero if it were `3.10`).
- `run: make check`: lint, types, import rules, document checks and tests with coverage.
- `run: make audit`: the dependency audit.
- `run: make run`: runs the program itself and writes `build/report.md`.
- `actions/upload-artifact@v4`: saves `build/report.md` under the name `report`.

Each `-` begins a list item (a step). Indentation is meaningful in YAML (see `yaml.md`).

## Try it yourself

```bash
sed -n 1,10p .github/workflows/ci.yml
```
Prints the top of the workflow.

```bash
make check && make audit && make run
```
This is what CI does after setting up Python. Each command should end with a success line.

```bash
grep -nE "uses:|run:" .github/workflows/ci.yml
```
Lists the six steps: three `uses:` actions, then `run: make check`, `run: make audit`, `run: make run`, and the
upload action. Once the repository is pushed, the GitHub "Actions" tab shows a real run.

```bash
ls .github/workflows
```
Prints `ci.yml`.

## Mistakes people make

- **Different commands in CI and locally.** Here CI only calls `make` targets.
- **Unquoted version numbers** like `3.10` in YAML, which become `3.1`.
- **Forgetting `actions/checkout`**, so later steps see an empty folder.
- **Using `@main` for actions.** This file pins major versions (`@v4`, `@v5`).
- **Treating a passing CI as proof of the lesson.** It proves the checks run; the README's table says what each
  check proves.

## Check yourself

1. What starts this workflow?
   **Answer:** A push or a pull request.
2. Why does CI run `make check` instead of listing each tool?
   **Answer:** So CI and a laptop run exactly the same commands.
3. What does `actions/checkout@v4` do?
   **Answer:** It copies the repository's files onto the runner.
4. Why is the Python version written in quotes?
   **Answer:** So YAML keeps it as text; a bare 3.12 would be read as a number.
5. What does the last step do?
   **Answer:** It saves `build/report.md` as a downloadable artifact.

## Further reading

- GitHub Actions documentation: <https://docs.github.com/en/actions>
- Workflow syntax: <https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions>
- `actions/checkout` v4: <https://github.com/actions/checkout/tree/v4>; `actions/setup-python` v5: <https://github.com/actions/setup-python/tree/v5>; `actions/upload-artifact` v4: <https://github.com/actions/upload-artifact/tree/v4>
