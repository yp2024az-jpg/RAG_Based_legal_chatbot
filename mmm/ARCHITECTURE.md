# RAG-Based Legal Advisor Bot - Architecture Document

## System Overview

The RAG-Based Legal Advisor Bot is a sophisticated AI system designed to provide accurate, domain-specific legal information through a combination of Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs).

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
│                   (CLI / Web / API Endpoints)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   QUERY PROCESSING LAYER                        │
│  ┌────────────────┬───────────────────┬─────────────────────┐   │
│  │    Validator   │   Categorizer     │     Enricher       │   │
│  └────────────────┴───────────────────┴─────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼────────────────────┐    ┌──────────▼─────────────────┐
│   MEMORY LAYER            │    │   RAG PIPELINE              │
│  ┌─────────────────────┐  │    │  ┌──────────────────────┐  │
│  │ Short-Term Memory   │  │    │  │  Data Pipeline       │  │
│  │ (Session Context)   │  │    │  │ ┌──────────────────┐ │  │
│  └─────────────────────┘  │    │  │ │ Preprocessor    │ │  │
│  ┌─────────────────────┐  │    │  │ │ Chunker         │ │  │
│  │ Long-Term Memory    │  │    │  │ │ Embedder        │ │  │
│  │ (VectorDB + Cache)  │  │    │  │ └──────────────────┘ │  │
│  └─────────────────────┘  │    │  └──────────────────────┘  │
└───────▬────────────────────┘    │  ┌──────────────────────┐  │
        │                         │  │  Hybrid Retriever    │  │
        │                         │  │ ┌──────────────────┐ │  │
        │                         │  │ │ FAISS Retriever │ │  │
        │                         │  │ │ BM25 Retriever  │ │  │
        │                         │  │ └──────────────────┘ │  │
        │                         │  └──────────────────────┘  │
        └────────────────┬────────┤  ┌──────────────────────┐  │
                         │        │  │  Response Generator │  │
                         │        │  └──────────────────────┘  │
                         │        └──────────────────────────┘  │
                         │                                      │
        ┌────────────────▼──────────────────────────────────┐  │
        │         EXTERNAL SYSTEMS                          │  │
        │  ┌─────────────┐    ┌──────────────────────────┐ │  │
        │  │ Google Gemini│    │ Vector Databases        │ │  │
        │  │ LLM API      │    │ (FAISS / ChromaDB)      │ │  │
        │  └─────────────┘    └──────────────────────────┘ │  │
        └─────────────────────────────────────────────────────┘  │
```

## Core Components

### 1. Query Processing Layer

#### QueryValidator
- **Purpose**: Validates if queries are legal domain relevant
- **Key Features**:
  - Keyword-based validation
  - Validity score calculation (0-1)
  - Threshold-based filtering
  
#### QueryCategorizer
- **Purpose**: Classifies queries into categories
- **Supported Categories**:
  - Case Comparison
  - Case Summarization
  - Legal Data Retrieval
  - Similar Case Finding
  - Legal Advice
  - Invalid (error detection)
  
#### QueryEnricher
- **Purpose**: Enhances queries with context and metadata
- **Capabilities**:
  - Jurisdiction detection (India, US, UK, etc.)
  - Legal domain classification (Criminal, Civil, Corporate, etc.)
  - Named entity extraction (acts, cases, persons)
  - Key term identification

### 2. Data Pipeline Layer

#### DataPreprocessor
- Text cleaning and normalization
- Case citation standardization
- Duplicate removal
- Legal document formatting

#### DocumentChunker
- **Strategies**: Sentence-based, Paragraph-based
- Configurable chunk size (default: 512 chars)
- Overlap support for context preservation
- Metadata preservation

#### DocumentEmbedder
- Uses Sentence Transformers for embeddings
- Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
- Batch processing support
- Efficient encoding

### 3. Retrieval Layer (Hybrid)

#### FAISS Retriever
- Semantic similarity search
- Fast nearest neighbor lookup
- Support for L2 and IP metrics
- Efficient indexing for 100M+ vectors

#### BM25 Retriever
- Lexical/keyword-based matching
- TF-IDF based ranking
- Fast for exact term matching
- Complements semantic search

#### HybridRetriever
- Combines FAISS and BM25
- Configurable weights (default: FAISS 0.6, BM25 0.4)
- Re-ranking mechanism
- Optimal result quality

### 4. Memory Management

#### Short-Term Memory (STM)
- Session-based conversation history
- Configurable size (default: 10 turns)
- TTL-based expiration (default: 1 hour)
- Context window for response generation

#### Long-Term Memory (LTM)
- Persistent document embeddings
- Response caching with confidence scores
- Document metadata storage
- Efficient cache invalidation

### 5. LLM Integration

#### ResponseGenerator
- Google Generative AI (Gemini) backend
- Configurable parameters:
  - Temperature: 0.7 (balanced creativity)
  - Top-K: 40
  - Top-P: 0.95
  - Max tokens: 2048

#### PromptTemplates
- QA prompt engineering
- Case comparison prompts
- Summarization prompts
- Legal advice prompts

## Data Flow

### Query Processing Flow
```
User Query
    │
    ├─→ QueryValidator (Validate domain relevance)
    │     │
    │     └─→ If invalid: Return error response
    │
    ├─→ QueryCategorizer (Classify query type)
    │
    ├─→ QueryEnricher (Extract metadata)
    │
    ├─→ Check LTM Cache (Query hash lookup)
    │     │
    │     ├─→ If found & high confidence: Return cached response
    │     │
    │     └─→ If not found: Continue...
    │
    ├─→ Generate Query Embedding
    │
    ├─→ HybridRetrieval:
    │     ├─→ FAISS Search (semantic)
    │     └─→ BM25 Search (lexical)
    │         │
    │         └─→ Combine & Re-rank results
    │
    ├─→ LLM Response Generation (context + query)
    │
    ├─→ Store in STM (session history)
    │
    └─→ Cache in LTM (future reference)
         │
         └─→ Return final response
