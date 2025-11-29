"""
Flask API Server for Legal Advisor Bot
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.core import LegalAdvisorBot
from src.utils import setup_logger
import uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize logger
logger = setup_logger(__name__)

# Initialize bot
bot = LegalAdvisorBot()

# Store sessions
sessions = {}


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'RAG-Based Legal Advisor Bot'
    })


@app.route('/api/v1/ingest', methods=['POST'])
def ingest_documents():
    """
    Ingest legal documents
    
    Request:
    {
        "documents": ["doc1", "doc2", ...],
        "metadata": [
            {"source": "Case Law Database", "year": 2023},
            ...
        ]
    }
    """
    try:
        data = request.json
        documents = data.get('documents', [])
        metadata_list = data.get('metadata', [])
        
        if not documents:
            return jsonify({'error': 'No documents provided'}), 400
        
        bot.ingest_legal_documents(documents, metadata_list)
        
        return jsonify({
            'status': 'success',
            'documents_ingested': len(documents)
        })
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/chat', methods=['POST'])
def chat():
    """
    Process a legal query
    
    Request:
    {
        "query": "Your legal question",
        "session_id": "optional_session_id"
    }
    
    Response:
    {
        "query": "...",
        "response": "...",
        "category": "...",
        "confidence": 0.95,
        "sources": [...]
    }
    """
    try:
        data = request.json
        query = data.get('query', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Start session if new
        if session_id not in sessions:
            bot.start_session(session_id)
            sessions[session_id] = True
        
        # Process query
        response = bot.query(query, session_id)
        
        return jsonify({
            'status': 'success',
            **response
        })
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """
    Get conversation history for a session
    
    Response:
    [
        {"query": "...", "response": "...", "timestamp": "..."},
        ...
    ]
    """
    try:
        history = bot.pipeline.stm.get_history()
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/session', methods=['POST'])
def create_session():
    """
    Create a new session
    
    Response:
    {
        "session_id": "uuid"
    }
    """
    try:
        session_id = str(uuid.uuid4())
        bot.start_session(session_id)
        sessions[session_id] = True
        
        return jsonify({'session_id': session_id})
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/session/<session_id>', methods=['DELETE'])
def end_session(session_id):
    """End a session"""
    try:
        bot.end_session(session_id)
        if session_id in sessions:
            del sessions[session_id]
        
        return jsonify({'status': 'success', 'message': 'Session ended'})
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics
    
    Response:
    {
        "indexed_documents": 1000,
        "active_sessions": 5,
        "cached_responses": 250,
        ...
    }
    """
    try:
        stats = bot.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting RAG-Based Legal Advisor Bot API Server...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
