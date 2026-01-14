# Design: GitHub Pages Documentation Site

## Context

**Problem Statement:**
The fx-bin project currently relies on README.md as the primary documentation source. While comprehensive, it has limitations:
- Single-page format makes it difficult to organize and navigate content
- Lacks visual demonstrations of command usage
- No dedicated space for real-world use case scenarios
- Difficult to maintain as the project grows (currently 10+ commands)

**Stakeholders:**
- End users: Developers, DevOps engineers, data scientists, and system administrators
- Maintainers: Need maintainable documentation structure
- Contributors: Need clear documentation for contributing to the project

**Constraints:**
- Must be static site (no backend services)
- Deployed on GitHub Pages (free tier)
- Use existing Markdown documentation where possible
- Minimal maintenance overhead
- Fast loading times and good mobile UX

## Goals / Non-Goals

**Goals:**
1. Provide professional, searchable documentation for all fx-bin commands
2. Include comprehensive use case scenarios for real-world applications
3. Enable easy discovery of commands and their capabilities
4. Support responsive design for mobile, tablet, and desktop
5. Implement automated deployment via GitHub Actions
6. Maintain consistency with existing project documentation style

**Non-Goals:**
1. Interactive playground or sandbox environment
2. Multi-language support (initially English-only)
3. User authentication or community features
4. Backend services or databases
5. Video tutorials (can be added later as external links)

## Decisions

### Decision 1: Static Site Generator - MkDocs

**Choice:** MkDocs with Material Theme

**Rationale:**
- **Native Markdown support**: Project already uses Markdown extensively
- **Developer-friendly**: Simple configuration, easy to maintain
- **GitHub Pages native**: Well-documented deployment workflow
- **Feature-rich**: Built-in search, code highlighting, responsive design
- **Material Theme**: Professional appearance, excellent mobile support
- **Community support**: Active development, large plugin ecosystem

**Alternatives considered:**
1. **Jekyll**: GitHub Pages default, but requires learning Liquid templating
2. **Docusaurus**: Powerful but complex configuration, heavier setup
3. **Hugo**: Fast but steeper learning curve for Markdown-focused content
4. **Pure HTML/CSS**: Full control but high maintenance overhead

### Decision 2: Theme - Material Theme for MkDocs

**Choice:** Material Theme for MkDocs (v9.0+)

**Rationale:**
- **Modern design**: Clean, professional appearance suitable for developer tools
- **Out of the box features**: Search, navigation, code copy, dark mode
- **Customizable palette**: Supports brand colors (green for fx-bin)
- **Responsive**: Excellent mobile and tablet support
- **Accessibility**: WCAG AA compliant out of the box
- **Performance**: Minimal JavaScript, fast loading

**Color scheme:**
- Primary: `#2E7D32` (green) - represents safety and efficiency
- Accent: `#1976D2` (blue) - represents reliability and professionalism
- Background: `#FAFAFA` (light gray) - clean reading experience
- Code block: `#263238` (dark) - high contrast for code examples

### Decision 3: Content Organization Structure

**Choice:** Hierarchical structure with clear navigation

**Rationale:**
- **Logical grouping**: Commands grouped by functionality
- **Progressive disclosure**: Start with basics, move to advanced
- **Discoverable**: Users can find what they need quickly
- **Scalable**: Easy to add new content as project grows

**Structure:**
```
fx-bin Documentation
├── Home (index.md)
├── Quick Start
│   ├── Installation
│   └── First Steps
├── Commands
│   ├── fx files
│   ├── fx size
│   ├── fx ff
│   ├── fx fff
│   ├── fx filter
│   ├── fx replace
│   ├── fx backup
│   ├── fx organize
│   ├── fx root
│   └── fx today
├── Use Cases
│   ├── Daily Development Workflow
│   ├── Project Cleanup
│   ├── Version Updates
│   ├── Dataset Management
│   └── Automation Scripts
├── Advanced
│   ├── Shell Integration
│   └── Performance Optimization
└── Contributing
    ├── Development Setup
    ├── Testing
    └── Code Style
```

