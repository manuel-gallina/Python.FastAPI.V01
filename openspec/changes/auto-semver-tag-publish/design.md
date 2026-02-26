## Context

Currently, releasing a new version requires a developer to manually run
`dagger call publish-docker-image --token <secret>`. There is no automated versioning — `pyproject.toml` holds a static
dev version (`0.1.0-dev.1`) that is never updated programmatically.

Existing workflows (`style.yml`, `tests.yml`) run on pull requests targeting `main`. There is no `push`-to-main
workflow. The project's commit convention (`feat:`, `fix:`, `chore:`, etc. per `CLAUDE.md`) aligns with the Conventional
Commits standard, enabling automated version bump inference.

The Dagger `publish_docker_image` function currently reads the version from `pyproject.toml` at build time, tightly
coupling the published tag to the file's static content.

## Goals / Non-Goals

**Goals:**

- Automatically create a SemVer Git tag on every merge to `main`
- Automatically bump `pyproject.toml` version to match the new tag
- Automatically publish a Docker image to GHCR tagged with both the SemVer version and `latest`
- Decouple the Dagger publish function from `pyproject.toml` so it can accept an explicit version

**Non-Goals:**

- Creating GitHub Releases with changelogs (can be added later; out of scope here)
- Triggering on any branch other than `main`
- Changing the PR workflow (tests and style checks remain on pull requests)

## Decisions

### 1. Versioning tool: `python-semantic-release`

Use `python-semantic-release` (PSR) to drive the release process.

**Why PSR over alternatives:**

- Native Python tooling — no Node.js dependency added to the project
- Reads and writes `pyproject.toml` version directly
- Understands the project's existing commit convention (`feat:` → minor, `fix:` → patch, `BREAKING` → major, everything
  else → no release)
- Official GitHub Actions plugin available (`python-semantic-release/python-semantic-release`)
- Commits version bumps with `[skip ci]` by default, preventing trigger loops

**Alternatives considered:**

- `mathieudutour/github-tag-action` — simpler, language-agnostic, but does not update `pyproject.toml` and requires
  separate tooling for Docker publish coordination
- `semantic-release` (Node.js) — wider ecosystem, but introduces a Node.js runtime dependency

### 2. Dagger `publish_docker_image` adaptation

Add an optional `version: str | None = None` parameter to `publish_docker_image`. When provided, use it directly as the
version tag; when omitted, fall back to reading `pyproject.toml` (preserving backward compatibility for manual
invocations).

**Why:** The GitHub Actions workflow runs `dagger call publish-docker-image` after PSR has already bumped
`pyproject.toml`, so the fallback path remains correct. The explicit parameter is available as an escape hatch if
needed.

### 3. Workflow trigger and sequencing

The release workflow triggers on `push` to `main`. PSR is configured to:

1. Inspect commits since the last tag
2. Determine the version bump (or skip if no releasable commits)
3. Bump the version in `pyproject.toml` and push a commit tagged `[skip ci]`
4. Create and push the SemVer Git tag
5. Call `dagger call publish-docker-image` using `GITHUB_TOKEN` as the registry token

**Why not `workflow_run` gating on tests:** The `tests.yml` workflow already gates merging via branch protection rules.
A `push`-to-main trigger is sufficient and simpler.

### 4. Branch protection bypass for PSR push

PSR pushes a version-bump commit directly to `main` as part of the release process. The repository's branch protection rules (require PRs, require status checks) block direct pushes — including from `GITHUB_TOKEN` — unless an explicit bypass is configured.

**Decision:** Grant `github-actions[bot]` a bypass exception in the branch protection rules. This allows the PSR version-bump commit and tag push to succeed without changing the protection model for human contributors (PRs still required for everyone else).

**Alternatives considered:**
- PAT with admin rights — works, but introduces a long-lived credential to rotate and manage
- Skip version-bump commit (`commit = false` in PSR config) — avoids the push entirely, but `pyproject.toml` version would never be updated automatically

**Note:** PSR's version-bump commit message includes `[skip ci]` by default, preventing the push from re-triggering `release.yml`.

### 5. GHCR authentication

Use `GITHUB_TOKEN` as the registry token (with `packages: write` permission declared in the workflow). This avoids
managing a separate long-lived `GHCR_TOKEN` secret.

The existing Dagger function signature accepts `token: dagger.Secret` with `registry: str = "ghcr.io"` — no change
needed to the authentication interface; only the token source changes (from a manually supplied secret to
`secrets.GITHUB_TOKEN` in CI).

## Risks / Trade-offs

- **PSR commit loop**: PSR commits the version bump back to `main`. If `[skip ci]` is not correctly applied (e.g.,
  branch protection rules strip it), workflows could retrigger. → Mitigation: Verify `[skip ci]` behavior in the target
  repo; configure PSR's `commit_message` if needed.
- **No release on non-releasable commits**: Merges with only `chore:`, `docs:`, or `refactor:` commits will not produce
  a new tag or Docker image. → This is intentional and consistent with SemVer semantics. The `release.yml` workflow must
  exit cleanly (success) in this case so that PRs are never blocked by a skipped release. PSR's `--noop` / no-op exit
  code must be handled: the workflow should treat "nothing to release" as a successful no-op, not a failure.
- **First-run bootstrap**: PSR needs an existing Git tag to calculate the bump from. If no tag exists, it will create
  `0.1.0` as the initial release regardless of commits. → Create an initial `0.1.0-dev.1` tag (or `0.0.0` anchor tag)
  before enabling the workflow.
- **`pyproject.toml` version drift**: Until the first automated release runs, the file version (`0.1.0-dev.1`) will not
  match any tag. → Acceptable transitional state; resolved on first release.

## Migration Plan

1. Add `python-semantic-release` to `[dependency-groups] dev` in `pyproject.toml` and configure PSR settings in
   `pyproject.toml` (tag format, commit parser, version variable).
2. Adapt `publish_docker_image` in `.dagger/src/ci_pipeline/main.py` (add optional `version` parameter).
3. Create `.github/workflows/release.yml` — runs PSR then `dagger call publish-docker-image`.
4. Push an anchor tag (`0.0.0` or the current dev equivalent) to `main` before merging, to give PSR a starting point.
5. Merge to `main`; verify the workflow runs end-to-end on the next qualifying commit.

**Rollback:** Disable or delete `release.yml`. No application code is changed; the Dagger function change is backward
compatible.

## Open Questions

- Should non-releasable merges (e.g., `chore:` only) still publish a `latest` Docker image, or only when a new version
  tag is created? _(Decision: publish only on version tag creation. Non-releasable merges must still exit the workflow
  cleanly — see Risks above.)_
- Should `refactor:` and `tests:` commits count as patch bumps, or truly produce no release? _(Decision: no release,
  consistent with PSR defaults. All PRs remain mergeable regardless.)_
