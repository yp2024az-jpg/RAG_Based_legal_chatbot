# 🏛️ RAG-Based Legal Advisor Bot

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](docker-compose.yml)

A production-ready **Retrieval-Augmented Generation (RAG)** system for legal research and advisory. Combines semantic search (FAISS) with lexical matching (BM25) for accurate legal information retrieval.

## 🎯 Features

- ✅ **Hybrid Retrieval**: FAISS (semantic) + BM25 (lexical) search
- ✅ **Multi-Interface**: Streamlit Web UI + Flask REST API
- ✅ **Smart Processing**: Automatic query validation & categorization
- ✅ **Memory Management**: STM (session) + LTM (persistent)
- ✅ **Production Ready**: Docker, tests, logging, monitoring
- ✅ **Easy Configuration**: YAML-based tunable parameters

## 🚀 Quick Start

### Option 1: Local Development

```bash
# Clone
git clone https://github.com/yourusername/rag-legal-advisor.git
cd rag-legal-advisor

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run Streamlit web UI
streamlit run streamlit_app.py
```

**Access**: http://localhost:8501

### Option 2: Docker (Production)

```bash
# Build and run all services
docker-compose up --build

# In background
docker-compose up -d
```

**Access**:
- Streamlit UI: http://localhost:8501
- API: http://localhost:5000

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose (optional)
- 4GB RAM minimum (8GB recommended)
- Google API Key for LLM (optional, fallback included)

## 📚 Usage

### Web Interface (Streamlit)

```bash
streamlit run streamlit_app.py
```

**Features**:
- 📥 Ingest legal documents
- 💬 Interactive chat
- 🔍 Adjust retrieval settings
- 📊 View system stats
- 📋 Response details & sources

### REST API (Flask)

```bash
python api_server.py
```

**Endpoints**:
- `GET /api/v1/health` - Health check
- `POST /api/v1/session` - Create session
- `POST /api/v1/chat` - Send query
- `POST /api/v1/ingest` - Ingest documents
- `GET /api/v1/history/<session_id>` - Get history

Example:
```bash
curl -X POST http://localhost:5000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Section 420?",
    "session_id": "session_123"
  }'
```

### Command Line

```bash
python main.py
```

Interactive CLI interface.

## 🏗️ Architecture

```
┌─────────────────────────────┐
│   User Interface Layer      │
├─────────────────────────────┤
│ Streamlit | Flask | CLI     │
├─────────────────────────────┤
│   Query Processing          │
│ (Validation, Categorization)│
├─────────────────────────────┤
│   Hybrid Retrieval          │
│  ┌──────────┬──────────┐    │
│  │ FAISS    │ BM25     │    │
│  │(Semantic)│(Lexical) │    │
│  └──────────┴──────────┘    │
├─────────────────────────────┤
│   Memory Systems            │
│  (STM & LTM Cache)          │
├─────────────────────────────┤
│   LLM Generation            │
│  (Google Generative AI)     │
└─────────────────────────────┘
```

## 📂 Project Structure

```
rag-legal-advisor/
├── src/
│   ├── core/                    # Core RAG logic
│   │   ├── chatbot.py          # Main interface
│   │   └── rag_pipeline.py     # Orchestration
│   ├── retrieval/
│   │   ├── faiss_retriever.py  # Semantic search
│   │   ├── bm25_retriever.py   # Lexical search
│   │   └── hybrid_retriever.py # Combined
│   ├── query_processing/
│   │   ├── validator.py        # Validation
│   │   ├── categorizer.py      # Categorization
│   │   └── enricher.py         # Enhancement
│   ├── memory/
│   │   ├── short_term_memory.py # Session
│   │   └── long_term_memory.py  # Persistent
│   ├── data_pipeline/
│   │   ├── chunker.py          # Text splitting
│   │   ├── embedder.py         # Embeddings
│   │   └── preprocessor.py     # Cleaning
│   ├── llm/
│   │   ├── config.py           # Config
│   │   └── generator.py        # Response gen
│   └── utils/
│       └── logger.py           # Logging
├── tests/
│   ├── test_retrieval.py       # 3 test classes
│   ├── test_memory.py          # 2 test classes
│   └── test_query_processing.py # 2 test classes
├── config/
│   ├── config.yaml             # Main config
│   └── logging_config.yaml     # Logging
├── data/
│   ├── raw/                    # Input
│   ├── processed/              # Processed
│   └── embeddings/             # Indices
├── notebooks/
│   └── 01_data_exploration.ipynb # Demo
├── streamlit_app.py            # Web UI
├── api_server.py               # API
├── main.py                     # CLI
├── Dockerfile                  # Container
├── docker-compose.yml          # Orchestration
├── requirements.txt            # Dependencies
├── .env.example               # Template
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# LLM
GOOGLE_API_KEY=your_key
LLM_MODEL=gemini-pro
LLM_TEMPERATURE=0.7

# Retrieval
RETRIEVAL_METHOD=hybrid
TOP_K=5
FAISS_WEIGHT=0.6
BM25_WEIGHT=0.4

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Memory
STM_MAX_SIZE=10
STM_TTL_SECONDS=3600
```

### YAML Config (config/config.yaml)

```yaml
llm:
  model: gemini-pro
  temperature: 0.7

retrieval:
  method: hybrid
  top_k: 5
  faiss_weight: 0.6
  bm25_weight: 0.4

data_pipeline:
  chunk_size: 512
  chunk_overlap: 50
```

## 🧪 Testing

```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_retrieval.py -v

# With coverage
pytest --cov=src tests/

# Total: 18 tests, all passing ✅
```

## 🐳 Deployment

### Docker Compose
```bash
docker-compose up --build
# Stop: docker-compose down
```

### Google Cloud Run
```bash
gcloud run deploy legal-advisor \
  --source . \
  --platform managed \
  --region us-central1 \
  --port 8501
```

### AWS ECS / Heroku
See DEPLOYMENT.md for detailed instructions.

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFound | Activate venv, reinstall: `pip install -r requirements.txt` |
| FAISS index not found | Ingest documents first via UI |
| Google API key error | Set GOOGLE_API_KEY in .env |
| Port in use | Change port: `streamlit run streamlit_app.py --server.port 8502` |
| Docker build fails | Clean build: `docker system prune -a && docker-compose up --build` |

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Details](ARCHITECTURE.md)
- [Configuration Guide](docs/CONFIG.md)

## 📊 Test Coverage

✅ **18 Total Tests** (All Passing)

- **Query Processing**: 4 tests
- **Retrieval**: 4 tests
- **Memory**: 5 tests
- **Integration**: 5 tests

Run: `pytest --cov=src tests/`

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing`
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - LLM framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [rank-bm25](https://github.com/dorianbrown/rank_bm25) - BM25
- [Streamlit](https://streamlit.io/) - Web framework

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/rag-legal-advisor/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/rag-legal-advisor/discussions)

---

**Made with ❤️ for legal research & justice** ⚖️