### Decision 4: Deployment Strategy - GitHub Actions

**Choice:** Automated deployment on push to main branch

**Rationale:**
- **Zero friction**: Updates deployed automatically on merge
- **Version control**: Deployed content is versioned with git
- **Reliable**: Proven GitHub Actions workflow with peaceiris/actions-gh-pages
- **Free**: No additional hosting costs
- **Fast**: Build and deploy in < 2 minutes

**Workflow trigger:** Push to `main` branch
**Deployment target:** `gh-pages` branch (GitHub Pages source)
**Build command:** `mkdocs build`
**Output directory:** `./site`

### Decision 5: Content Source Strategy

**Choice:** Create dedicated `docs/site/` directory for documentation source

**Rationale:**
- **Separation of concerns**: Distinguishes developer docs from user-facing documentation
- **Clean structure**: Avoids mixing internal project docs with public site docs
- **Future-proof**: Allows different maintenance lifecycles for each
- **Easy navigation**: Clear distinction between project internals and user guide

**Existing docs location:** `docs/` (developer-focused documentation)
**New docs location:** `docs/site/` (user-facing documentation site)

## Risks / Trade-offs

### Risk 1: Documentation Maintenance Overhead

**Risk:** Additional documentation increases maintenance burden

**Impact:** Medium
**Likelihood:** High

**Mitigation:**
- Establish documentation-first culture: Update docs with every code change
- Use code examples from actual test files to ensure accuracy
- Automate link validation in CI/CD pipeline
- Set up periodic documentation review schedule

### Risk 2: Outdated Content

**Risk:** Documentation becomes stale as features evolve

**Impact:** High (user experience)
**Likelihood:** Medium

**Mitigation:**
- Add documentation checks to PR review checklist
- Include code example verification in test suite
- Use automated link checking tools (e.g., markdown-link-check)
- Add "Last Updated" timestamps to each page

### Risk 3: Theme Updates Breaking Changes

**Risk:** Material Theme updates may break customizations

**Impact:** Low
**Likelihood:** Medium

**Mitigation:**
- Pin theme version in requirements.txt
- Test theme updates in development before deployment
- Document customizations in design.md
- Follow theme upgrade guides carefully

### Risk 4: GitHub Actions Deployment Failures

**Risk:** Automated deployment fails due to configuration or network issues

**Impact:** Medium (users see stale content)
**Likelihood:** Low

**Mitigation:**
- Monitor GitHub Actions workflow status
- Set up failure notifications via email/Slack
- Keep deployment workflow simple and well-tested
- Document manual deployment process as backup

### Risk 5: Mobile UX Degradation

**Risk:** Documentation site may not work well on mobile devices

**Impact:** Medium
**Likelihood:** Low (Material Theme handles this well)

**Mitigation:**
- Use Material Theme's responsive design features
- Test on actual mobile devices (iPhone, Android)
- Verify touch navigation works correctly
- Optimize images and code blocks for small screens

## Migration Plan

### Phase 1: Setup (Days 1-2)
1. Initialize MkDocs project
2. Configure Material Theme with custom palette
3. Set up GitHub Actions workflow
4. Test local build and deployment

### Phase 2: Core Content (Days 3-7)
1. Write homepage with hero section
2. Write quick start guide
3. Write command reference pages (10 commands)
4. Test local site and gather feedback

### Phase 3: Advanced Content (Days 8-10)
1. Write use case scenarios (5+ use cases)
2. Write shell integration guide
3. Write performance optimization tips
4. Add code examples from test files

### Phase 4: Quality Assurance (Days 11-12)
1. Local build testing
2. Link validation
3. Responsive design testing
4. Accessibility audit
5. Content review and proofreading

### Phase 5: Deployment (Days 13-14)
1. Configure GitHub repository settings
2. Merge feature branch to main
3. Monitor GitHub Actions deployment
4. Verify live site functionality

