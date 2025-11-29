# RAG-Based Legal Advisor Bot - System Diagrams & Flowcharts

## 1. Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                            │
│  ┌──────────────────────┐        ┌─────────────────────────────────┐    │
│  │  CLI Interface       │        │  REST API (Flask)              │    │
│  │  (main.py)          │        │  - Chat endpoint               │    │
│  │  - Interactive chat │        │  - Session management          │    │
│  │  - Sessions         │        │  - History retrieval           │    │
│  │  - Demo queries     │        │  - Statistics                  │    │
│  └──────────────────────┘        └─────────────────────────────────┘    │
└────────────┬─────────────────────────────────┬─────────────────────────┘
             │                                 │
             └─────────────────┬───────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────────────────┐
│                     LEGAL ADVISOR CHATBOT CORE                           │
│              (src/core/chatbot.py - LegalAdvisorBot)                    │
└──────────────────────────────┬────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ QUERY PROCESSOR │  │  RAG PIPELINE    │  │  MEMORY MANAGEMENT   │
│ (query_process) │  │  (rag_pipeline)  │  │  (memory)           │
└─────────────────┘  └──────────────────┘  └──────────────────────┘
        │                    │                      │
        ├─Validator         ├─Data Pipeline       ├─STM
        ├─Categorizer       ├─Retrieval           ├─LTM
        └─Enricher          ├─LLM Generator
                            └─Memory Integration
```

## 2. Query Processing Flow

```
                    USER QUERY
                        │
                        ▼
                ┌───────────────────┐
                │  QueryValidator   │
                │ (Legal domain?)   │
                └───────┬───────────┘
                        │
                    ┌───┴───┐
                    │       │
              Invalid   Valid
                    │       │
                    │       ▼
                    │  ┌──────────────────┐
                    │  │ QueryCategorizer │
                    │  │ (Classify type)  │
                    │  └────────┬─────────┘
                    │           │
                    │      ┌────┴──────┬────────────────────┐
                    │      │           │                    │
                    │   Category  Confidence          Alternates
                    │      │           │                    │
                    │      ▼           │                    │
                    │  ┌──────────────────┐               │
                    │  │ QueryEnricher    │               │
                    │  │ - Jurisdiction   │               │
                    │  │ - Domain         │               │
                    │  │ - Entities       │               │
                    │  │ - Key terms      │               │
                    │  └────────┬─────────┘               │
                    │           │                        │
                    ▼           ▼                        ▼
                ERROR      ENRICHED QUERY          ALTERNATIVE
                RESPONSE   (Ready for RAG)         CATEGORIES
```

## 3. Data Pipeline Flow

```
RAW LEGAL DOCUMENTS
        │
        ▼
┌─────────────────────────────┐
│   DataPreprocessor          │
│ • Remove whitespace         │
│ • Normalize citations       │
│ • Clean text                │
│ • Remove duplicates         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   DocumentChunker           │
│ • Sentence/paragraph split  │
│ • Configurable size         │
│ • Overlap preservation      │
│ • Metadata attachment       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  DocumentEmbedder           │
│ • Sentence Transformers     │
│ • 384-dim vectors           │
│ • Batch processing          │
│ • Caching                   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   Index Storage             │
├─ FAISS Index (384-dim)      │
├─ BM25 Index (tokenized)     │
├─ Metadata Mappings         │
└─ Document Chunks (CSV)      │
           │
           ├─ Local Files
           ├─ Vector DB
           └─ Metadata DB
```

## 4. Hybrid Retrieval System

```
                    QUERY
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
    ┌────────────┐            ┌──────────────┐
    │ FAISS      │            │ BM25         │
    │ RETRIEVER  │            │ RETRIEVER    │
    └─────┬──────┘            └────────┬─────┘
          │                            │
          │ Query Embedding           │ Tokenization
          │ (384-dim vector)          │ (TF-IDF)
          │                            │
          ▼                            ▼
    ┌────────────────────┐    ┌─────────────────────┐
    │ Index.search()     │    │ Index.get_scores()  │
    │ k=5 results        │    │ k=5 results         │
    │ L2 distance        │    │ BM25 scores         │
    └─────────┬──────────┘    └──────────┬──────────┘
              │                          │
              ▼                          ▼
        ┌──────────────┐         ┌──────────────────┐
        │ Similarity   │         │ Raw BM25         │
        │ Scores       │         │ Scores           │
        │ [0.95...]    │         │ [2.45...]        │
        └──────┬───────┘         └─────────┬────────┘
               │                           │
               │ Normalize (0-1)          │ Normalize (0-1)
               │                           │
               ▼                           ▼
        ┌──────────────┐         ┌──────────────────┐
        │ FAISS Score  │         │ BM25 Score       │
        │ × 0.6        │         │ × 0.4            │
        └──────┬───────┘         └─────────┬────────┘
               │                           │
               └───────────┬───────────────┘
                           │
                           ▼
                    ┌─────────────────────┐
                    │ COMBINED SCORE      │
                    │ = (FAISS × 0.6) +   │
                    │   (BM25 × 0.4)      │
                    └────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ FINAL RANKING       │
                    │ Sort by score       │
                    │ Return top-k (3-5)  │
                    └────────┬────────────┘
                             │
                             ▼
                    RETRIEVED DOCUMENTS
                    (Most relevant first)
