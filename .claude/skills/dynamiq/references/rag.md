# RAG Components Reference

## Document Converters

### PyPDF Converter
```python
from dynamiq.nodes.converters import PyPDFConverter

converter = PyPDFConverter(
    document_creation_mode="one-doc-per-page"  # or "one-doc-per-file"
)
# Input: {"files": [BytesIO(pdf_data)]}
# Output: {"documents": [Document(...), ...]}
```

### Unstructured Converter
```python
from dynamiq.nodes.converters import UnstructuredConverter

converter = UnstructuredConverter(
    document_creation_mode="one-doc-per-element",
    converting_strategy="auto"  # "auto", "fast", "hi_res", "ocr_only"
)
# Supports: TXT, DOCX, XLSX, PPTX, HTML, XML, JSON, CSV
```

### LLM PDF Converter
```python
from dynamiq.nodes.converters import PyPDFConverter

converter = PyPDFConverter(
    document_creation_mode="one-doc-per-page",
    extraction_mode="layout"  # "plain" or "layout"
)
```

### PPTX Converter
```python
from dynamiq.nodes.converters.pptx import PPTXConverter

converter = PPTXConverter(
    document_creation_mode="one-doc-per-slide"  # or "one-doc-per-file"
)
```

## Document Splitter

```python
from dynamiq.nodes.splitters.document import DocumentSplitter

splitter = DocumentSplitter(
    split_by="sentence",     # "character", "word", "sentence", "page", "passage", "title"
    split_length=10,         # Number of units per chunk
    split_overlap=1          # Overlapping units between chunks
)
# Input: {"documents": [Document(...)]}
# Output: {"documents": [Document(...), ...]}  # Split documents
```

### Split Strategies

| Strategy | Best For |
|----------|----------|
| `sentence` | Prose text, articles |
| `character` | Fixed-size chunks |
| `word` | General purpose |
| `page` | Paginated content |
| `passage` | Logical sections |
| `title` | Structured documents |

## Embedders

### OpenAI Document Embedder
```python
from dynamiq.nodes.embedders import OpenAIDocumentEmbedder
from dynamiq.connections import OpenAI as OpenAIConnection

embedder = OpenAIDocumentEmbedder(
    connection=OpenAIConnection(api_key="OPENAI_API_KEY"),
    model="text-embedding-3-small",
    dimensions=1536  # Optional: specific dimensions
)
# Input: {"documents": [Document(...)]}
# Output: {"documents": [Document(embedding=[...]), ...]}
```

### OpenAI Text Embedder
```python
from dynamiq.nodes.embedders import OpenAITextEmbedder

text_embedder = OpenAITextEmbedder(
    connection=OpenAIConnection(api_key="OPENAI_API_KEY"),
    model="text-embedding-3-small"
)
# Input: {"query": "search text"}
# Output: {"embedding": [...], "query": "search text"}
```

### Other Embedders
- `CohereDocumentEmbedder` / `CohereTextEmbedder`
- `GeminiDocumentEmbedder` / `GeminiTextEmbedder`
- `BedrockDocumentEmbedder` / `BedrockTextEmbedder`
- `MistralDocumentEmbedder` / `MistralTextEmbedder`
- `HuggingFaceDocumentEmbedder` / `HuggingFaceTextEmbedder`

## Vector Stores

### Pinecone
```python
from dynamiq.nodes.writers import PineconeDocumentWriter
from dynamiq.nodes.retrievers import PineconeDocumentRetriever
from dynamiq.connections import Pinecone as PineconeConnection

conn = PineconeConnection(api_key="PINECONE_API_KEY")

# Writer
writer = PineconeDocumentWriter(
    connection=conn,
    index_name="default",
    dimension=1536,
    metric="cosine",
    namespace="production",
    batch_size=100,
    create_if_not_exists=True
)

# Retriever
retriever = PineconeDocumentRetriever(
    connection=conn,
    index_name="default",
    top_k=5,
    filters={"category": "docs"}
)
```

### Qdrant
```python
from dynamiq.nodes.writers import QdrantDocumentWriter
from dynamiq.nodes.retrievers import QdrantDocumentRetriever
from dynamiq.connections import Qdrant as QdrantConnection

conn = QdrantConnection(url="http://localhost:6333", api_key="optional")

writer = QdrantDocumentWriter(
    connection=conn,
    index_name="documents",
    dimension=1536,
    metric="cosine"
)

retriever = QdrantDocumentRetriever(
    connection=conn,
    index_name="documents",
    top_k=5
)
```

