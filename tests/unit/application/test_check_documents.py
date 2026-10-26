import pytest

from design_review.application.check_documents import CheckSettings, check_documents, run_fitness_functions
from design_review.application.reporting import render_fitness, render_markdown, render_text
from design_review.infrastructure.markdown import MarkdownDocumentReader
from design_review.infrastructure.model_toml import TomlModelSource
from tests.conftest import MemoryStore, repository_files


def run(files):
    store = MemoryStore(files)
    return check_documents(store, MarkdownDocumentReader(store), CheckSettings())


def test_the_repository_documents_pass():
    report = run(repository_files())
    assert report.ok
    assert report.findings == ()
    assert len(report.subjects) == 6


def test_a_review_pointing_at_an_unknown_requirements_file_is_reported():
    files = repository_files()
    path = "docs/reviews/review-2026-10-22-uploads-service.md"
    files[path] = files[path].replace("docs/requirements/uploads-nfrs.md", "docs/requirements/missing.md")
    assert {f.code for f in run(files).findings} == {"REV002"}


def test_a_missing_checklist_is_reported():
    files = repository_files()
    del files["docs/checklists/design-checklist.md"]
    assert {f.code for f in run(files).findings} == {"DOC001"}


def test_the_template_is_not_mistaken_for_a_review():
    files = repository_files()
    files["docs/reviews/comparison.md"] = "not a review"
    assert run(files).ok


@pytest.fixture(scope="module")
def fitness():
    store = MemoryStore(repository_files())
    return run_fitness_functions(TomlModelSource(store), horizon_seconds=43_200)


def test_the_models_scenarios_give_the_recorded_verdicts(fitness):
    assert fitness.ok
    assert [r.passed for r in fitness.thumbnails] == [False, False, True]
    assert [v.result.holds for v in fitness.durability] == [False, True, True]


def test_reports_render_text_and_markdown(fitness):
    text = render_fitness(fitness)
    assert "peak needs 80 workers" in text
    assert "lost: crash after put_object, respond" in text
    assert "orphan:" in text
    assert text.splitlines()[-1].startswith("OK:")
    report = run(repository_files())
    assert render_text(report).splitlines()[-1] == "OK: 6 documents checked, 0 errors, 0 warnings"
    markdown = render_markdown(report, fitness)
    assert "**Verdict:** OK" in markdown
    assert "None." in markdown
    assert "## Fitness functions" in markdown


def test_failing_reports_say_so():
    files = repository_files()
    del files["docs/checklists/design-checklist.md"]
    report = run(files)
    assert render_text(report).splitlines()[0].startswith("ERROR")
    assert "FAILED" in render_text(report)
    assert "| error | DOC001 |" in render_markdown(
        report, run_fitness_functions(TomlModelSource(MemoryStore(repository_files())), horizon_seconds=7200)
    )
