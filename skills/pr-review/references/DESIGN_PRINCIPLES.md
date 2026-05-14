# Design Principles

Decision framework for accepting, requesting changes, or rejecting PRs.

## Stable Public Interfaces

**CRITICAL:** Always preserve function signatures, argument positions, and names for exported/public methods.

Before approving changes to public APIs:
- Check if the function/class is exported in `__init__.py`
- Look for existing usage patterns in tests and examples
- New parameters MUST use keyword-only syntax: `*, new_param: str = "default"`
- Mark experimental features with docstring warnings

Ask: "Would this change break someone's code if they used it last week?"

## Accept When

1. **Clear value** — Solves a real problem (new integration, bug fix, performance improvement)
2. **Follows patterns** — File placement, naming, class hierarchy match existing code
3. **Adequate tests** — Unit tests with mocks (required), integration tests (expected)
4. **Non-breaking** — Public API unchanged, or new params are keyword-only with defaults
5. **API-aligned** — Parameter names/types match the actual AWS service API
6. **Well-documented** — Public methods have Google-style docstrings with type hints

## Request Changes When

1. **Good intent, needs work** — The feature makes sense but implementation has issues
2. **Missing tests** — No unit tests, or integration tests aren't properly gated
3. **Wrong location** — Files in the wrong directory or module
4. **API mismatch** — Parameter names don't match AWS API, wrong types
5. **Missing exports** — New public class not added to `__init__.py`
6. **Breaking change without justification** — Changed signature of existing public method
7. **Missing docstrings** — Public methods without documentation
8. **Overly broad scope** — PR does too many things; suggest splitting

## Reject When

1. **Fundamentally wrong approach** — Can't be fixed with iteration
2. **Breaks public API** — Removes or renames existing public methods without deprecation path
3. **Duplicates existing** — Functionality already exists in the repo
4. **Embargoed API without coordination** — Implements non-GA API without prior arrangement
5. **Security risk** — Uses `eval()`, `exec()`, `pickle` on user input, or bare `except:`
6. **Unmaintainable** — Adds significant complexity without clear ownership plan

## Design Decisions

### When to create a new module vs extend existing

**New module when:**
- It's a genuinely new AWS service integration
- The existing module would become too large (>1000 lines)
- The new functionality has a different lifecycle/ownership

**Extend existing when:**
- Adding a new method to an existing integration
- Adding support for a new parameter or feature of the same API
- Bug fix or performance improvement

### When to use inheritance vs composition

**Inheritance (subclass) when:**
- The new class IS-A variant of the parent (e.g., ChatBedrockConverse extends BaseChatModel)
- LangChain's type system requires it (retrievers, embeddings, etc.)

**Composition when:**
- The new functionality wraps or orchestrates existing components
- The relationship is HAS-A (e.g., a toolkit that contains multiple tools)

### Optional dependencies

If an integration requires packages beyond boto3:
- Add to `pyproject.toml` as optional dependency group
- Use lazy imports with clear error messages
- Document installation: `pip install langchain-aws[feature]`
- Example: tools require `[tools]` extra

### Error handling

- Never use bare `except:` — always catch specific exceptions
- Use a `msg` variable for error messages
- Wrap boto3 exceptions in meaningful LangChain exceptions where appropriate
- Include actionable information in error messages (what went wrong, what to do)

### Streaming

If the AWS API supports streaming:
- Implement both sync and async streaming
- Use `yield` for streaming responses
- Handle partial JSON in streaming tool calls (see bedrock_converse.py for patterns)
- Test streaming separately from non-streaming

## Code Quality Standards

- All public methods: type hints + Google-style docstrings
- Descriptive variable names (no single-letter except loop vars)
- Functions >20 lines: consider breaking up
- No commented-out code in PRs
- American English spelling in docs
