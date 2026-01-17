# Tasks: Fix MkDocs Configuration for Documentation Deployment

## Phase 1: Analysis and Verification

- [ ] **T1.1**: Verify current `mkdocs.yml` configuration
  - Check that `docs_dir` setting is NOT present
  - Confirm `use_directory_urls` is NOT set (using default `true`)
  - Note current directory structure and nav configuration
  - Document the misalignment between file location and nav paths

- [ ] **T1.2**: Verify documentation file locations
  - Confirm documentation files are in `docs/site/` directory
  - Verify that `docs/site/commands/files.md` exists
  - Check that nav references are correct relative paths

- [ ] **T1.3**: Understand MkDocs default behavior
  - Verify that MkDocs defaults to looking for files in `docs/`
  - Confirm that nav paths are resolved relative to `docs/`
  - Document that this causes file not found errors

## Phase 2: Local Build Testing

- [ ] **T2.1**: Install MkDocs locally (if not already installed)
  - Install using `pip install mkdocs-material` or use poetry
  - Verify MkDocs command is available

- [ ] **T2.2**: Run MkDocs build WITHOUT fix
  - Run `mkdocs build --clean`
  - Document any errors or warnings
  - Check if `site/commands/files/index.html` is generated
  - Verify that build fails or produces incomplete site

- [ ] **T2.3**: Run MkDocs build WITH fix (dry run)
  - Manually add `docs_dir: docs/site` to `mkdocs.yml`
  - Run `mkdocs build --clean`
  - Verify that build completes successfully
  - Check that `site/commands/files/index.html` is generated
  - Verify that all expected HTML files are created
  - Revert `mkdocs.yml` change (dry run only)

## Phase 3: Configuration Update

- [ ] **T3.1**: Update `mkdocs.yml` configuration
  - Add `docs_dir: docs/site` to mkdocs.yml
  - Ensure configuration is properly formatted (YAML)
  - Add comments explaining the setting if needed
  - Verify no syntax errors in configuration
  - Confirm that nav configuration does NOT need changes

- [ ] **T3.2**: Verify configuration change
  - Run `mkdocs build --clean` to verify build succeeds
  - Check that output is complete and correct
  - Test local preview with `mkdocs serve`
  - Access `http://localhost:8000/` in browser
  - Navigate to various pages to verify they load correctly

## Phase 4: Deployment

- [ ] **T4.1**: Commit configuration changes
  - Stage modified `mkdocs.yml`
  - Create commit with descriptive message
  - Example: `fix: Add docs_dir configuration to MkDocs`

- [ ] **T4.2**: Push to main branch
  - Push commit to origin/main
  - Verify push succeeds without errors
  - Confirm GitHub Actions workflow triggers

- [ ] **T4.3**: Monitor GitHub Actions deployment
  - Go to Actions tab in GitHub repository
  - Check "Deploy Documentation" workflow status
  - Verify that build completes successfully
  - Confirm that deployment to gh-pages branch succeeds
  - Wait for workflow to complete (typically 1-3 minutes)

## Phase 5: Verification

- [ ] **T5.1**: Test documentation URL access
  - Access home page: `https://frankyxhl.github.io/fx_bin/`
  - Verify page loads correctly
  - Check that navigation menu is visible and functional

- [ ] **T5.2**: Test command documentation pages
  - Access command pages via directory URLs:
    - `https://frankyxhl.github.io/fx_bin/commands/files/`
    - `https://frankyxhl.github.io/fx_bin/commands/size/`
    - `https://frankyxhl.github.io/fx_bin/commands/ff/`
    - `https://frankyxhl.github.io/fx_bin/commands/fff/`
    - `https://frankyxhl.github.io/fx_bin/commands/filter/`
    - `https://frankyxhl.github.io/fx_bin/commands/replace/`
    - `https://frankyxhl.github.io/fx_bin/commands/backup/`
    - `https://frankyxhl.github.io/fx_bin/commands/root/`
    - `https://frankyxhl.github.io/fx_bin/commands/today/`
    - `https://frankyxhl.github.io/fx_bin/commands/organize/`
  - Verify each page loads without 404 errors
  - Check that content is displayed correctly