```

### Data Ingestion Flow
```
Raw Legal Documents
    │
    ├─→ DataPreprocessor (Clean & normalize)
    │
    ├─→ DocumentChunker (Split into chunks)
    │
    ├─→ DocumentEmbedder (Generate embeddings)
    │
    ├─→ Store in Retrievers:
    │     ├─→ FAISS Index (semantic search)
    │     └─→ BM25 Index (lexical search)
    │
    └─→ Store in LTM (metadata & documents)
```

## Configuration

### Key Parameters
```python
# Query Processing
- min_query_length: 5 characters
- legal_keyword_threshold: ≥1 keyword or 30% density

# Data Pipeline
- chunk_size: 512 characters
- chunk_overlap: 50 characters
- embedding_model: sentence-transformers/all-MiniLM-L6-v2
- embedding_dimension: 384

# Retrieval
- hybrid_method: FAISS (0.6) + BM25 (0.4)
- top_k_results: 5 documents

# Memory
- stm_max_size: 10 turns
- stm_ttl: 3600 seconds
- ltm_cache_ttl: 30 days

# LLM
- model: gemini-pro
- temperature: 0.7
- max_tokens: 2048
```

## Query Categories Detail

### 1. Case Comparison
**Detection Keywords**: compare, versus, vs, difference, contrast, similar, distinguish
**Example**: "Compare the ruling in Case X vs Case Y"
**Prompt Type**: Comparative analysis

### 2. Case Summarization
**Detection Keywords**: summarize, summary, overview, explain, describe, details
**Example**: "Summarize the landmark judgment in this case"
**Prompt Type**: Extractive summarization

### 3. Legal Data Retrieval
**Detection Keywords**: penalty, punishment, fine, section, article, provision, law, act
**Example**: "What are the penalties under Section 420 IPC?"
**Prompt Type**: Factual retrieval

### 4. Similar Case Finding
**Detection Keywords**: similar, like, analogous, precedent, related, comparable
**Example**: "Find cases similar to the one I'm studying"
**Prompt Type**: Semantic similarity

### 5. Legal Advice
**Detection Keywords**: should, can i, advice, help, liable, responsible, what if
**Example**: "What should I do in this legal situation?"
**Prompt Type**: Advisory/guidance

## Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Query Validation | < 50ms | Keyword-based |
| Query Categorization | < 50ms | Pattern matching |
| Embedding Generation | < 500ms | Batch processing |
| FAISS Search | < 200ms | 100M vectors |
| BM25 Search | < 300ms | Full corpus |
| LLM Response | < 3s | API latency dependent |
| Total End-to-End | < 5s | Average response time |

## Scalability Considerations

1. **Vector Index**: FAISS supports 100M+ document vectors
2. **Memory Management**: LTM can cache 1000s of responses
3. **Concurrent Users**: Session management supports multiple parallel queries
4. **Document Processing**: Batch processing for efficient ingestion
5. **Cache Strategy**: Smart invalidation prevents stale responses

## Security & Privacy

1. **API Key Management**: Stored in .env (never in code)
2. **Data Validation**: Input sanitization for all queries
3. **Query Logging**: Audit trail in logs/
4. **Session Isolation**: Independent STM per session
5. **Cache Isolation**: Query hashing for privacy

## Integration Points

### External APIs
- Google Generative AI (LLM)
- Sentence Transformers (Embeddings)
- FAISS (Vector Search)
- BM25 (Lexical Search)

### Database Connections
- FAISS Index (local/network)
- ChromaDB (optional vector DB)
- MongoDB (optional document storage)

### Future Extensions
- Multi-LLM support
- Fine-tuned legal models
- Real-time case law updates
- Citation validation
- Multi-language support
