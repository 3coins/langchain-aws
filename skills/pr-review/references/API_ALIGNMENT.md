# API Alignment

How to verify that a PR correctly wraps an AWS service API.

## Verification Process

1. **Identify the AWS service** — Which boto3 client does this integration use?
2. **Check parameter names** — Do they match the boto3/AWS API parameter names?
3. **Check parameter types** — Are types correct (str vs list, required vs optional)?
4. **Check supported operations** — Does the integration expose the right subset of API operations?
5. **Check response handling** — Are responses parsed correctly?

## Common Mistakes

### Wrong parameter casing
AWS APIs use camelCase in the wire protocol but boto3 uses PascalCase for parameters:
```python
# Wrong — using wire protocol casing
client.invoke_model(modelId="...", contentType="...")

# Correct — using boto3 parameter names
client.invoke_model(modelId="...", contentType="...")
# Note: boto3 parameter names match the API docs, check the specific service
```

### Missing optional parameters
Contributors often implement only the parameters they need. Check if commonly-used optional parameters are exposed:
- Timeout/retry configuration
- Region override
- Custom endpoint URL
- Pagination parameters for list operations

### Incorrect types
- `str` vs `List[str]` for multi-value parameters
- `int` vs `float` for numeric parameters
- `Dict[str, Any]` vs typed dictionaries for complex parameters
- Optional parameters should use `Optional[T] = None`

### Hardcoded values that should be configurable
- Model IDs
- Region names
- Endpoint URLs
- Retry counts

## Bedrock-Specific Guidance

### Converse API (preferred) vs InvokeModel (legacy)

**ChatBedrockConverse** (preferred for new work):
- Uses the Bedrock Converse API (`bedrock-runtime.converse` / `converse_stream`)
- Unified interface across all providers (Anthropic, Cohere, Meta, Amazon, etc.)
- Supports tool calling, streaming, thinking/reasoning natively
- Parameters align with the [Converse API docs](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)

**ChatBedrock** (legacy):
- Uses `bedrock-runtime.invoke_model` / `invoke_model_with_response_stream`
- Provider-specific request/response formats
- Should NOT be used for new integrations unless there's a specific reason

### Multi-Provider Considerations

Bedrock Converse wraps multiple providers. When reviewing changes:
- Does the change work across providers or is it provider-specific?
- If provider-specific, is it properly gated (e.g., only for Anthropic models)?
- Are model-specific parameters handled via `additional_model_request_fields`?
- Does the change handle provider-specific response formats correctly?

### Model Profiles

The repo maintains model profiles in `libs/aws/langchain_aws/data/_profiles.py` that define capabilities per model. Changes to model support should check if profiles need updating.

## Knowledge Bases / Retriever API

- Uses `bedrock-agent-runtime.retrieve` or `retrieve_and_generate`
- Key parameters: `knowledgeBaseId`, `retrievalQuery`, `retrievalConfiguration`
- Filter expressions follow a specific syntax — verify against API docs

## AgentCore APIs

- Browser tools: `agentcore.create_browser_session`, navigation/interaction methods
- Code interpreter: `agentcore.create_code_interpreter_session`, execute methods
- Memory: `agentcore.create_memory`, session management
- These are newer APIs — verify against the latest AgentCore documentation

## Verification Checklist

- [ ] Parameter names match boto3 client method signatures
- [ ] Required vs optional parameters are correctly marked
- [ ] Default values are sensible and documented
- [ ] Error responses from the API are handled (not just happy path)
- [ ] Pagination is handled for list operations
- [ ] Streaming is implemented if the API supports it
- [ ] Region/endpoint configuration is exposed
- [ ] Credentials flow through correctly (boto3 session/client)
