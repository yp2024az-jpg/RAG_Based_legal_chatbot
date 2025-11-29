"""
Document Chunker - Splits documents into manageable chunks
"""
from typing import List, Dict, Any
import re

class ChunkStrategy:
    """Base class for chunking strategies"""
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        raise NotImplementedError


class SentenceChunker(ChunkStrategy):
    """Chunks text by sentences"""
    
    def chunk(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Chunk text by sentences
        
        Args:
            text: Input text
            chunk_size: Approximate chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of chunks
        """
        # Split by sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Maintain overlap
                overlap_sentences = []
                overlap_chars = 0
                for s in reversed(current_chunk):
                    if overlap_chars + len(s) <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_chars += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences + [sentence]
                current_length = overlap_chars + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


class ParagraphChunker(ChunkStrategy):
    """Chunks text by paragraphs"""
    
    def chunk(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Chunk text by paragraphs
        
        Args:
            text: Input text
            chunk_size: Approximate chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of chunks
        """
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks


class DocumentChunker:
    """Main document chunker with multiple strategies"""
    
    def __init__(self, strategy: str = "sentence", chunk_size: int = 512, overlap: int = 50):
        """
        Initialize Document Chunker
        
        Args:
            strategy: Chunking strategy ("sentence" or "paragraph")
            chunk_size: Size of chunks
            overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        if strategy == "sentence":
            self.chunker = SentenceChunker()
        elif strategy == "paragraph":
            self.chunker = ParagraphChunker()
        else:
            self.chunker = SentenceChunker()
    
    def chunk(self, document: str) -> List[str]:
        """
        Chunk a document
        
        Args:
            document: Document text
            
        Returns:
            List of chunks
        """
        return self.chunker.chunk(document, self.chunk_size, self.overlap)
    
    def chunk_with_metadata(self, document: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk document and preserve metadata
        
        Args:
            document: Document text
            metadata: Document metadata
            
        Returns:
            List of chunks with metadata
        """
        chunks = self.chunk(document)
        
        result = []
        for idx, chunk in enumerate(chunks):
            result.append({
                'text': chunk,
                'chunk_id': idx,
                'metadata': metadata,
                'original_length': len(document),
                'chunk_length': len(chunk)
            })
        
        return result
