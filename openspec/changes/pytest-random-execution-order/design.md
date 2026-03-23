## Context

The project uses `pytest` with `asyncio_mode = "auto"` across three test levels (unit, integration, acceptance). Currently tests always execute in the same deterministic order, which can hide implicit dependencies between test cases. The `pytest-randomly` plugin randomises test collection order using a seed that is printed to the console, making failures reproducible.

## Goals / Non-Goals

**Goals:**
- Add `pytest-randomly` as a dev dependency so all test runs use randomised order by default.
- Allow reproducing a specific run order by passing `--randomly-seed=<seed>` to pytest.

**Non-Goals:**
- Changing how tests are written or structured.
- Enforcing test isolation beyond what randomised ordering surfaces.
- Configuring a fixed seed in `pyproject.toml` (that would defeat the purpose).

## Decisions

### Use `pytest-randomly` over alternatives

`pytest-randomly` is the most widely adopted pytest plugin for this purpose (referenced in the issue). It integrates transparently — no test changes required — and prints the seed at the start of each run so failures are always reproducible. Alternatives such as `pytest-random-order` exist but are less maintained.

### Add as a dev/test dependency only

`pytest-randomly` is only needed during test execution and should not be included in the production package. It will be added under `[project.optional-dependencies]` or the equivalent uv dev-dependency group in `pyproject.toml`.

## Risks / Trade-offs

- **Newly exposed test failures** → Tests that relied on implicit ordering will now fail intermittently. This is expected and desirable — each failure should be fixed to make the test truly independent.
- **CI run time** → No impact; randomisation has negligible overhead.
- **Seed not pinned** → Each run uses a different seed, so two back-to-back runs may not reproduce the same failure. Mitigation: the seed is always printed; use `--randomly-seed=last` or the printed value to replay.