- [ ] **T5.3**: Test use case documentation pages
  - Access use case pages via directory URLs:
    - `https://frankyxhl.github.io/fx_bin/use-cases/daily-workflow/`
    - `https://frankyxhl.github.io/fx_bin/use-cases/project-cleanup/`
    - `https://frankyxhl.github.io/fx_bin/use-cases/version-updates/`
    - `https://frankyxhl.github.io/fx_bin/use-cases/dataset-management/`
    - `https://frankyxhl.github.io/fx_bin/use-cases/automation-scripts/`
  - Verify each page loads without 404 errors
  - Check that content is displayed correctly

- [ ] **T5.4**: Test advanced topic documentation pages
  - Access advanced topic pages via directory URLs:
    - `https://frankyxhl.github.io/fx_bin/advanced/shell-integration/`
    - `https://frankyxhl.github.io/fx_bin/advanced/performance/`
  - Verify each page loads without 404 errors
  - Check that content is displayed correctly

- [ ] **T5.5**: Verify internal links and navigation
  - Click on navigation menu items
  - Verify all navigation links work correctly
  - Check that internal page links work
  - Verify that no broken links exist
  - Test breadcrumbs and back-to-top navigation

- [ ] **T5.6**: Verify trailing slash behavior
  - Test URLs without trailing slash: `https://frankyxhl.github.io/fx_bin/commands/files`
  - Test URLs with trailing slash: `https://frankyxhl.github.io/fx_bin/commands/files/`
  - Verify that both work (GitHub Pages should auto-redirect)

- [ ] **T5.7**: Final comprehensive verification
  - Access all 23 documentation pages
  - Verify no 404 errors on any page
  - Check that all content is displayed correctly
  - Verify that search functionality works (if configured)
  - Test responsive design on mobile (if configured)

## Phase 6: Documentation and Archive

- [ ] **T6.1**: Update project documentation (if needed)
  - Document that `docs_dir: docs/site` is required
  - Update any developer guides that reference MkDocs configuration
  - Ensure all documentation references are correct

- [ ] **T6.2**: Create spec delta for documentation capability
  - Create `openspec/changes/fix-docs-directory-urls/specs/documentation/spec.md`
  - Add MODIFIED requirements for MkDocs configuration correctness
  - Include scenarios for docs_dir configuration
  - Document expected behavior with correct configuration

- [ ] **T6.3**: Archive this change request
  - Move to `openspec/changes/archive/fix-docs-directory-urls/` directory
  - Update archive index if needed
  - Mark as completed in project tracking
  - Update task_plan.md if relevant

## Success Metrics

- MkDocs build completes successfully without errors
- All documentation pages are accessible via directory URLs
- No 404 errors on any documentation page
- GitHub Actions workflow completes successfully
- Documentation deploys to GitHub Pages without issues
- All internal links and navigation work correctly
- Backward compatibility maintained (if applicable)

## Estimated Effort

- **Phase 1**: 20 minutes (analysis and verification)
- **Phase 2**: 30 minutes (local build testing)
- **Phase 3**: 15 minutes (configuration update and local testing)
- **Phase 4**: 15 minutes (commit, push, and monitoring)
- **Phase 5**: 30 minutes (comprehensive verification)
- **Phase 6**: 20 minutes (documentation and archive)

- **Total**: ~130 minutes (2 hours 10 minutes)

## Risk Assessment

- **Low Risk**: Configuration change only, no code modifications
- **Low Risk**: Standard MkDocs configuration option
- **Low Risk**: Single line change, easy to verify
- **Low Risk**: Backward compatible (only fixes configuration)
- **Low Risk**: Easy rollback (remove docs_dir if needed)

## Rollback Plan

If issues arise:
1. Remove `docs_dir: docs/site` from `mkdocs.yml`
2. Commit and push changes
3. GitHub Actions will rebuild
4. Previous behavior restored (build failures may return)

Rollback time: ~5 minutes
