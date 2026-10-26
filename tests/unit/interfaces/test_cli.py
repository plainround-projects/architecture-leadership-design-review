import shutil
from pathlib import Path

import pytest

from design_review.interfaces.cli import main
from tests.conftest import REPOSITORY_ROOT


@pytest.fixture
def copy_of_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shutil.copytree(REPOSITORY_ROOT / "docs", tmp_path / "docs")
    shutil.copytree(REPOSITORY_ROOT / "model", tmp_path / "model")
    monkeypatch.setenv("REVIEW_ROOT", str(tmp_path))
    return tmp_path


def test_check_passes(copy_of_repo, capsys):
    assert main(["check"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "OK: 6 documents checked, 0 errors, 0 warnings"


def test_check_fails_when_the_calculation_is_removed(copy_of_repo, capsys):
    review = copy_of_repo / "docs/reviews/review-2026-10-22-uploads-service.md"
    review.write_text(review.read_text().replace(" = ", " is "))
    assert main(["check"]) == 1
    assert "REV004" in capsys.readouterr().out


def test_fitness_prints_the_table(copy_of_repo, capsys):
    assert main(["fitness"]) == 0
    out = capsys.readouterr().out
    assert "ceiling" in out
    assert out.splitlines()[-1].startswith("OK:")


def test_fitness_fails_when_a_scenario_surprises_the_review(copy_of_repo, capsys):
    model = copy_of_repo / "model/uploads.toml"
    model.write_text(model.read_text().replace("workers = 80", "workers = 9"))
    assert main(["fitness"]) == 1
    assert "UNEXPECTED" in capsys.readouterr().out


def test_report_writes_markdown(copy_of_repo):
    assert main(["report"]) == 0
    assert "## Fitness functions" in (copy_of_repo / "build/report.md").read_text()


def test_a_broken_model_exits_with_2(copy_of_repo, capsys):
    (copy_of_repo / "model/uploads.toml").write_text("[load]\n")
    assert main(["fitness"]) == 2
    assert "model error" in capsys.readouterr().err


def test_a_bad_setting_exits_with_2(monkeypatch, capsys):
    monkeypatch.setenv("PROPOSAL_MAX_WORDS", "lots")
    assert main(["check"]) == 2
    assert "PROPOSAL_MAX_WORDS" in capsys.readouterr().err
