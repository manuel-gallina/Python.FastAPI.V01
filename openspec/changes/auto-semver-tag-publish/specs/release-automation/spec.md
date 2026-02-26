## ADDED Requirements

### Requirement: SemVer tag created on qualifying merge

When commits merged to `main` include at least one releasable type (`feat:`, `fix:`, or any commit with `BREAKING`), the
system SHALL determine the appropriate version bump (major / minor / patch), update the version in `pyproject.toml`,
push a version-bump commit to `main`, and create a corresponding SemVer Git tag (e.g., `1.2.0`).

#### Scenario: feat commit triggers minor bump

- **WHEN** a PR containing a `feat:` commit is merged to `main`
- **THEN** the minor version is incremented and a new Git tag is created (e.g., `0.2.0`)

#### Scenario: fix commit triggers patch bump

- **WHEN** a PR containing a `fix:` commit is merged to `main`
- **THEN** the patch version is incremented and a new Git tag is created (e.g., `0.1.1`)

#### Scenario: breaking change triggers major bump

- **WHEN** a PR containing a commit with `BREAKING` in its message is merged to `main`
- **THEN** the major version is incremented and a new Git tag is created (e.g., `1.0.0`)

#### Scenario: pyproject.toml version is updated

- **WHEN** a new SemVer tag is created
- **THEN** `pyproject.toml` version field SHALL reflect the new version and a commit with `[skip ci]` is pushed to
  `main`

### Requirement: Release workflow exits cleanly on non-releasable merge

When commits merged to `main` contain only non-releasable types (`chore:`, `docs:`, `refactor:`, `tests:`), the release
workflow SHALL exit successfully without creating a tag, bumping a version, or publishing a Docker image.

#### Scenario: chore-only merge produces no release

- **WHEN** a PR containing only `chore:` commits is merged to `main`
- **THEN** the release workflow completes with a success status and no tag or image is created

#### Scenario: docs-only merge produces no release

- **WHEN** a PR containing only `docs:` commits is merged to `main`
- **THEN** the release workflow completes with a success status and no tag or image is created

#### Scenario: non-releasable merge does not block future PRs

- **WHEN** the release workflow completes as a no-op
- **THEN** the workflow exits with a zero (success) exit code, and no required status check for PRs is affected

### Requirement: Docker image published to GHCR on new version tag

When a new SemVer Git tag is created by the release workflow, the system SHALL build the Docker image and publish it to
GHCR with two tags: the exact SemVer version without `v` prefix (e.g., `1.2.0`) and `latest`.

#### Scenario: image published with version and latest tags

- **WHEN** a new SemVer tag is created (e.g., `0.2.0`)
- **THEN** the Docker image is published to `ghcr.io/<owner>/python-fastapi-v01:0.2.0` (no `v` prefix)
- **THEN** the Docker image is also published to `ghcr.io/<owner>/python-fastapi-v01:latest`

#### Scenario: no image published on no-op release

- **WHEN** the release workflow determines no version bump is needed
- **THEN** the Docker publish step is skipped and no image is pushed to GHCR

### Requirement: Dagger publish function accepts explicit version parameter

The `publish_docker_image` Dagger function SHALL accept an optional `version` string parameter. When provided, the
supplied version SHALL be used as the published image tag instead of the version read from `pyproject.toml`. When
omitted, the function SHALL fall back to reading the version from `pyproject.toml`, preserving backward compatibility
for manual invocations.

#### Scenario: explicit version overrides pyproject.toml

- **WHEN** `publish_docker_image` is called with `--version 0.2.0`
- **THEN** the published image tags use `0.2.0` (no `v` prefix) regardless of the value in `pyproject.toml`

#### Scenario: omitting version falls back to pyproject.toml

- **WHEN** `publish_docker_image` is called without `--version`
- **THEN** the published image tags use the version read from `pyproject.toml`
