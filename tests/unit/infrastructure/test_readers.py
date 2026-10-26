import pytest

from design_review.domain.capacity import ModelError
from design_review.infrastructure.filesystem import FileSystemStore
from design_review.infrastructure.markdown import MarkdownDocumentReader, table_rows
from design_review.infrastructure.model_toml import TomlModelSource
from design_review.infrastructure.settings import SettingsError, load_settings
from tests.conftest import MemoryStore, repository_files


def reader():
    return MarkdownDocumentReader(MemoryStore(repository_files()))


def test_table_rows_keys_cells_by_the_header_and_pads_short_rows():
    rows = table_rows(["| A | B |", "| --- | --- |", "| 1 | 2 |", "| 3 |", "", "| 9 | 9 |"])
    assert rows == [{"A": "1", "B": "2"}, {"A": "3", "B": ""}]
    assert table_rows(["no table here"]) == []


def test_the_requirements_document_is_parsed():
    parsed = reader().read_requirements("docs/requirements/uploads-nfrs.md")
    assert [r.id for r in parsed.requirements] == ["R1", "R2", "R3", "R4", "R5", "R6"]
    assert parsed.requirements[2].target == "95 percent within 30 seconds of upload"
    assert "freshness" in parsed.required_categories


def test_a_requirements_document_without_categories_uses_the_default_five():
    store = MemoryStore({"r.md": "# R\n\n## Requirements\n| ID | Category |\n| - | - |\n| R1 | throughput |\n"})
    assert MarkdownDocumentReader(store).read_requirements("r.md").required_categories[0] == "throughput"


def test_the_proposal_is_parsed_with_its_diagram():
    proposal = reader().read_proposal("docs/proposals/uploads-service-draft-1.md")
    assert proposal.author == "Uploads team lead"
    assert "thumbnail job (1 worker)" in proposal.diagram
    assert set(proposal.sections) >= {"Overview", "Datastore", "Unsure"}
    assert proposal.title.startswith("Proposal: photo uploads")


def test_the_review_record_is_parsed():
    review = reader().read_review("docs/reviews/review-2026-10-22-uploads-service.md")
    assert (review.reviewers, review.author, review.date_text) == (
        "Platform architect",
        "Uploads team lead",
        "2026-10-22",
    )
    assert len(review.used) == 6
    assert [f.cls for f in review.findings][:5] == ["must-fix", "must-fix", "should-fix", "withdrawn", "taste"]
    assert review.findings[4].note == "dropped"
    assert review.disagreements[0].finding == "4"
    assert review.risks[0].owner == "Uploads team lead"
    assert len(review.decisions) == 3
    assert "Requirements used" in review.sections


def test_a_review_without_a_disagreement_has_none():
    store = MemoryStore({"r.md": "# Design review: x\n\n## Findings\n| # |\n| - |\n"})
    assert MarkdownDocumentReader(store).read_review("r.md").disagreements == ()


def test_a_bullet_that_wraps_onto_the_next_line_is_one_decision():
    store = MemoryStore({"r.md": "# Design review: x\n\n## Decisions\n- first line\n  continues here\n- second\n"})
    assert MarkdownDocumentReader(store).read_review("r.md").decisions == ("first line continues here", "second")


def test_the_checklist_is_parsed_and_malformed_lines_are_kept():
    store = MemoryStore({"c.md": "- [ ] CHK-01 [cost] Is there an estimate?\n- [ ] nope\ntext\n"})
    parsed = MarkdownDocumentReader(store).read_checklist("c.md")
    assert [(i.id, i.category) for i in parsed.items] == [("CHK-01", "cost")]
    assert parsed.malformed == ("- [ ] nope",)


def test_the_model_file_is_loaded_and_validated():
    model = TomlModelSource(MemoryStore(repository_files())).load("model/uploads.toml")
    assert model.load.average_rate == pytest.approx(3.889, abs=0.001)
    assert [s.workers for s in model.thumbnails] == [1, 8, 80]
    assert [s.expect_pass for s in model.durability] == [False, True, True]
    assert model.burst.peak_rate == 40


GOOD = repository_files()["model/uploads.toml"]


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("not toml [", "not valid TOML"),
        (GOOD.replace("[burst]", "[burst_x]"), r"no \[burst\]"),
        (GOOD.replace("photos_per_listing = 10", ""), "missing"),
        (GOOD.replace('expect = "fail"', 'expect = "maybe"', 1), "expect must be"),
        (GOOD.replace("weekend_share = 0.70", "weekend_share = 7"), "weekend_share"),
    ],
)
def test_a_bad_model_file_is_rejected_with_a_reason(text, message):
    with pytest.raises(ModelError, match=message):
        TomlModelSource(MemoryStore({"m.toml": text})).load("m.toml")


def test_the_file_system_store_reads_lists_and_writes(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("a")
    (tmp_path / "docs" / "b.txt").write_text("b")
    store = FileSystemStore(tmp_path)
    assert store.list_paths("docs") == ["docs/a.md"]
    assert store.list_paths("nope") == []
    store.write_text("build/r.md", "x")
    assert (store.exists("build/r.md"), store.read_text("build/r.md")) == (True, "x")
    with pytest.raises(ValueError, match="escapes"):
        store.read_text("../x")


def test_settings_default_and_validate():
    assert load_settings({}).check.proposal_max_words == 1000
    assert load_settings({"PROPOSAL_MAX_WORDS": "500", "REVIEW_ROOT": "r"}).check.proposal_max_words == 500
    for bad in ("many", "0"):
        with pytest.raises(SettingsError):
            load_settings({"PROPOSAL_MAX_WORDS": bad})
