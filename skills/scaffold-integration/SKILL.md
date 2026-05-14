---
name: scaffold-integration
description: Generate boilerplate for new AWS service integrations in langchain-aws. Creates source files, unit tests, and integration tests with proper structure and gating. Use when adding a new AWS service integration to the repository.
---

# Scaffold Integration for langchain-aws

Use this skill when adding a new AWS service integration to the langchain-aws repository.

## When to Use

- Adding a new AWS service integration (retriever, tool, vectorstore, etc.)
- Creating a new chat model wrapper for a Bedrock provider
- Adding a new toolkit or tool for an AWS service

## Workflow

1. **Determine integration type** — What kind of LangChain component is this?
2. **Review similar implementations** — See [references/SIMILAR_IMPLEMENTATIONS.md](references/SIMILAR_IMPLEMENTATIONS.md)
3. **Generate boilerplate** — Use the templates in `assets/templates/`
4. **Fill in the implementation** — Replace TODOs with actual logic
5. **Run pre-submit checks** — Use the `pre-submit-check` skill before submitting

## Step 1: Determine Integration Type

Ask these questions:

| Question | If Yes → Type |
|----------|---------------|
| Does it generate text/chat responses? | Chat Model |
| Does it retrieve documents from a data source? | Retriever |
| Does it store/search vector embeddings? | Vector Store |
| Does it generate embeddings? | Embeddings |
| Does it provide a tool an agent can call? | Tool / Toolkit |
| Does it rerank/compress documents? | Document Compressor |

See [references/INTEGRATION_TYPES.md](references/INTEGRATION_TYPES.md) for detailed guidance on base classes and patterns.

## Step 2: Generate Files

Based on the integration type, create these files:

### For a Retriever (example: `my_service`)
```
libs/aws/langchain_aws/retrievers/my_service.py          # Implementation
libs/aws/tests/unit_tests/retrievers/test_my_service.py   # Unit tests (mocked)
libs/aws/tests/integration_tests/retrievers/test_my_service.py  # Integration tests (gated)
```

### For a Tool/Toolkit
```
libs/aws/langchain_aws/tools/my_service_tools.py
libs/aws/tests/unit_tests/tools/test_my_service_tools.py
libs/aws/tests/integration_tests/tools/test_my_service_tools.py
```

### For a Vector Store
```
libs/aws/langchain_aws/vectorstores/my_service/
├── __init__.py
├── base.py
libs/aws/tests/unit_tests/vectorstores/test_my_service.py
libs/aws/tests/integration_tests/vectorstores/test_my_service.py
```

## Step 3: Update Exports

After creating the implementation file:

1. Add imports to the module's `__init__.py` (e.g., `libs/aws/langchain_aws/retrievers/__init__.py`)
2. Add imports to the package's `__init__.py` (`libs/aws/langchain_aws/__init__.py`)

## Step 4: TODO Checklist After Scaffolding

After generating boilerplate, complete these items:

- [ ] Replace all `TODO` comments with actual implementation
- [ ] Verify parameter names match the AWS service API (boto3 client)
- [ ] Add proper error handling for boto3 exceptions
- [ ] Write meaningful unit tests with mocked boto3 responses
- [ ] Gate integration tests with `@pytest.mark.skipif`
- [ ] Add Google-style docstrings to all public methods
- [ ] Update `pyproject.toml` if new dependencies are needed
- [ ] Run `make format && make lint && make test` from `libs/aws/`
- [ ] Consider adding a sample notebook in `samples/`

## Templates

Use these templates as starting points. They follow current repo patterns:

- [retriever.py.tmpl](assets/templates/retriever.py.tmpl) — BaseRetriever subclass
- [tool.py.tmpl](assets/templates/tool.py.tmpl) — BaseTool subclass
- [unit_test.py.tmpl](assets/templates/unit_test.py.tmpl) — Unit test with mocked boto3
- [integration_test.py.tmpl](assets/templates/integration_test.py.tmpl) — Gated integration test

## Reference Documents

- [INTEGRATION_TYPES.md](references/INTEGRATION_TYPES.md) — Base classes and patterns per type
- [SIMILAR_IMPLEMENTATIONS.md](references/SIMILAR_IMPLEMENTATIONS.md) — Exemplar code to reference
