# Repository Patterns

Module organization and naming conventions for langchain-aws.

## Package Structure

The repo is a monorepo with three packages under `libs/`:

| Package | Path | Purpose |
|---------|------|---------|
| langchain-aws | `libs/aws/` | Core LangChain integrations for AWS services |
| langgraph-checkpoint-aws | `libs/langgraph-checkpoint-aws/` | LangGraph checkpointing with AWS services |
| langchain-agentcore-codeinterpreter | `libs/agentcore-codeinterpreter/` | AgentCore Code Interpreter sandbox |

## Module Organization (libs/aws/langchain_aws/)

| Directory | Integration Type | Base Class |
|-----------|-----------------|------------|
| `chat_models/` | Chat model wrappers | `BaseChatModel` |
| `llms/` | LLM wrappers (legacy) | `BaseLLM` |
| `embeddings/` | Embedding models | `Embeddings` |
| `retrievers/` | Document retrievers | `BaseRetriever` |
| `vectorstores/` | Vector storage backends | `VectorStore` |
| `tools/` | Agent tools/toolkits | `BaseTool` / `BaseToolkit` |
| `agents/` | Agent wrappers | Custom (Bedrock Agents) |
| `graphs/` | Graph database integrations | Custom (Neptune) |
| `chains/` | QA chains | Custom (graph QA) |
| `middleware/` | Request/response middleware | Custom |
| `runnables/` | LangChain Runnables | `Runnable` |
| `document_compressors/` | Document reranking | `BaseDocumentCompressor` |
| `utilities/` | Shared utility code | N/A |
| `data/` | Static data (model profiles) | N/A |

## Naming Conventions

### Files
- Snake_case: `bedrock_converse.py`, `sagemaker_endpoint.py`
- Service-specific prefix: `bedrock.py`, `kendra.py`, `neptune_graph.py`
- Private helpers: `_anthropic_utils.py`, `_compat.py`

### Classes
- PascalCase with service name: `ChatBedrockConverse`, `AmazonKendraRetriever`
- Prefix with `Chat` for chat models: `ChatBedrock`, `ChatBedrockConverse`
- Prefix with `Bedrock`/`Amazon` for AWS services: `BedrockEmbeddings`, `AmazonKnowledgeBasesRetriever`

### Modules with subdirectories
Complex integrations use a subdirectory with `base.py`:
```
vectorstores/
├── __init__.py
├── inmemorydb/
│   ├── __init__.py
│   ├── base.py
│   ├── filters.py
│   ├── cache.py
│   └── schema.py
├── s3_vectors/
│   ├── __init__.py
│   └── base.py
└── valkey/
    ├── __init__.py
    ├── base.py
    └── filters.py
```

## Public API Exports

Every public class MUST be exported in the appropriate `__init__.py`:

1. **Module-level `__init__.py`** — Export from the module directory
2. **Package-level `__init__.py`** (`langchain_aws/__init__.py`) — Export from the top-level package

Check `libs/aws/langchain_aws/__init__.py` for the canonical list of public exports.

## Test Structure

Tests MUST mirror the source structure:

```
libs/aws/langchain_aws/chat_models/bedrock_converse.py
→ libs/aws/tests/unit_tests/chat_models/test_bedrock_converse.py
→ libs/aws/tests/integration_tests/chat_models/test_bedrock_converse.py
```

Rules:
- Test file name: `test_` + source file name
- Test directory mirrors source directory
- Each test directory has an `__init__.py`
- Unit tests: `tests/unit_tests/` (no network calls)
- Integration tests: `tests/integration_tests/` (network calls permitted)

## Samples and Notebooks

User-facing features should have:
- A sample notebook in `samples/` (organized by category: agents, memory, models, tools)
- Or a Jupyter notebook in `notebooks/` for more complex demonstrations

## Configuration Files

- `pyproject.toml` — Package metadata, dependencies, tool config (per package)
- `uv.lock` — Locked dependencies (per package)
- `Makefile` — Development commands (per package)
