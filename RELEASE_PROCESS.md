# Release Process

This document describes how CatalogBuilder manages versioning, releases, and automatic version bumping.

## Overview

CatalogBuilder uses an automated release process that:
1. Requires all PRs to specify a version bump type
2. Validates that exactly one version bump option is selected
3. Automatically bumps the version when a PR is merged to main
4. Creates git tags that trigger the conda package build

## Version Scheme

CatalogBuilder uses **calendar versioning** with the format: `YYYY.MAJOR.MINOR`

- **YYYY (Year)**: Automatically set to the current year. Updates automatically on calendar year changes.
- **MAJOR**: Incremented for bug fixes, patches, and maintenance releases
- **MINOR**: Incremented for new features and backwards-compatible additions

### Examples
- `2026.0.0` → First release of 2026
- `2026.1.0` → First major version bump in 2026
- `2026.1.5` → Fifth minor version bump under major version 1

## Creating a Pull Request

When you create a PR to the `main` branch, the PR template will ask you to select a version bump type. **You must select exactly one option:**

### Version Bump Options

- **No version bump** - Select this for:
  - Documentation updates
  - Test improvements
  - Refactoring without functional changes
  - Code cleanup

- **Minor version** - Select this for:
  - Bug fixes and patches
  - Internal improvements
  - Maintenance releases
  - (Increments `2026.0.x`)

- **Major version** - Select this for:
  - New features
  - Backwards-compatible API additions
  - Enhancements to existing functionality
  - (Increments `2026.x.0`, resets minor to 0)

## Automated Workflow

### After Merge
When your PR is merged to `main`:
1. The `auto-version-bump` workflow runs
2. It reads your version bump selection from the PR body
3. **bumpversion** automatically:
   - Updates the version in `pyproject.toml`
   - Updates the version in `meta.yaml` (for conda)
   - Creates a commit with the new version
   - Creates a git tag with the version number (e.g., `2026.1.0`)
4. The commit and tag are pushed back to the repository

## Troubleshooting

### PR Validation Failed
**Problem**: You see "PR Validation Failed" comment

**Solution**:
1. Edit the PR description
2. Check the "Version Bump (Required)" section
3. Ensure you have selected exactly ONE checkbox
4. Save the changes

## Manual Version Bumping (Not Recommended)

If you need to manually bump the version:

```bash
# Bump major version
bumpversion major --config-file pyproject.toml

# Bump minor version
bumpversion minor --config-file pyproject.toml

# This will update both pyproject.toml and meta.yaml automatically
```

**Note**: This requires bumpversion to be installed locally:
```bash
pip install bumpversion
```

## Related Files

- [.github/pull_request_template.md](.github/pull_request_template.md) - PR template with version bump checkboxes
- [.github/workflows/validate-pr.yml](.github/workflows/validate-pr.yml) - Validates version bump selection
- [.github/workflows/auto-version-bump.yml](.github/workflows/auto-version-bump.yml) - Automatically bumps version after merge
- [.github/workflows/build-conda.yml](.github/workflows/build-conda.yml) - Builds conda package on version tags
- [pyproject.toml](pyproject.toml) - Bumpversion configuration
- [meta.yaml](meta.yaml) - Conda package metadata
