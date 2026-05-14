# Common Issues

Patterns from historical PR reviews — things that frequently need correction.

## Streaming Serialization

**Problem:** Bedrock streams tool-use responses as incremental JSON string fragments. During streaming, `content[].tool_use.input` accumulates as a string, while `tool_calls[].args` is maintained as a dict.

**What to check:**
- Does the PR handle both string and dict forms of tool input?
- Is `parse_partial_json` used when converting string tool input to dict?
- Is the conversion happening at the right boundary (when sending to Bedrock, not in checkpoint layer)?

**Reference:** See `_lc_content_to_bedrock()` in `chat_models/bedrock_converse.py` for the correct pattern.

## Tool Calling Parameter Handling

**Problem:** Tool call parameters can arrive in different formats depending on the streaming state and provider.

**What to check:**
- Are tool call args handled as both `str` (during streaming accumulation) and `dict` (final state)?
- Is JSON parsing robust to partial/malformed JSON during streaming?
- Are tool names preserved correctly through the round-trip?
- CamelCase vs snake_case tool names — does the integration handle both?

## Missing Error Handling for boto3 Exceptions

**Problem:** Contributors often only implement the happy path without handling AWS service errors.

**What to check:**
- Are `botocore.exceptions.ClientError` caught and wrapped meaningfully?
- Are throttling errors (429) handled with appropriate messaging?
- Are validation errors from the API surfaced clearly to the user?
- Is there a catch for `EndpointConnectionError` (wrong region, service not available)?

**Expected pattern:**
```python
from botocore.exceptions import ClientError

try:
    response = client.converse(**params)
except ClientError as e:
    error_code = e.response["Error"]["Code"]
    if error_code == "ThrottlingException":
        msg = "Request throttled by Bedrock. Consider reducing request rate."
        raise ValueError(msg) from e
    raise
```

## Incorrect Content Type Handling

**Problem:** Bedrock Converse uses a specific content block format that differs from other LLM APIs.

**What to check:**
- Are content blocks correctly structured as `[{"text": "..."}, {"image": {...}}, ...]`?
- Is the conversion between LangChain message format and Bedrock content blocks correct?
- Are multi-modal inputs (images, documents) handled with correct MIME types?
- Is the `toolResult` content block format correct for tool responses?

## Breaking Public API

**Problem:** Contributors change method signatures without realizing they're breaking existing users.

**What to check:**
- Are any exported class/method signatures changed?
- Are parameter positions changed (positional args)?
- Are default values changed for existing parameters?
- Is a previously optional parameter now required?

**Rule:** New parameters MUST be keyword-only with defaults: `*, new_param: str = "default"`

## Missing __init__.py Exports

**Problem:** New classes are created but not exported, making them undiscoverable.

**What to check:**
- Is the new class added to the module's `__init__.py`?
- Is it added to the package-level `langchain_aws/__init__.py`?
- Are the `__all__` lists updated if they exist?

## Credential Handling

**Problem:** Hardcoded credentials or incorrect credential flow.

**What to check:**
- Are credentials passed through boto3 session (not hardcoded)?
- Is the `credentials_profile_name` parameter supported?
- Is `region_name` configurable?
- Does the integration respect `AWS_DEFAULT_REGION` and standard boto3 credential chain?
- No secrets in test files or example code

## Duplicate Functionality

**Problem:** Contributors implement something that already exists in the repo.

**Common duplicates to watch for:**
- Custom retry logic (boto3 already has retry configuration)
- Custom JSON parsing (use `langchain_core.utils.json.parse_partial_json`)
- Custom streaming accumulation (check existing patterns in bedrock_converse.py)
- Custom user-agent patching (already handled by `langchain_aws.utils`)

## Overly Complex PRs

**Problem:** PRs that do too many things at once, making review difficult.

**Signs:**
- Changes span multiple unrelated modules
- Mix of refactoring and new features
- Bug fix bundled with feature addition
- Formatting changes mixed with logic changes

**Action:** Request the PR be split into focused, reviewable chunks.

## Provider-Specific Code in Generic Paths

**Problem:** Code that only works for one Bedrock provider placed in the generic Converse path.

**What to check:**
- Is provider-specific logic gated behind model ID checks?
- Does it break other providers?
- Should it use `additional_model_request_fields` instead of modifying the core request?
- Is there a model profile that should be updated?
