from dataclasses import replace

from design_review.domain.checklist import Checklist, ChecklistItem, check_checklist
from design_review.domain.proposal import Proposal, check_proposal
from design_review.domain.requirements import Requirement, RequirementSet, check_requirements
from design_review.domain.review import (
    AcceptedRisk,
    ActionItem,
    Assessment,
    Disagreement,
    ReviewFinding,
    ReviewRecord,
    UsedRequirement,
    check_review,
    warn_long_must_fix,
)

SET = RequirementSet(
    "docs/requirements/x.md",
    (
        Requirement("R1", "throughput", "Peak", "40 uploads a second", "load test"),
        Requirement("R2", "latency", "p99", "under 3 seconds", "dashboard"),
        Requirement("R3", "availability", "Uptime", "99.9 percent a month", "uptime check"),
        Requirement("R4", "durability", "Loss", "0 uploads lost", "restore test"),
        Requirement("R5", "cost", "Cost", "2,000 dollars a month", "cloud bill"),
    ),
)


def req_codes(requirement_set):
    return {f.code for f in check_requirements(requirement_set)}


def test_good_requirements_pass():
    assert check_requirements(SET) == []


def test_an_adjective_is_not_a_requirement():
    broken = replace(SET, requirements=(replace(SET.requirements[0], target="fast"), *SET.requirements[1:]))
    assert "REQ001" in req_codes(broken)


def test_a_number_that_reads_as_an_adjective_is_caught():
    broken = replace(SET, requirements=(replace(SET.requirements[0], target="highly 1"), *SET.requirements[1:]))
    assert "REQ001" in req_codes(broken)


def test_a_requirement_nobody_can_check_is_a_wish():
    broken = replace(SET, requirements=(replace(SET.requirements[0], verification="TBD"), *SET.requirements[1:]))
    assert "REQ002" in req_codes(broken)


def test_the_five_categories_must_be_covered():
    assert "REQ003" in req_codes(replace(SET, requirements=SET.requirements[:3]))


def test_ids_must_be_unique():
    assert "REQ004" in req_codes(
        replace(SET, requirements=(SET.requirements[0], SET.requirements[0], *SET.requirements[1:]))
    )


NAMES = ("Overview", "Data flow", "Datastore", "External calls", "Scaling", "Failure handling", "Unsure")
SECTIONS = dict.fromkeys(NAMES, "enough words in this section")
PROPOSAL = Proposal("p.md", "T", "A", SECTIONS, "a --> b", 400)


def test_a_concrete_proposal_passes():
    assert check_proposal(PROPOSAL) == []


def test_a_proposal_must_name_its_datastore_and_the_rest():
    sections = {**SECTIONS, "Datastore": ""}
    assert [f.code for f in check_proposal(replace(PROPOSAL, sections=sections))] == ["PRP001"]


def test_a_proposal_needs_a_diagram_with_arrows():
    assert [f.code for f in check_proposal(replace(PROPOSAL, diagram="boxes"))] == ["PRP002"]


def test_a_proposal_longer_than_two_pages_is_reported():
    assert [f.code for f in check_proposal(replace(PROPOSAL, word_count=1001))] == ["PRP003"]
    assert check_proposal(replace(PROPOSAL, word_count=1001), max_words=2000) == []


def test_a_proposal_needs_an_author():
    assert [f.code for f in check_proposal(replace(PROPOSAL, author=""))] == ["PRP004"]


def good_review() -> ReviewRecord:
    return ReviewRecord(
        path="docs/reviews/review-a.md",
        system="s",
        date_text="2026-10-22",
        reviewers="Reviewer",
        author="Author",
        requirements_path=SET.path,
        sections=(
            "Requirements used",
            "Assessment",
            "Findings",
            "Decisions",
            "Accepted risks",
            "Action items",
            "Disagreement",
        ),
        used=tuple(UsedRequirement(r.id, r.name, r.target, r.verification) for r in SET.requirements),
        assessments=(
            Assessment("R1", "doesn't", "1 / 2 s = 0.5 a second"),
            Assessment("R2", "meets", "fine"),
            Assessment("R3", "might not", "single points"),
            Assessment("R4", "meets", "fine"),
            Assessment("R5", "meets", "fine"),
        ),
        findings=(
            ReviewFinding("1", "one worker", "R1", "must-fix", ""),
            ReviewFinding("2", "single point", "R3", "should-fix", ""),
            ReviewFinding("3", "one retry", "R1", "withdrawn", ""),
            ReviewFinding("4", "another CDN", "none", "taste", "dropped"),
        ),
        decisions=("Workers will scale on queue age.",),
        risks=(AcceptedRisk("R3: one database", "Team lead", "2026-12-01"),),
        actions=(ActionItem("add a metric", "Team lead", "2026-10-29"),),
        disagreements=(Disagreement("3", "failures are rare", "accepted. I changed my position."),),
    )


def rev_codes(review):
    return {f.code for f in check_review(review, SET)}


def test_a_good_review_passes():
    assert check_review(good_review(), SET) == []


def test_a_review_needs_its_header_and_sections():
    assert "REV001" in rev_codes(replace(good_review(), date_text="soon"))
    assert "REV001" in rev_codes(replace(good_review(), author=""))
    assert "REV013" in rev_codes(replace(good_review(), sections=("Findings",)))


