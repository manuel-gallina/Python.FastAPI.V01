## Why

Releasing a new version currently requires manually calling `dagger call publish-docker-image` with a registry token and
managing version numbers by hand. Automating SemVer tagging and Docker image publication on PR merge eliminates these
manual steps, ensures every merge to `main` produces a consistently versioned artifact in GHCR, and reduces the risk of
missed or inconsistent releases.

## What Changes

- New GitHub Actions workflow (`release.yml`) triggered on push to `main` that determines the next SemVer version,
  creates a Git tag, and publishes the Docker image to GHCR.
- `publish_docker_image` Dagger function is adapted to accept an explicit version string as input, decoupling the
  published tag from the static value in `pyproject.toml`.
- `pyproject.toml` version is updated automatically by the workflow as part of the release process.

## Capabilities

### New Capabilities

- `release-automation`: Automated SemVer versioning (Git tag creation) and Docker image publication to GHCR triggered on
  every merge to `main`.

### Modified Capabilities

_(none — no existing spec-level requirements are changing)_

## Impact

- `.github/workflows/release.yml` — new workflow file
- `.dagger/src/ci_pipeline/main.py` — `publish_docker_image` function signature and implementation adapted to accept an
  explicit version parameter and bake `PROJECT__VERSION` into the container image
- `pyproject.toml` — version field set to `0.0.0` placeholder; real version baked into the image at publish time via
  `PROJECT__VERSION` env var
- GitHub repository settings — requires `GITHUB_TOKEN` with `contents: write` (tags) and a `GHCR_TOKEN` repository
  secret (Classic PAT with `write:packages` scope) for GHCR authentication
    