### Phase 6: Integration (Day 15)
1. Update README.md with documentation links
2. Update PyPI package metadata
3. Archive OpenSpec change
4. Announce documentation site release

### Rollback Plan
If deployment fails or site has critical issues:
1. Delete gh-pages branch
2. Disable GitHub Pages in repository settings
3. Investigate root cause in feature branch
4. Fix issues and retry deployment

## Open Questions

1. **Custom Domain**: Should we use a custom domain (e.g., fx-bin.dev) or stay with github.io?
   - **Current decision**: Use github.io initially, evaluate custom domain after 6 months
   - **Criteria**: Traffic analysis, community feedback, branding needs

2. **Multi-language Support**: Should we support languages beyond English?
   - **Current decision**: English-only for MVP
   - **Future consideration**: Internationalization after core site is stable

3. **Interactive Features**: Should we add command playground or sandbox?
   - **Current decision**: No (not in goals)
   - **Future consideration**: Evaluate user feedback and technical feasibility

4. **Documentation Metrics**: Should we track documentation usage with analytics?
   - **Current decision**: No (privacy-focused, free tier limitations)
   - **Future consideration**: GitHub Pages built-in analytics if needed

5. **User Contributions**: Should we allow community contributions to documentation?
   - **Current decision**: Yes, follow standard PR process
   - **Process**: PR review, maintain style consistency, verify code examples

## Appendix: Technical Specifications

### MkDocs Configuration
```yaml
site_name: fx-bin
site_url: https://frankyxhl.github.io/fx_bin/
site_description: A powerful, secure, and well-tested collection of Python file operation utilities
repo_url: https://github.com/frankyxhl/fx_bin
repo_name: frankyxhl/fx_bin

theme:
  name: material
  palette:
    primary: green
    accent: blue
    scheme: default
  features:
    - content.code.copy
    - navigation.instant
    - navigation.tracking
    - search.suggest
    - search.highlight
    - toc.integrate

plugins:
  - search
  - minify:
      minify_html: true

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
  - pymdownx.details
  - attr_list
  - md_in_html
```

### GitHub Actions Workflow
```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install mkdocs-material
      - run: mkdocs build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

### Directory Structure
```
docs/
├── site/                    # Documentation site source
│   ├── index.md             # Homepage
│   ├── quick-start/         # Quick start guide
│   ├── commands/            # Command reference
│   │   ├── files.md
│   │   ├── size.md
│   │   ├── ff.md
│   │   ├── fff.md
│   │   ├── filter.md
│   │   ├── replace.md
│   │   ├── backup.md
│   │   ├── organize.md
│   │   ├── root.md
│   │   └── today.md
│   ├── use-cases/          # Real-world scenarios
│   ├── advanced/           # Advanced topics
│   │   ├── shell-integration.md
│   │   └── performance.md
│   └── contributing/      # Contribution guide
├── testing/               # Developer docs (existing)
├── bdd-testing-guide.md   # Developer docs (existing)
└── ...                    # Other developer docs
```

### Content Template (Command Reference)
```markdown
# Command: fx files

## Overview
[Brief description of the command]

## Features
- Feature 1
- Feature 2
- Feature 3

## Usage
```bash
fx files [OPTIONS] [PATHS...]
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `--pattern` | string | `*` | Glob pattern to match files |
| `--exclude` | string | - | Pattern to exclude files |
| `--recursive` | flag | True | Search subdirectories |
| `--detailed` | flag | False | Show detailed statistics |

## Examples

### Basic Usage
```bash
fx files .              # Count files in current directory
fx files /path/to/dir   # Count files in specific directory
```

### Pattern Matching
```bash
fx files . --pattern "*.py"      # Count Python files only
fx files . --exclude "*test*"    # Exclude test files
```

### Real-World Scenarios
[3-5 detailed use cases]

## See Also
- [fx filter](filter.md) - Filter files by extension
- [fx size](size.md) - Analyze file sizes
```
