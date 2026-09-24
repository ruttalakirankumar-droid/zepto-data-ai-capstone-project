# Zepto Support Assistant

## Project Overview

This module implements a policy-aware customer support assistant for Zepto.

The system uses:

- 8 policy documents
- Sentence Transformers
- `all-MiniLM-L6-v2` embeddings
- ChromaDB vector database
- Semantic top-k retrieval
- Structured prompt template
- LangGraph `StateGraph`
- Pydantic structured output
- FastAPI
- Docker

The assistant supports two types of questions:

1. **Policy questions** → retrieve relevant policy documents and answer using retrieved context.
2. **General questions** → provide a direct answer without policy retrieval.

---

# Architecture

```text
Policy Documents
       |
       v
Document Loading
       |
       v
Chunking
       |
       v
all-MiniLM-L6-v2
       |
       v
ChromaDB
       |
       v
User Query
       |
       v
Intent Classification
       |
       +----------------------+
       |                      |
       v                      v
policy_question       general_question
       |                      |
       v                      v
ChromaDB Retrieval      Direct Answer
       |
       v
Retrieved Context
       |
       v
Structured Prompt
       |
       v
Mock/LLM Generation
       |
       v
Pydantic Validation
       |
       v
FastAPI /ask
```

---

# Project Structure

```text
support_assistant/
│
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
│
├── chroma_db/
├── ingest.py
├── retriever.py
├── prompt.py
├── graph.py
├── models.py
├── api.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# Policy Document Corpus

The support assistant uses 8 policy documents covering topics such as:

- Delivery policy
- Returns and refunds
- Membership tiers
- Order tracking
- Damaged or missing items
- Customer support
- Gift cards
- Other Zepto support policies

The documents are stored in the `docs/` directory.

---

# Embeddings

The project uses the Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

Each document is split into chunks and converted into vector embeddings.

These embeddings are stored in ChromaDB for semantic search.

---

# ChromaDB

ChromaDB is used as the vector database.

Collection name:

```text
support_docs
```

The ingestion pipeline stores:

- Document text
- Document ID
- Chunk ID
- Embeddings

The retrieval function is:

```python
retrieve_documents(query, top_k=3)
```

The system retrieves the top 3 relevant chunks for a policy question.

---

# Ingestion

The document ingestion pipeline is implemented in:

```text
ingest.py
```

Run ingestion using:

```bash
python support_assistant/ingest.py
```

The ingestion process:

1. Loads policy documents.
2. Splits documents into chunks.
3. Generates `all-MiniLM-L6-v2` embeddings.
4. Stores embeddings in ChromaDB.
5. Creates the `support_docs` collection.

The completed ingestion stored 16 document chunks.

---

# Retrieval

Retrieval is implemented in:

```text
retriever.py
```

The system converts the user query into an embedding and performs semantic similarity search in ChromaDB.

Example:

```python
results = retrieve_documents(
    query,
    top_k=3
)
```

The returned results contain:

- Document ID
- Chunk ID
- Document content
- Distance

---

# Prompt Design

The structured prompt follows this order:

1. Role
2. Context
3. Task
4. Format
5. Length

The prompt also contains:

### Negative Constraint

The assistant is instructed:

```text
Do not invent or assume any policy details.
```

### Few-Shot Example

The prompt includes an example showing how a policy question should be answered using retrieved policy context.

If the provided context is insufficient, the assistant is instructed to state that it does not have enough information in the provided policy documents.

---

# LangGraph Workflow

The workflow is implemented using LangGraph `StateGraph`.

The state uses:

```python
TypedDict
```

The graph contains three main nodes:

```text
classify_intent
retrieve_and_answer
direct_answer
```

### Policy Question

```text
User Query
    |
    v
classify_intent
    |
    v
policy_question
    |
    v
retrieve_and_answer
    |
    v
ChromaDB Retrieval
```

### General Question

```text
User Query
    |
    v
classify_intent
    |
    v
general_question
    |
    v
