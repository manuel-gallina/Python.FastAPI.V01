## 1. Dependencies & pyproject.toml

- [x] 1.1 Set `pyproject.toml` `version = "0.0.0"` (placeholder; real version baked into image via env var at publish time)
- [x] 1.2 Verify environment with `uv sync --locked`

## 2. Dagger CI Adaptation

- [x] 2.1 Add optional `version: Annotated[str | None, Doc(...)] = None` parameter to `publish_docker_image` in `.dagger/src/ci_pipeline/main.py`
- [x] 2.2 Update `publish_docker_image` body: resolve version from parameter or `pyproject.toml` fallback, then bake it into the container as `PROJECT__VERSION` env var
- [x] 2.3 Update the function docstring to document the new `version` parameter

## 3. Release Workflow

- [x] 3.1 Create `.github/workflows/release.yml` with trigger `on: push: branches: [main]` and `concurrency: release`
- [x] 3.2 Declare `permissions: contents: write` on the job (`GHCR_TOKEN` PAT carries its own package scope)
- [x] 3.3 Add checkout step with `fetch-depth: 0` (tag action needs full history)
- [x] 3.4 Add `mathieudutour/github-tag-action@v6.2` step with `default_bump: false` and `tag_prefix: ""`; capture `id: tag` to expose `new_tag` output
- [x] 3.5 Add conditional Dagger CLI install step gated on `steps.tag.outputs.new_tag != ''`
- [x] 3.6 Add conditional Docker publish step gated on `steps.tag.outputs.new_tag != ''`, calling `dagger call publish-docker-image --token env:GHCR_TOKEN --version ${{ steps.tag.outputs.new_tag }}`

## 4. Bootstrap & Verification

- [ ] 4.1 Create a `GHCR_TOKEN` repository secret — Classic PAT with `write:packages` scope — **required before merging**
- [ ] 4.2 Create an anchor Git tag (`0.0.0`) on current `main` HEAD so the tag action has a baseline — **must be done on `main` before this PR is merged**
- [ ] 4.3 Merge a `fix:` or `feat:` PR and confirm: correct tag created, image published to GHCR with version and `latest` tags, `PROJECT__VERSION` correct inside the container
- [ ] 4.4 Merge a `chore:` PR and confirm the release workflow exits successfully with no tag and no image published
