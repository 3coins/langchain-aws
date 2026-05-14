# Contribution Checklist

Complete checklist for langchain-aws contributions. All "Required" items must pass for merge.

## PR Title (Required)

Format: `<type>(<scope>): <description>`

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `release`

Allowed scopes: `aws`, `langgraph-checkpoint-aws`, `agentcore-codeinterpreter`, `model-profiles`

Examples:
- `feat(aws): add support for Nova Sonic streaming`
- `fix(aws): handle empty tool call responses in Converse API`
- `docs: update retriever usage examples`

## Code Quality (Required)

- [ ] All public methods have type hints (parameters and return types)
- [ ] All public methods have Google-style docstrings
- [ ] No bare `except:` clauses — catch specific exceptions
- [ ] Error messages use a `msg` variable: `msg = "..."; raise ValueError(msg)`
- [ ] No `eval()`, `exec()`, or `pickle` on user-controlled input
- [ ] No commented-out code
- [ ] American English spelling in documentation

## Testing (Required)

- [ ] Unit tests exist for all new logic (`tests/unit_tests/`)
- [ ] Unit tests use mocked responses (no network calls)
- [ ] Tests are deterministic (no flaky tests)
- [ ] Test file mirrors source file location (`langchain_aws/foo/bar.py` → `tests/unit_tests/foo/test_bar.py`)

## Testing (Expected)

- [ ] Integration tests exist (`tests/integration_tests/`)
- [ ] Integration tests are properly gated with one of:
  - `@pytest.mark.skipif(not os.environ.get("AWS_ACCESS_KEY_ID"), ...)`
  - `@pytest.mark.skip(reason="Requires provisioned infrastructure")`
  - `pytest.importorskip("optional_dependency")`
- [ ] Edge cases covered (empty responses, errors, pagination)
- [ ] For new chat models: conformance test in `test_standard.py`

## File Organization (Required)

- [ ] Source files in correct module directory (see REPO_PATTERNS.md)
- [ ] New public classes exported in module `__init__.py`
- [ ] New public classes exported in `langchain_aws/__init__.py`
- [ ] Test directory has `__init__.py`

## Public API (Required)

- [ ] No breaking changes to existing public method signatures
- [ ] New parameters are keyword-only with defaults: `*, param: str = "default"`
- [ ] Deprecated methods marked with warnings (not removed)

## Documentation (Expected)

- [ ] Docstrings explain "why" not just "what"
- [ ] Complex logic has inline comments
- [ ] For user-facing features: sample notebook in `samples/`

## PR Description (Required)

- [ ] Describes the "why" of the changes
- [ ] Highlights areas requiring careful review
- [ ] Includes AI disclaimer if agents were used in the contribution
- [ ] References related issues (if applicable)

## Dependencies (If Applicable)

- [ ] New dependencies added to `pyproject.toml` with version constraints
- [ ] Optional dependencies use extras groups (e.g., `[tools]`)
- [ ] `uv.lock` updated (`uv lock`)
- [ ] Lazy imports with clear error messages for optional deps

## Before Submitting

```bash
# From the package directory (e.g., libs/aws/)
make format    # Fix formatting
make lint      # Check lint + types
make test      # Run unit tests
```

All three must pass. CI will reject PRs that fail these checks.