```

## 5. LLM Integration & Response Generation

```
ENRICHED QUERY + RETRIEVED DOCS
            │
            ▼
    ┌──────────────────────────┐
    │ SELECT PROMPT TEMPLATE   │
    │ Based on query category  │
    └───────┬──────────────────┘
            │
    ┌───────┴─────────────────────────────────┐
    │                                         │
    ├─ CASE_COMPARISON                      │
    │  "Compare the following cases..."      │
    │                                         │
    ├─ CASE_SUMMARIZATION                   │
    │  "Summarize this legal ruling..."      │
    │                                         │
    ├─ LEGAL_DATA_RETRIEVAL                 │
    │  "Based on this legal information..."  │
    │                                         │
    ├─ SIMILAR_CASE_FINDING                 │
    │  "Find similar cases to..."            │
    │                                         │
    └─ LEGAL_ADVICE                         │
       "Provide guidance based on..."        │
            │
            ▼
    ┌──────────────────────────┐
    │ CONSTRUCT PROMPT         │
    │ • System instructions    │
    │ • Retrieved context      │
    │ • Query                  │
    │ • Few-shot examples      │
    └───────┬──────────────────┘
            │
            ▼
    ┌──────────────────────────────┐
    │ CALL GOOGLE GEMINI LLM       │
    │ • Model: gemini-pro          │
    │ • Temperature: 0.7           │
    │ • Max tokens: 2048           │
    │ • Top-p: 0.95                │
    └───────┬──────────────────────┘
            │
            ▼
    ┌──────────────────────────┐
    │ LLM RESPONSE             │
    │ • Generated text         │
    │ • Source citations       │
    │ • Confidence signal      │
    └───────┬──────────────────┘
            │
            ▼
    ┌──────────────────────────┐
    │ POST-PROCESS             │
    │ • Verify against sources │
    │ • Add source attr.       │
    │ • Confidence scoring     │
    │ • Grounding checks       │
    └───────┬──────────────────┘
            │
            ▼
    FINAL LEGAL ANSWER
    (Sourced, verified, grounded)
```

## 6. Memory System Architecture

```
                    SESSION
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌─────────┐  ┌────────────┐  ┌─────────┐
    │   STM   │  │ STM Meta   │  │   LTM   │
    │ History │  │  (Metadata)│  │  Cache  │
    └────┬────┘  └────┬───────┘  └────┬────┘
         │             │              │
         │ (Last 10)   │ (User data)   │ (Global)
         │             │              │
         ▼             │              ▼
    ┌─────────────────┐│      ┌──────────────────┐
    │ Turn 1: Query   ││      │ Response Cache   │
    │ Turn 1: Response││      │ • Query hash     │
    │ Turn 2: Query   ││      │ • Response text  │
    │ Turn 2: Response││      │ • Confidence     │
    │ ...             ││      │ • Timestamp      │
    └─────────────────┘│      └─────────────────┘
                       │
                       ▼
                ┌──────────────────┐
                │ Session Metadata │
                │ • User ID        │
                │ • Created at     │
                │ • Last updated   │
                │ • Context window │
                └──────────────────┘
                       │
                       ├─→ Memory for Response
                       ├─→ Context for Next Query
                       └─→ Persistence Layer
```

## 7. System Interaction Diagram

```
┌────────────┐
│   USER     │
└─────┬──────┘
      │
      │ Query
      │
      ▼
┌────────────────────────────────┐
│  Interface Layer               │
│  ┌─────────────────────────┐   │
│  │ CLI (main.py)           │   │
│  │ API (api_server.py)     │   │
│  │ Python API              │   │
│  └──────────┬──────────────┘   │
└─────────────┼──────────────────┘
              │
              ▼
┌────────────────────────────────┐
│ LegalAdvisorBot                │
│ ┌──────────────────────────┐   │
│ │ Query Processing         │   │
│ │ • Validate               │   │
│ │ • Categorize             │   │
│ │ • Enrich                 │   │
│ └──────────┬───────────────┘   │
└───────────┼────────────────────┘
            │
            ▼
