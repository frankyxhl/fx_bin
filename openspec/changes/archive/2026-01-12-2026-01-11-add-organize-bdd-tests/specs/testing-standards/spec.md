## ADDED Requirements

### Requirement: BDD Feature File Coverage
The organize command SHALL have Behavior-Driven Development (BDD) tests using pytest-bdd with Gherkin `.feature` files.

#### Scenario: BDD tests are executable
- **WHEN** developer runs `poetry run pytest tests/bdd/test_organize_steps.py -v`
- **THEN** all BDD scenarios execute successfully
- **AND** step definitions are properly implemented

#### Scenario: BDD tests use correct markers
- **WHEN** developer runs `poetry run pytest -m "bdd and smoke" -v`
- **THEN** only smoke-tagged BDD tests execute
- **AND** markers align with pyproject.toml definitions

### Requirement: BDD Scenario Coverage
The organize command BDD tests SHALL cover core functionality scenarios.

#### Scenario: Core functionality coverage
- **WHEN** BDD test suite is executed
- **THEN** scenarios cover: date-based organization, dry-run mode, recursive scanning
- **AND** scenarios cover: conflict resolution modes (SKIP, OVERWRITE, RENAME, ASK)
- **AND** scenarios cover: edge cases (empty directories, invalid paths, symlinks)

#### Scenario: Path structure matches specification
- **WHEN** BDD scenarios describe date-based organization
- **THEN** default path structure is documented as `YYYY/YYYYMM/YYYYMMDD/` (depth 3)
- **AND** aligns with `openspec/specs/organize/spec.md`
