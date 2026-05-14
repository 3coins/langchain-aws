# Integration Types

Guide for choosing the right base class and pattern for your AWS service integration.

## Decision Table

| Integration Type | Base Class | Directory | When to Use |
|-----------------|------------|-----------|-------------|
| Chat Model | `BaseChatModel` | `chat_models/` | Service generates conversational text responses |
| LLM | `BaseLLM` | `llms/` | Legacy text completion (prefer Chat Model for new work) |
| Retriever | `BaseRetriever` | `retrievers/` | Service retrieves documents from a data source |
| Vector Store | `VectorStore` | `vectorstores/` | Service stores and searches vector embeddings |
| Embeddings | `Embeddings` | `embeddings/` | Service generates vector embeddings from text |
| Tool | `BaseTool` | `tools/` | Single action an agent can invoke |
| Toolkit | `BaseToolkit` | `tools/` | Collection of related tools |
| Document Compressor | `BaseDocumentCompressor` | `document_compressors/` | Service reranks or filters documents |
| Runnable | `Runnable` | `runnables/` | Generic LangChain runnable wrapper |

## Chat Models

**Preferred approach:** Extend `ChatBedrockConverse` or use it directly with model-specific configuration.

**When to create a new chat model class:**
- The service is NOT accessible through Bedrock (e.g., SageMaker endpoints)
- The service requires a fundamentally different request/response format

**Do NOT create a new class when:**
- The model is available through Bedrock — use `ChatBedrockConverse(model="model-id")` instead
- You just need different default parameters — use a factory function or subclass with defaults

**Key patterns:**
- Implement `_generate` and `_stream` methods
- Support `bind_tools` for tool calling
- Handle `additional_model_request_fields` for provider-specific params
- Use `langchain_aws.utils.create_aws_client` for boto3 client creation

## Retrievers

**Base class:** `langchain_core.retrievers.BaseRetriever`

**Required method:** `_get_relevant_documents(query, *, run_manager) -> List[Document]`

**Key patterns:**
- Use `pydantic.model_validator(mode="after")` to create boto3 client
- Accept `region_name` and `credentials_profile_name` for AWS config
- Return `Document` objects with `page_content` and `metadata`
- Support filtering via typed filter models (see `SearchFilter` in bedrock retriever)

## Tools and Toolkits

**Single tool:** Subclass `langchain_core.tools.BaseTool`
- Define `name`, `description`, `args_schema`
- Implement `_run` method
- Optionally implement `_arun` for async

**Toolkit (multiple related tools):** Subclass `langchain_core.tools.BaseToolkit`
- Implement `get_tools() -> List[BaseTool]`
- Manage shared state (e.g., session, client) at toolkit level
- Individual tools reference the toolkit's shared resources

## Vector Stores

**Base class:** `langchain_core.vectorstores.VectorStore`

**Required methods:**
- `add_texts(texts, metadatas, **kwargs) -> List[str]`
- `similarity_search(query, k, **kwargs) -> List[Document]`

**Key patterns:**
- Use a subdirectory if the implementation needs multiple files (filters, schema, etc.)
- Support both sync and async operations where the service supports it
- Implement `from_texts` classmethod for convenience construction

## Embeddings

**Base class:** `langchain_core.embeddings.Embeddings`

**Required methods:**
- `embed_documents(texts: List[str]) -> List[List[float]]`
- `embed_query(text: str) -> List[float]`

**Key patterns:**
- Handle batching (AWS APIs often have batch size limits)
- Support async variants if the service supports it
- Normalize embeddings if the service doesn't do it automatically

## Document Compressors

**Base class:** `langchain_core.document_compressors.BaseDocumentCompressor`

**Required method:** `compress_documents(documents, query, **kwargs) -> List[Document]`

**Key patterns:**
- Used for reranking retrieved documents
- Return documents in relevance order with updated metadata (scores)

## Common Patterns Across All Types

### AWS Client Creation
```python
from langchain_aws.utils import create_aws_client

client = create_aws_client(
    "service-name",
    region_name=self.region_name,
    credentials_profile_name=self.credentials_profile_name,
)
```

### Optional Dependencies
If your integration needs packages beyond boto3:
```python
try:
    import optional_package
except ImportError:
    msg = (
        "Could not import optional_package. "
        "Install with: pip install langchain-aws[feature]"
    )
    raise ImportError(msg)
```

### Pydantic Model Configuration
```python
from pydantic import ConfigDict

class MyIntegration(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)
```