┌────────────────────────────────┐
│ RAG Pipeline                   │
│ ┌──────────────────────────┐   │
│ │ Check LTM Cache          │   │
│ │ Ingest → Process → Index │   │
│ │ Retrieve (FAISS+BM25)    │   │
│ │ Generate (LLM)           │   │
│ │ Post-process             │   │
│ └──────────┬───────────────┘   │
└───────────┼────────────────────┘
            │
            ├─ Store in STM ──→ ┌──────────────┐
            │                   │ Session Mem  │
            │                   └──────────────┘
            │
            ├─ Cache in LTM ──→ ┌──────────────┐
            │                   │ LTM Cache    │
            │                   └──────────────┘
            │
            │ Final Response
            │
            ▼
        ┌───────────┐
        │   USER    │
        │ (Answer)  │
        └───────────┘
```

## 8. Performance Timeline

```
User Query
    │ 50ms
    ├──────→ QueryValidator
    │ 50ms
    ├──────→ QueryCategorizer
    │ 50ms
    ├──────→ QueryEnricher
    │
    ├─ Check LTM Cache ──┐ (0ms or 50ms)
    │                    │
    ├─ Generate Embedding (500ms)
    │
    ├─ FAISS Search (200ms)
    ├─ BM25 Search (300ms)
    ├─ Combine Results (50ms)
    │
    ├─ Build Prompt (50ms)
    │
    ├─ LLM Call (2-3 seconds) ← Dominant latency
    │
    ├─ Post-process (100ms)
    │
    ├─ Store in Memory (50ms)
    │
    ▼ 3500ms (Total, including LLM)
Response to User
```

## 9. Data Flow - Complete Journey

```
┌─────────────────────────────────────────────────────────────────┐
│ INGESTION PHASE                                                 │
│                                                                 │
│ Raw Docs → Preprocess → Chunk → Embed → FAISS Index            │
│                         ↓                    ↓                  │
│                    + Metadata        + Metadata Map             │
│                         ↓                    ↓                  │
│                      Chunks      → BM25 Index                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ QUERY PROCESSING PHASE                                          │
│                                                                 │
│ Query → Validate → Categorize → Enrich → Ready for RAG         │
│         (✓/✗)        (6 types)  (metadata)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RETRIEVAL PHASE                                                 │
│                                                                 │
│ Query Embedding ──┐                                            │
│ Query String ─────┤→ [FAISS Search] + [BM25 Search]           │
│                   └──→ [Combine Scores] → [Re-rank]           │
│                         Top-K Results                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ GENERATION PHASE                                                │
│                                                                 │
│ [Query + Context] → [Select Template] → [Build Prompt]        │
│                                              ↓                  │
│                                    [Call LLM API]              │
│                                              ↓                  │
│                                    [Post-process]              │
│                                              ↓                  │
│                                    [Add Citations]             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STORAGE PHASE                                                   │
│                                                                 │
│ Response → [Store in STM] (session)                            │
│         → [Cache in LTM] (persistent)                          │
│         → [Return to User]                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 10. Query Categorization Decision Tree

```
                    QUERY INPUT
                        │
                        ▼
            ┌────────────────────────┐
            │ Check for keywords:    │
            │ compare, versus, vs    │
            └────┬───────────────────┘
                 │
             YES │ NO
              │  │
              │  ▼
              │  ┌───────────────────────┐
              │  │ summarize, summary    │
              │  │ overview, explain     │
              │  └────┬─────────────────┘
              │       │
              │   YES │ NO
              │    │  │
              │    │  ▼
              │    │  ┌─────────────────────┐
              │    │  │ penalty, fine,      │
              │    │  │ section, article    │
              │    │  └────┬───────────────┘
              │    │       │
              │    │   YES │ NO
              │    │    │  │
              │    │    │  ▼
              │    │    │  ┌──────────────────┐
              │    │    │  │ similar, like,   │
              │    │    │  │ precedent        │
              │    │    │  └────┬────────────┘
              │    │    │       │
              │    │    │   YES │ NO
              │    │    │    │  │
              │    │    │    │  ▼
              │    │    │    │  ┌───────────────┐
              │    │    │    │  │ should, can i,│
              │    │    │    │  │ advice        │
              │    │    │    │  └────┬──────────┘
              │    │    │    │       │
              │    │    │    │   YES │ NO
              │    │    │    │    │  │
              ▼    ▼    ▼    ▼    ▼  ▼
         CASE  CASE   LEGAL SIMILAR LEGAL INVALID
         COMP  SUMM   DATA   CASE  ADVICE
```

---

These diagrams provide a visual understanding of the system architecture, data flows, and how all components interact together.
