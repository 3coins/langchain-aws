# Testing Guide

Testing requirements, layers, and CI constraints for langchain-aws.

## Testing Layers

| Layer | Location | Runs in CI? | Purpose |
|-------|----------|-------------|---------|
| Standard conformance | `tests/unit_tests/test_standard.py` | ✅ Yes | LangChain ChatModel/Retriever API conformance |
| Unit tests (mocked) | `tests/unit_tests/` | ✅ Yes | Logic correctness, no network calls |
| Integration compile check | `tests/integration_tests/` | ⚠️ Compile only | Verifies tests parse/import correctly |
| Integration (provider) | `tests/integration_tests/` | ❌ No | Requires AWS access + model enablement |
| Integration (infra) | `tests/integration_tests/` | ❌ No | Requires provisioned resources (RDS, DynamoDB, etc.) |

## What's Required vs Expected

### Required (PR will not be merged without these)
- **Unit tests** for all new logic, using mocked boto3 responses
- Tests must be deterministic (no flaky tests)
- Tests must pass without network access
- Test file mirrors source file location

### Expected (strongly encouraged, may block merge)
- **Integration tests** that exercise the real API — even if they can't run in CI
- Integration tests properly gated so they don't break CI
- Edge case coverage (empty responses, errors, pagination)

### Nice-to-have
- Performance benchmarks for hot paths
- Sample notebooks demonstrating the feature

## CI Constraints

The CI environment (owned by LangChain team, not us):
- Has limited AWS access — not all Bedrock models are enabled
- Cannot provision infrastructure (no RDS, DynamoDB, Neptune, etc.)
- Cannot access AgentCore services
- Runs integration tests in **compile-only mode** (imports are checked, tests don't execute)

This means:
- Unit tests with mocks are the primary quality gate
- Integration tests serve as documentation and local validation
- Contributors must be able to run integration tests locally with their own AWS credentials

## Mocking Patterns

### Basic boto3 mock
```python
from unittest.mock import MagicMock, patch

@patch("langchain_aws.chat_models.bedrock_converse.boto3.Session")
def test_invoke(mock_session):
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client
    mock_client.converse.return_value = {
        "output": {"message": {"role": "assistant", "content": [{"text": "Hello"}]}},
        "usage": {"inputTokens": 10, "outputTokens": 5},
        "stopReason": "end_turn",
    }
    # ... test logic
```

### Using cassettes (VCR-style)
The repo uses compressed YAML cassettes in `tests/cassettes/`:
```python
import pytest
from tests.conftest import replay_cassette

@replay_cassette("test_my_feature.yaml.gz")
def test_my_feature():
    # Real API call recorded, replayed from cassette
    ...
```

### Mocking for streaming
```python
def mock_stream_response():
    """Mock a streaming Bedrock Converse response."""
    yield {"contentBlockStart": {"contentBlockIndex": 0, "start": {"text": ""}}}
    yield {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": "Hello"}}}
    yield {"messageStop": {"stopReason": "end_turn"}}
    yield {"metadata": {"usage": {"inputTokens": 10, "outputTokens": 5}}}
```

## Integration Test Gating

Integration tests MUST be gated so they don't execute in CI. Accepted patterns:

### Environment variable gate (preferred)
```python
import os
import pytest

@pytest.mark.skipif(
    not os.environ.get("AWS_ACCESS_KEY_ID"),
    reason="AWS credentials not available"
)
def test_bedrock_invoke():
    ...
```

### Marker-based skip
```python
import pytest

@pytest.mark.skip(reason="Requires provisioned DynamoDB table")
def test_dynamodb_checkpoint():
    ...
```

### Import skip
```python
import pytest

neptune = pytest.importorskip("gremlinpython")
```

### Conditional fixture
```python
@pytest.fixture
def bedrock_client():
    if not os.environ.get("AWS_DEFAULT_REGION"):
        pytest.skip("AWS region not configured")
    import boto3
    return boto3.client("bedrock-runtime")
```

## Multi-Provider Testing (Bedrock Converse)

Bedrock Converse wraps multiple providers. Testing considerations:

- **Unit tests**: Mock the Converse API response format (provider-agnostic)
- **Integration tests**: Test with specific models if available
- **Provider-specific behavior**: Gate behind model availability checks
- **Tool calling**: Test with models that support tools (Claude, Nova)
- **Streaming**: Test streaming with models that support it

Pattern for multi-model integration tests:
```python
MODELS_TO_TEST = [
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.amazon.nova-pro-v1:0",
]

@pytest.mark.parametrize("model_id", MODELS_TO_TEST)
@pytest.mark.skipif(not os.environ.get("AWS_ACCESS_KEY_ID"), reason="No AWS creds")
def test_invoke_with_model(model_id):
    ...
```

## Infra-Dependent Tests

For tests requiring provisioned infrastructure:

1. **Document what's needed** in a comment at the top of the test file:
```python
"""
Integration tests for DynamoDB checkpoint saver.

Requirements:
- AWS credentials with DynamoDB access
- Table: langchain-checkpoints (created by tests/cfn/dynamodb.yaml)
- Region: us-east-1
"""
```

2. **Gate on a specific env var** that indicates infra is available:
```python
@pytest.mark.skipif(
    not os.environ.get("DYNAMODB_TABLE_NAME"),
    reason="DynamoDB table not provisioned"
)
```

3. **Provide setup instructions** or CloudFormation/CDK templates where possible

## Requirements by Change Type

| Change Type | Unit Tests | Integration Tests | Conformance Tests |
|-------------|-----------|-------------------|-------------------|
| New chat model | Required (mocked) | Expected (gated) | Required (test_standard.py) |
| New retriever | Required (mocked) | Expected (gated) | N/A |
| New tool/toolkit | Required (mocked) | Expected (gated) | N/A |
| New vectorstore | Required (mocked) | Expected (gated) | N/A |
| Bug fix | Required (reproduces bug) | If applicable | N/A |
| New parameter | Required | If behavior changes | N/A |
| Performance improvement | Required (benchmarks) | Optional | N/A |

## Red Flags in PR Reviews

- ❌ No tests at all
- ❌ Integration tests that would run (and fail) in CI — missing skip/gate
- ❌ Tests that require secrets not available in CI
- ❌ Tests that import but don't actually test anything meaningful
- ❌ Only happy-path tests, no error handling coverage
- ⚠️ Unit tests that make real network calls (should be mocked)
- ⚠️ Integration tests without documentation of what infra is needed
