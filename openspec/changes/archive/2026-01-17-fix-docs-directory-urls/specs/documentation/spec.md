# Spec: Documentation Capability (MODIFIED)

## Overview
MODIFIED requirements for the documentation capability to ensure MkDocs configuration correctness and proper URL access patterns.

## MODIFIED Requirements

### Requirement: MkDocs configuration aligns with repository docs directory
The documentation site MUST have correct MkDocs configuration to ensure proper build and deployment.

- The `mkdocs.yml` configuration MUST specify the `docs_dir` setting.
- The `docs_dir` value MUST point to the directory containing the documentation source files.
- The `docs_dir` value MUST align with the actual directory structure of the repository.

#### Scenario: Repository with documentation in a subdirectory
- **GIVEN** documentation source files are located in `docs/site/`
- **AND** MkDocs `nav` entries reference paths like `commands/files.md`
- **WHEN** MkDocs runs `mkdocs build` for GitHub Pages deployment
- **THEN** `mkdocs.yml` MUST include `docs_dir: docs/site`
- **AND** the build MUST complete without file-not-found errors

#### Scenario: Verification of build output
- **GIVEN** `mkdocs.yml` includes `docs_dir: docs/site`
- **WHEN** the build runs with `mkdocs build --clean`
- **THEN** the build MUST complete successfully
- **AND** the output directory `site/` MUST be created
- **AND** `site/index.html` MUST be created
- **AND** `site/commands/files/index.html` MUST be created

### Requirement: CI builds and deploys documentation successfully
The documentation site MUST be successfully built by MkDocs and deployed to GitHub Pages.

- MkDocs build MUST complete without errors.
- All documentation source files MUST be converted to HTML.
- The output MUST be compatible with the configured GitHub Pages deployment mechanism.
- The GitHub Actions workflow MUST successfully deploy the built site.

#### Scenario: GitHub Actions build and deployment
- **GIVEN** `.github/workflows/deploy-docs.yml` runs `mkdocs build`
- **AND** `mkdocs.yml` has correct `docs_dir` configuration
- **WHEN** code is pushed to the `main` branch
- **THEN** the "Deploy Documentation" workflow MUST succeed
- **AND** documentation MUST be accessible on GitHub Pages after deployment

### Requirement: Documentation pages are accessible via directory URLs
All documentation pages MUST be accessible via correct, user-friendly URLs.

- All documentation pages MUST be accessible via directory URLs.
- Directory URLs MUST work both with and without trailing slashes.
- No 404 errors should occur for valid documentation pages.
- Internal links MUST point to correct accessible URLs.

#### Scenario: Command documentation access
- **GIVEN** documentation includes command pages under `docs/site/commands/`
- **WHEN** a user accesses command pages via `/commands/<command>/`
- **THEN** the following pages MUST be accessible:
  - `/commands/files/`
  - `/commands/size/`
  - `/commands/ff/`
  - `/commands/fff/`
  - `/commands/filter/`
  - `/commands/replace/`
  - `/commands/backup/`
  - `/commands/root/`
  - `/commands/today/`
  - `/commands/organize/`

#### Scenario: Use case and advanced documentation access
- **GIVEN** documentation includes use-case pages under `docs/site/use-cases/` and advanced pages under `docs/site/advanced/`
- **WHEN** a user accesses documentation pages via directory URLs
- **THEN** the following pages MUST be accessible:
  - `/use-cases/daily-workflow/`
  - `/use-cases/project-cleanup/`
  - `/use-cases/version-updates/`
  - `/use-cases/dataset-management/`
  - `/use-cases/automation-scripts/`
  - `/advanced/shell-integration/`
  - `/advanced/performance/`

## Notes

### MkDocs Configuration Best Practices
- Always specify `docs_dir` if documentation is not in the default `docs/` directory
- The `docs_dir` value should be relative to the repository root
- Nav paths are resolved relative to `docs_dir`
- Default `use_directory_urls: true` is recommended for cleaner URLs

### GitHub Pages Behavior
- GitHub Pages serves `index.html` from directories automatically
- Directory URLs (`/commands/files/`) are preferred for user experience
- Both `/path` and `/path/` (with trailing slash) work (301 redirect)
- Markdown `.md` files are NOT served (only HTML files are deployed)

### URL Patterns
- **Preferred**: Directory URLs (e.g., `/commands/files/`)
- **Alternative**: Explicit HTML URLs (e.g., `/commands/files/index.html`)
- **Not Supported**: Markdown URLs (e.g., `/commands/files.md`)

## Migration Notes

This is a MODIFIED requirement that fixes a configuration oversight in the original GitHub Pages implementation.

### From (Previous)
- No `docs_dir` configuration
- MkDocs defaulting to `docs/` directory
- File resolution issues and build failures

### To (Correct)
- Added `docs_dir: docs/site` configuration
- Correct file resolution
- Successful builds and deployments

### Backward Compatibility
- No breaking changes
- Existing directory URLs continue to work
- Only fixes configuration issues
