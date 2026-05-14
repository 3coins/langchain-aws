---
name: pre-submit-check
description: Self-service validation for langchain-aws contributions. Checks code quality, test coverage, file placement, and CI readiness before submitting a PR. Use before opening a pull request to catch common issues early.
---

# Pre-Submit Check for langchain-aws

Run this skill before submitting a PR to validate your contribution meets repository standards.

## When to Use

- You've finished implementing a feature or fix and want to verify it's ready for review
- You want to catch issues that would delay the review process
- You're unsure if your tests are properly structured or gated

## Validation Workflow

1. **Run local checks** — Execute lint and tests locally
2. **Run structural validation** — Use the validation script to check file placement and test coverage
3. **Review the checklist** — See [references/CHECKLIST.md](references/CHECKLIST.md) for the full requirements
4. **Fix any issues** — Address failures before submitting

## Step 1: Run Local Checks

From the package directory (e.g., `libs/aws/`):

```bash
# Format code
make format

# Run linter + type checker
make lint

# Run unit tests
make test
```

All three must pass before submitting. CI will reject PRs that fail these.

## Step 2: Run Structural Validation

From the repo root:

```bash
python3 scripts/validate_contribution.py --repo-root .
```

Or check specific files:

```bash
python3 scripts/validate_contribution.py --repo-root . --changed-files libs/aws/langchain_aws/my_module.py
```

## Step 3: Review Checklist

See [references/CHECKLIST.md](references/CHECKLIST.md) for the complete checklist. Key items:

- PR title follows Conventional Commits format
- Unit tests exist for new code (mocked, no network calls)
- Integration tests are properly gated (won't break CI)
- Public methods have type hints and Google-style docstrings
- New classes are exported in `__init__.py`
- No breaking changes to public API
- PR description includes AI disclaimer if agents were used

## Available Scripts

- **`scripts/validate_contribution.py`** — Validates contribution readiness. Run with: `python3 scripts/validate_contribution.py --repo-root /path/to/langchain-aws`

## Reference Documents

- [CHECKLIST.md](references/CHECKLIST.md) — Complete contribution checklist