### Other Vector Stores
- `WeaviateDocumentWriter` / `WeaviateDocumentRetriever`
- `ChromaDocumentWriter` / `ChromaDocumentRetriever`
- `MilvusDocumentWriter` / `MilvusDocumentRetriever`
- `ElasticsearchDocumentWriter` / `ElasticsearchDocumentRetriever`
- `PGVectorDocumentWriter` / `PGVectorDocumentRetriever`
- `OpenSearchDocumentWriter` / `OpenSearchDocumentRetriever`

## Complete RAG Indexing Flow

```python
from io import BytesIO
from dynamiq import Workflow
from dynamiq.connections import OpenAI as OpenAIConnection, Pinecone as PineconeConnection
from dynamiq.nodes.converters import PyPDFConverter
from dynamiq.nodes.splitters.document import DocumentSplitter
from dynamiq.nodes.embedders import OpenAIDocumentEmbedder
from dynamiq.nodes.writers import PineconeDocumentWriter

rag_wf = Workflow()

# 1. Convert PDF
converter = PyPDFConverter(document_creation_mode="one-doc-per-page")
rag_wf.flow.add_nodes(converter)

# 2. Split documents
splitter = DocumentSplitter(
    split_by="sentence",
    split_length=10,
    split_overlap=1
).inputs(documents=converter.outputs.documents).depends_on(converter)
rag_wf.flow.add_nodes(splitter)

# 3. Embed documents
embedder = OpenAIDocumentEmbedder(
    connection=OpenAIConnection(api_key="KEY"),
    model="text-embedding-3-small"
).inputs(documents=splitter.outputs.documents).depends_on(splitter)
rag_wf.flow.add_nodes(embedder)

# 4. Store vectors
writer = PineconeDocumentWriter(
    connection=PineconeConnection(api_key="KEY"),
    index_name="default",
    dimension=1536
).inputs(documents=embedder.outputs.documents).depends_on(embedder)
rag_wf.flow.add_nodes(writer)

# Run indexing
rag_wf.run(input_data={
    "files": [BytesIO(open("document.pdf", "rb").read())],
    "metadata": [{"filename": "document.pdf"}]
})
```

## Complete RAG Retrieval Flow

```python
from dynamiq import Workflow
from dynamiq.connections import OpenAI as OpenAIConnection, Pinecone as PineconeConnection
from dynamiq.nodes.embedders import OpenAITextEmbedder
from dynamiq.nodes.retrievers import PineconeDocumentRetriever
from dynamiq.nodes.llms import OpenAI
from dynamiq.prompts import Prompt, Message

retrieval_wf = Workflow()

# 1. Embed query
embedder = OpenAITextEmbedder(
    connection=OpenAIConnection(api_key="KEY"),
    model="text-embedding-3-small"
)
retrieval_wf.flow.add_nodes(embedder)

# 2. Retrieve documents
retriever = PineconeDocumentRetriever(
    connection=PineconeConnection(api_key="KEY"),
    index_name="default",
    top_k=5
).inputs(embedding=embedder.outputs.embedding).depends_on(embedder)
retrieval_wf.flow.add_nodes(retriever)

# 3. Generate answer
prompt = Prompt(messages=[
    Message(content="""
Answer based on context:

Question: {{ query }}

Context:
{% for doc in documents %}
- {{ doc.content }}
{% endfor %}
""", role="user")
])

generator = OpenAI(
    connection=OpenAIConnection(api_key="KEY"),
    model="gpt-4o",
    prompt=prompt
).inputs(
    documents=retriever.outputs.documents,
    query=embedder.outputs.query
).depends_on([retriever, embedder])
retrieval_wf.flow.add_nodes(generator)

# Run retrieval
result = retrieval_wf.run(input_data={"query": "What is the document about?"})
print(result.output[generator.id]["output"]["content"])
```

## RAG Best Practices

| Setting | Recommendation |
|---------|----------------|
| Chunk size | 256-512 tokens |
| Chunk overlap | 10-20% |
| Top-k retrieval | Start with 5 |
| Search | Prefer hybrid (vector + BM25) |
| Embedding model | Match to your use case |
