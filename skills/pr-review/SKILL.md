---
name: pr-review
description: AI-assisted PR review for langchain-aws. Evaluates API alignment with AWS services, design decisions, repo organization patterns, and testing adequacy. Use when reviewing pull requests or changes to the langchain-aws repository.
---

# PR Review for langchain-aws

Use this skill when reviewing a pull request or set of changes to the langchain-aws repository.

## When to Use

- Reviewing a PR from a service team or external contributor
- Evaluating whether a proposed change aligns with repo patterns
- Assessing if test coverage is adequate given CI constraints
- Determining if an AWS API integration is correctly implemented

## Review Workflow

1. **Understand the change** — Read the PR description and diff to understand intent
2. **Check structure** — Run `scripts/check_structure.py` to verify file placement and test mirroring
3. **Verify API alignment** — See [references/API_ALIGNMENT.md](references/API_ALIGNMENT.md)
4. **Evaluate design** — See [references/DESIGN_PRINCIPLES.md](references/DESIGN_PRINCIPLES.md)
5. **Assess tests** — See [references/TESTING_GUIDE.md](references/TESTING_GUIDE.md)
6. **Provide feedback** — Structured review with clear accept/request-changes/reject recommendation

## Decision Framework

### Accept when:
- Change provides clear value (new integration, bug fix, performance improvement)
- Follows existing repo patterns (see [references/REPO_PATTERNS.md](references/REPO_PATTERNS.md))
- Has adequate test coverage (unit tests required, integration tests expected)
- Does not break public API
- API parameters align with the actual AWS service

### Request changes when:
- Good intent but implementation needs work
- Missing tests or tests aren't properly gated
- File placement or naming doesn't follow conventions
- API parameter names/types don't match AWS service API
- Missing docstrings or type hints on public methods

### Reject when:
- Fundamentally wrong approach that can't be fixed with iteration
- Breaks existing public API without justification
- Duplicates existing functionality
- Implements a non-GA API without coordination (embargoed features)

## Available Scripts

- **`scripts/check_structure.py`** — Validates file placement, test mirroring, and integration test gating. Run with: `python scripts/check_structure.py --repo-root /path/to/langchain-aws --changed-files file1.py file2.py`

## Reference Documents

- [REPO_PATTERNS.md](references/REPO_PATTERNS.md) — Module organization and naming conventions
- [API_ALIGNMENT.md](references/API_ALIGNMENT.md) — AWS API verification guidance
- [DESIGN_PRINCIPLES.md](references/DESIGN_PRINCIPLES.md) — Accept/reject criteria and design standards
- [TESTING_GUIDE.md](references/TESTING_GUIDE.md) — Testing requirements, layers, and CI constraints
- [COMMON_ISSUES.md](references/COMMON_ISSUES.md) — Patterns from historical PR reviews
