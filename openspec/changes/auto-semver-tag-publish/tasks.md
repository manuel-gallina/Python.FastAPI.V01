## 1. Dependencies & PSR Configuration

- [x] 1.1 Run `uv add --group dev python-semantic-release` to add the dependency and update `uv.lock` atomically
- [x] 1.2 Add `[tool.semantic_release]` configuration block to `pyproject.toml`: set
  `version_toml = ["pyproject.toml:project.version"]`, tag format (`{version}`), commit parser (angular), and `main` as
  the release branch (PSR ≥ v9 uses `version_toml`, not `version_variables`)
- [x] 1.3 Verify the environment with `uv sync --locked`

## 2. Dagger CI Adaptation

- [x] 2.1 Add optional `version: Annotated[str | None, Doc("explicit version tag to publish")] = None` parameter to
  `publish_docker_image` in `.dagger/src/ci_pipeline/main.py`
- [x] 2.2 Update `publish_docker_image` body: use `version` argument when provided; fall back to reading
  `pyproject.toml` when `None`
- [x] 2.3 Update the function docstring to document the new `version` parameter

## 3. Release Workflow

- [x] 3.1 Create `.github/workflows/release.yml` with trigger `on: push: branches: [main]` and `concurrency: release` to
  prevent parallel runs
- [x] 3.2 Declare `permissions: contents: write` and `packages: write` on the job
- [x] 3.3 Add checkout step with `fetch-depth: 0` and `token: ${{ secrets.GITHUB_TOKEN }}` (PSR needs full history to
  inspect commits)
- [x] 3.4 Add PSR step using `python-semantic-release/python-semantic-release@v10`, passing `github_token`, and
  capturing `id: release` to expose `released` and `version` outputs
- [x] 3.5 Add conditional Dagger CLI install step gated on `steps.release.outputs.released == 'true'`
- [x] 3.6 Add conditional Docker publish step gated on `steps.release.outputs.released == 'true'`, calling
  `dagger call publish-docker-image --token env:GITHUB_TOKEN --version ${{ steps.release.outputs.version }}` (PSR
  outputs version without `v` prefix, e.g. `0.2.0` — pass it as-is, no prefix needed)

## 4. Bootstrap & Verification

- [ ] 4.1 Create an anchor Git tag (e.g., `0.0.0`) on current `main` HEAD so PSR has a baseline to compute the first
  bump from — **this must be done on `main` before this change's PR is merged**; if omitted, PSR will create an
  unintended release on first run
- [ ] 4.2 Run `semantic-release version --noop` locally to verify the PSR configuration parses commits correctly and
  resolves the expected next version
- [ ] 4.3 Merge a `fix:` or `feat:` PR and confirm the full workflow completes: correct tag created, `pyproject.toml`
  bumped, image published to GHCR with version and `latest` tags
- [ ] 4.4 Merge a `chore:` PR and confirm the release workflow exits with success status and no tag, version bump, or
  Docker image is produced