def test_requirements_must_match_the_requirements_document():
    review = good_review()
    changed = replace(review, used=(replace(review.used[0], target="10 uploads a second"), *review.used[1:]))
    assert "REV002" in rev_codes(changed)
    assert "REV002" in rev_codes(replace(review, used=(*review.used[:4], replace(review.used[4], id="R9"))))
    assert "REV002" in rev_codes(replace(review, used=review.used[:4]))


def test_every_requirement_needs_a_verdict_from_the_list():
    review = good_review()
    assert "REV003" in rev_codes(replace(review, assessments=review.assessments[:4]))
    assert "REV003" in rev_codes(
        replace(review, assessments=(replace(review.assessments[0], verdict="bad"), *review.assessments[1:]))
    )


def test_the_review_must_show_a_calculation():
    review = good_review()
    no_math = replace(review, assessments=(replace(review.assessments[0], reason="too slow"), *review.assessments[1:]))
    assert "REV004" in rev_codes(no_math)


def test_a_concern_must_point_at_a_requirement():
    review = good_review()
    opinion = replace(review, findings=(replace(review.findings[0], requirement="R9"), *review.findings[1:]))
    assert "REV005" in rev_codes(opinion)
    bad_class = replace(review, findings=(replace(review.findings[0], cls="urgent"), *review.findings[1:]))
    assert "REV005" in rev_codes(bad_class)


def test_a_taste_finding_names_no_requirement_and_is_dropped_aloud():
    review = good_review()
    with_requirement = replace(review.findings[3], requirement="R1")
    assert "REV006" in rev_codes(replace(review, findings=(*review.findings[:3], with_requirement)))
    kept = replace(review.findings[3], note="")
    assert "REV006" in rev_codes(replace(review, findings=(*review.findings[:3], kept)))


def test_a_review_that_blocks_on_everything_is_a_bottleneck():
    review = good_review()
    all_must = tuple(replace(item, cls="must-fix", requirement="R1", note="") for item in review.findings)
    assert "REV008" in rev_codes(replace(review, findings=all_must))
    no_taste = replace(review, findings=review.findings[:3])
    assert "REV008" in rev_codes(no_taste)


def test_decisions_risks_and_actions_need_owners_and_dates():
    review = good_review()
    assert "REV009" in rev_codes(replace(review, decisions=()))
    assert "REV009" in rev_codes(replace(review, decisions=("ok",)))
    assert "REV010" in rev_codes(replace(review, risks=(AcceptedRisk("R3: x", "the team", "2026-12-01"),)))
    assert "REV010" in rev_codes(replace(review, risks=(AcceptedRisk("R3: x", "Lead", "December"),)))
    assert "REV011" in rev_codes(replace(review, actions=()))
    assert "REV011" in rev_codes(replace(review, actions=(ActionItem("x", "everyone", "2026-10-29"),)))
    assert "REV011" in rev_codes(replace(review, actions=(ActionItem("x", "Lead", "soon"),)))


def test_a_verdict_that_is_not_met_needs_a_finding_or_a_risk():
    review = good_review()
    orphan = replace(review, findings=review.findings[2:], risks=())
    assert "REV007" in rev_codes(orphan)


def test_a_review_where_the_reviewer_is_never_wrong_looks_like_a_rubber_stamp():
    review = good_review()
    assert "REV012" in rev_codes(replace(review, disagreements=()))
    assert "REV012" in rev_codes(replace(review, disagreements=(Disagreement("3", "x", "rejected."),)))
    assert "REV012" in rev_codes(replace(review, disagreements=(Disagreement("1", "x", "accepted."),)))


def test_a_long_must_fix_list_is_a_warning():
    review = good_review()
    many = tuple(replace(review.findings[0], number=str(n)) for n in range(5))
    assert [f.code for f in warn_long_must_fix(replace(review, findings=many))] == ["REV014"]
    assert warn_long_must_fix(review) == []


CHECK = Checklist(
    "c.md",
    (
        ChecklistItem("CHK-01", "throughput", "Did you compute the peak?"),
        ChecklistItem("CHK-02", "availability", "Which parts are single points?"),
    ),
    (),
)


def test_a_checklist_that_covers_the_findings_passes():
    assert check_checklist(CHECK, SET, [good_review()]) == []


def test_a_checklist_item_is_a_question_in_a_known_category():
    items = (ChecklistItem("CHK-01", "throughput", "Compute the peak."), ChecklistItem("CHK-02", "mystery", "Why?"))
    assert [f.code for f in check_checklist(replace(CHECK, items=items), SET, [])] == ["CHK001", "CHK001"]


def test_malformed_lines_and_long_lists_are_reported():
    assert [f.code for f in check_checklist(replace(CHECK, malformed=("- [ ] bad",)), SET, [])] == ["CHK001"]
    assert [f.code for f in check_checklist(CHECK, SET, [], max_items=1)] == ["CHK003"]


def test_a_finding_in_a_category_no_item_covers_is_reported():
    review = good_review()
    only_throughput = replace(CHECK, items=CHECK.items[:1])
    assert [f.code for f in check_checklist(only_throughput, SET, [review])] == ["CHK002"]
