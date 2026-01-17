# Change: Fix MkDocs Configuration for Documentation Deployment

## Why
The current MkDocs configuration is missing the `docs_dir` setting, causing the following issues:
- Documentation files are located in the `docs/site/` directory
- The MkDocs `nav` configuration references files as `commands/files.md` (relative to `docs/`)
- MkDocs defaults to looking for files in the `docs/` directory
- Result: MkDocs cannot find documentation files, causing build failures or incorrect content
- Users experience 404 errors or missing documentation pages

This is a critical configuration oversight preventing proper documentation deployment.

## Dependencies
- **DEPENDS ON**: `openspec/changes/add-github-pages` (previous change that created the documentation site)
- **REASON**: This change fixes a configuration oversight in the original GitHub Pages implementation

## What Changes
- **MODIFY**: Update `mkdocs.yml` to add the `docs_dir: docs/site` configuration
- **IMPACT**: MkDocs will correctly locate documentation files in the `docs/site/` directory
- **BENEFIT**: The documentation builds successfully and all pages are accessible
- **BACKWARD COMPATIBLE**: No breaking changes (fixes configuration only)

## Impact
- **Affected specs**:
  - MODIFIED: `documentation` capability from `openspec/changes/add-github-pages/specs/documentation/spec.md`
  - REQUIRES: Add MODIFIED requirements for MkDocs configuration correctness
- **Affected code**:
  - MODIFY: `mkdocs.yml` (add `docs_dir: docs/site` configuration)
- **Affected documentation**:
  - No content changes required
  - MkDocs configuration fix only
- **Deployment**:
  - GitHub Actions will rebuild documentation successfully
  - All documentation pages will be accessible
  - URLs will work as intended
- **Breaking changes**: None (configuration fix only, no content or API changes)
- **Migration needs**: None (configuration update only, no user-facing changes)

## Success Criteria
- [ ] MkDocs build completes successfully without errors
- [ ] All documentation pages are accessible via correct URLs
- [ ] GitHub Actions workflow "Deploy Documentation" succeeds
- [ ] Documentation deploys to GitHub Pages without issues
- [ ] No 404 errors on any documentation page
- [ ] All 10 command pages are accessible
- [ ] All 5 use case pages are accessible
- [ ] All 2 advanced topic pages are accessible

## Verification Steps
1. Run `mkdocs build --clean` locally to verify that the build succeeds
2. Check that `site/commands/files/index.html` is generated
3. Verify that `site/index.html` is generated
4. Test the local preview using `mkdocs serve`
5. Commit and push the changes to main
6. Verify that the GitHub Actions workflow completes successfully
7. Access `https://frankyxhl.github.io/fx_bin/` and verify that the documentation loads
8. Test the navigation to various pages (commands, use-cases, advanced)
9. Verify that all internal links work correctly
