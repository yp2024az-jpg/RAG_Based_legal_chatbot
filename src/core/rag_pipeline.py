"""
RAG Pipeline - Orchestrates the RAG process
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import hashlib

from src.query_processing import QueryValidator, QueryCategorizer, QueryEnricher
from src.retrieval import HybridRetriever
from src.data_pipeline import DocumentChunker, DocumentEmbedder, DataPreprocessor
from src.llm import ResponseGenerator
from src.memory import ShortTermMemory, LongTermMemory
from src.utils import setup_logger, InvalidQueryException

logger = setup_logger(__name__)

class RAGPipeline:
    """
    Retrieval-Augmented Generation Pipeline.
    Orchestrates the complete RAG flow from query to response.
    """
    
    def __init__(self, 
                 embedding_dim: int = 384,
                 chunk_size: int = 512,
                 stm_max_size: int = 10,
                 faiss_weight: float = 0.6,
                 bm25_weight: float = 0.4):
        """
        Initialize RAG Pipeline
        
        Args:
            embedding_dim: Embedding dimension
            chunk_size: Document chunk size
            stm_max_size: Short-term memory size
            faiss_weight: Weight for FAISS in hybrid retrieval
            bm25_weight: Weight for BM25 in hybrid retrieval
        """
        # Query processing
        self.validator = QueryValidator()
        self.categorizer = QueryCategorizer()
        self.enricher = QueryEnricher()
        
        # Data pipeline
        self.chunker = DocumentChunker(chunk_size=chunk_size)
        self.embedder = DocumentEmbedder()
        self.preprocessor = DataPreprocessor()
        
        # Retrieval
        self.retriever = HybridRetriever(
            embedding_dim=embedding_dim,
            faiss_weight=faiss_weight,
            bm25_weight=bm25_weight
        )
        
        # LLM
        self.generator = ResponseGenerator()
        
        # Memory
        self.stm = ShortTermMemory(max_size=stm_max_size)
        self.ltm = LongTermMemory()
        
        # Document store
        self.documents = []
        
        logger.info("RAG Pipeline initialized successfully")
    
    def ingest_documents(self, documents: List[str], metadata_list: List[Dict[str, Any]] = None):
        """
        Ingest documents into the pipeline
        
        Args:
            documents: List of document texts
            metadata_list: Optional list of metadata for each document
        """
        logger.info(f"Ingesting {len(documents)} documents...")
        
        all_chunks = []
        all_embeddings = []
        all_metadata = []
        
        for doc_idx, doc in enumerate(documents):
            # Preprocess
            cleaned_doc = self.preprocessor.clean_text(doc)
            
            # Chunk
            chunks = self.chunker.chunk(cleaned_doc)
            
            # Embed
            embeddings = self.embedder.embed_texts(chunks)
            
            # Store
            for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                all_chunks.append(chunk)
                all_embeddings.append(embedding)
                
                chunk_meta = {
                    'doc_id': doc_idx,
                    'chunk_id': chunk_idx,
                    'original_doc_length': len(doc),
                    'chunk_length': len(chunk)
                }
                
                if metadata_list and doc_idx < len(metadata_list):
                    chunk_meta.update(metadata_list[doc_idx])
                
                all_metadata.append(chunk_meta)
                
                # Store in LTM
                self.ltm.store_document_metadata(
                    f"doc_{doc_idx}_chunk_{chunk_idx}",
                    chunk_meta
                )
        
        # Add to retriever
        self.retriever.add_documents(all_chunks, all_embeddings, all_metadata)
        self.documents = all_chunks
        
        logger.info(f"Ingested {len(all_chunks)} chunks successfully")
    
    def process_query(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline
        
        Args:
            query: User query
            session_id: Optional session ID
            
        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Processing query: {query}")
        
        # 1. Validate query
        if not self.validator.is_valid(query):
            raise InvalidQueryException("Query is not a valid legal domain query")
        
        validity_score = self.validator.get_validity_score(query)
        
        # 2. Categorize query
        category, category_confidence = self.categorizer.categorize(query)
        
        # 3. Enrich query
        session_context = self.stm.session_metadata if session_id else {}
        enriched_query = self.enricher.enrich(query, session_context)
        
        # 4. Check LTM cache
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cached_response = self.ltm.retrieve_response(query_hash)
        
        if cached_response and cached_response['confidence'] > 0.8:
            logger.info("Using cached response from LTM")
            response = cached_response['response']
            sources = cached_response['sources']
        else:
            # 5. Generate query embedding
            query_embedding = self.embedder.embed_text(query)
            
            # 6. Retrieve relevant documents
            retrieved_docs = self.retriever.search(
                query, 
                query_embedding, 
                k=5
            )
            
            if not retrieved_docs:
                response = "No relevant legal documents found for your query."
                sources = []
            else:
                # 7. Prepare context
                context = "\n\n".join([doc for doc, _ in retrieved_docs])
                sources = retrieved_docs
                
                # 8. Generate response
                response = self.generator.generate_with_context(
                    query,
                    context,
                    query_type=category.value
                )
                
                # Cache in LTM
                confidence_score = sum(score for _, score in retrieved_docs) / len(retrieved_docs)
                self.ltm.store_response(
                    query_hash,
                    response,
                    [doc for doc, _ in retrieved_docs],
                    confidence_score
                )
        
        # 9. Store in STM
        self.stm.add_turn(query, response, category.value)
        
        # Prepare result
        result = {
            'query': query,
            'response': response,
            'category': category.value,
            'category_confidence': category_confidence,
            'validity_score': validity_score,
            'sources': sources,
            'enriched_query': enriched_query,
            'session_id': session_id
        }
        
        return result
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get current session history"""
        return self.stm.get_history()
    
    def clear_session(self):
        """Clear current session"""
        self.stm.clear()
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            'indexed_documents': self.retriever.get_document_count(),
            'stm_size': len(self.stm.history),
            'ltm_embeddings': self.ltm.get_all_embeddings_count(),
            'cached_responses': self.ltm.get_response_cache_size()
        }
