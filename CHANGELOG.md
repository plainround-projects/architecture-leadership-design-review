# Changelog

All notable changes to this project are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-26

### Added

- The uploads proposal (draft 1), six performance requirements, the review record with its disagreement, a security-lens requirement set and review, their comparison and a seven-question design checklist.
- `design-review check | fitness | report`: proposal, requirement, review and checklist rules (PRP, REQ, REV, CHK, DOC), and the capacity, queue-wait and write-order fitness functions with the scenarios in `model/uploads.toml`.
- Layered package (`domain`, `application`, `infrastructure`, `interfaces`) with the dependency rule enforced by import-linter, unit tests, one integration test per "Done when" line, ruff, mypy strict, hash-pinned lock files and a CI workflow.