direct_answer
```

---

# Mock LLM Mode

The project supports:

```text
MOCK_LLM=1
```

This is the default mode for the local graded workflow.

No external LLM API key is required.

For policy questions, the mock response is generated from the retrieved context rather than using a fixed canned policy answer.

Example response format:

```text
Based on the retrieved context: <retrieved policy content>
```

---

# Pydantic Response

Structured responses are validated using Pydantic.

The response contains:

```text
answer
sources
confidence
```

Example:

```json
{
  "answer": "Based on the retrieved context: ...",
  "sources": [
    "doc_01::doc_01_chunk_0"
  ],
  "confidence": 1.0
}
```

The confidence value is constrained between:

```text
0.0 and 1.0
```

---

# FastAPI

The API is implemented in:

```text
api.py
```

Run locally using:

```bash
python -m uvicorn api:app --app-dir support_assistant --reload
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoint

## POST `/ask`

Request:

```json
{
  "query": "How much is the delivery fee below INR 149?"
}
```

The API validates the request and returns a structured `SupportResponse`.

---

# API Testing

Two API tests were successfully completed.

## Test 1: Policy Question

Request:

```json
{
  "query": "How much is the delivery fee below INR 149?"
}
```

Result:

```text
HTTP 200 OK
```

The response returned:

- Retrieved policy context
- Source document IDs
- Confidence score

## Test 2: General Question

Request:

```json
{
  "query": "What is artificial intelligence?"
}
```

Result:

```text
HTTP 200 OK
```

The general question was routed to the direct-answer node without policy retrieval.

---

# Docker

The application was successfully containerized using Docker.

## Docker Image Build

The Docker image was built using:

```bash
docker build -t zepto-support-assistant -f support_assistant/Dockerfile .
```

Build completed successfully.

Docker image:

```text
zepto-support-assistant:latest
```

## Docker Container

The container was successfully started using:

```bash
docker start zepto-support
```

Container status was verified using:

```bash
docker ps
```

The container was running successfully with:

```text
STATUS: Up
PORTS: 0.0.0.0:8000->8000/tcp
NAME: zepto-support
```

## Docker API Test

The FastAPI `/ask` endpoint was tested successfully inside the Docker container.

Test request:

```json
{
  "query": "How much is the delivery fee below INR 149?"
}
```

Result:

```text
HTTP 200 OK
```

The Dockerized application successfully:

- Started the FastAPI application
- Served the `/ask` endpoint
- Performed policy-document retrieval
- Returned retrieved document sources
- Returned a confidence score

---

# Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Embeddings | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Retrieval | Semantic top-k retrieval |
| Workflow | LangGraph |
| State | TypedDict |
| Validation | Pydantic |
| API | FastAPI |
| Containerization | Docker |
| Mock Mode | MOCK_LLM=1 |

---

# Data Flow

```text
Policy Documents
       ↓
Chunking
       ↓
Embedding Generation
       ↓
ChromaDB
       ↓
User Query
       ↓
Intent Classification
       ↓
Policy / General Routing
       ↓
Top-k Retrieval for Policy Questions
       ↓
Structured Prompt
       ↓
Mock/LLM Generation
       ↓
Pydantic Validation
       ↓
FastAPI Response
```

---

# Conclusion

The Zepto Support Assistant provides a policy-aware customer support workflow using semantic retrieval, ChromaDB, LangGraph, structured prompting, Pydantic validation, FastAPI, and Docker.

The policy retrieval workflow, general-question routing, API tests, Docker image build, Docker container execution, and Docker `/ask` endpoint were successfully tested.

# Optional Real-LLM Path

By default, `MOCK_LLM=1`, so no API key is required.

When `MOCK_LLM=0`, the `retrieve_and_answer` stage still performs document retrieval and builds the same structured prompt. It then uses the optional real-LLM generation path.

The real-LLM request includes bounded retry logic with up to 3 attempts and exponential backoff. If all attempts fail, the error is raised instead of returning a fabricated answer.

Environment variables:

- `MOCK_LLM=1` — default mock mode
- `OPENAI_API_KEY` — required only when `MOCK_LLM=0`
- `OPENAI_MODEL` — optional model configuration

The default graded workflow uses `MOCK_LLM=1` and does not require an external API key.