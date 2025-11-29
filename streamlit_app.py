"""
Streamlit Frontend for RAG-Based Legal Advisor Bot with Legal Database Integration
"""
import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any
import uuid
from datetime import datetime
import json
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.chatbot import LegalAdvisorBot
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# LOAD LEGAL DATABASE (NEW!)
# ============================================================================
@st.cache_resource
def load_legal_database():
    """Load legal database from JSON file"""
    try:
        legal_db_path = Path(__file__).parent / 'data' / 'legal_database' / 'legal_sections.json'
        if legal_db_path.exists():
            with open(legal_db_path, 'r', encoding='utf-8') as f:
                legal_sections = json.load(f)
            return legal_sections
        return None
    except Exception as e:
        logger.error(f"Error loading legal database: {e}")
        return None

@st.cache_resource
def load_legal_metadata():
    """Load legal database metadata"""
    try:
        metadata_path = Path(__file__).parent / 'data' / 'embeddings' / 'legal_sections_metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata
        return None
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        return None

# Load legal database
legal_sections = load_legal_database()
legal_metadata = load_legal_metadata()
has_legal_database = legal_sections is not None and len(legal_sections) > 0

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Legal Advisor Bot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #1f3a93;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .section-header {
        color: #2d5aa6;
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5em;
    }
    .query-box {
        background-color: #f0f4ff;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #2d5aa6;
    }
    .response-box {
        background-color: #f9f9f9;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #4caf50;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #2196f3;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #ff9800;
    }
    .stats-card {
        background-color: #f5f5f5;
        padding: 1.5em;
        border-radius: 0.5em;
        text-align: center;
    }
    .category-badge {
        display: inline-block;
        background-color: #2d5aa6;
        color: white;
        padding: 0.4em 0.8em;
        border-radius: 0.3em;
        font-size: 0.9em;
        margin: 0.2em;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'bot' not in st.session_state:
    st.session_state.bot = LegalAdvisorBot()
    logger.info("Bot initialized")

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
    st.session_state.bot.start_session(st.session_state.session_id)
    logger.info(f"Session created: {st.session_state.session_id}")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'documents_ingested' not in st.session_state:
    st.session_state.documents_ingested = False

# ============================================================================
# SIDEBAR - CONFIGURATION & CONTROLS
# ============================================================================
with st.sidebar:
    st.markdown("# ⚙️ Configuration")
    
    # Session Info
    st.markdown("### 📋 Session Info")
    st.info(f"**Session ID:** {st.session_state.session_id}")
    st.text(f"Active: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Document Ingestion
    st.markdown("### 📄 Document Management")
    
    if not st.session_state.documents_ingested:
        if st.button("📥 Ingest Sample Documents", use_container_width=True):
            with st.spinner("Ingesting sample documents..."):
                sample_documents = [
                    """
                    Indian Penal Code - Section 420 (Cheating and Dishonestly Inducing Delivery of Property):
                    Whoever cheats and thereby dishonestly induces the person deceived to deliver any 
                    property to any person, or to make, alter or destroy the whole or any part of a valuable 
                    security, or anything which is signed or sealed, with the intent that it may be used as 
                    a valuable security, shall be punished with imprisonment of either description for a term 
                    which may extend to seven years, and shall also be liable to fine.
                    """,
                    
                    """
                    Criminal Procedure Code - Section 154 (Registration of FIR):
                    (1) Any person can lodge a First Information Report (FIR) regarding any cognizable offence 
                    at the nearest police station.
                    (2) The FIR must contain the basic facts and details of the alleged crime and names of 
                    the accused if known.
                    (3) If the police refuse to register an FIR, the person can approach the Magistrate.
                    """,
                    
                    """
                    Indian Penal Code - Section 302 (Punishment for Murder):
                    Whoever commits murder shall be punished with imprisonment of either description for a 
                    term which may extend to life, or with rigorous imprisonment for a term which may extend 
                    to ten years, and shall also be liable to fine, or to both.
                    """,
                ]
                
                try:
                    st.session_state.bot.ingest_legal_documents(sample_documents)
                    st.session_state.documents_ingested = True
                    st.success("✅ Documents ingested successfully!")
                    logger.info("Sample documents ingested")
                except Exception as e:
                    st.error(f"❌ Error ingesting documents: {str(e)}")
                    logger.error(f"Error ingesting documents: {e}")
        # Ingest full legal database as sample documents (if available)
        if has_legal_database:
            if st.button("📥 Ingest Legal Database (23 sections)", use_container_width=True):
                with st.spinner("Ingesting legal database into the retrieval index..."):
                    try:
                        docs = []
                        metadata_list = []
                        for sec in legal_sections:
                            if not sec:
                                continue
                            title = sec.get('title') or sec.get('id')
                            content = sec.get('content', '')
                            # Combine title and content to improve retrieval
                            doc_text = f"{title}\n\n{content}"
                            docs.append(doc_text)
                            metadata_list.append({
                                'id': sec.get('id'),
                                'title': title,
                                'category': sec.get('category'),
                                'year': sec.get('year'),
                                'jurisdiction': sec.get('jurisdiction')
                            })

                        if len(docs) == 0:
                            st.warning("No legal sections found to ingest.")
                        else:
                            st.session_state.bot.ingest_legal_documents(docs, metadata_list)
                            st.session_state.documents_ingested = True
                            st.success(f"✅ Ingested {len(docs)} legal sections into the index")
                            logger.info(f"Ingested {len(docs)} legal sections into index")
                    except Exception as e:
                        st.error(f"❌ Error ingesting legal database: {str(e)}")
                        logger.error(f"Error ingesting legal database: {e}")
    else:
        st.success("✅ Documents loaded and indexed")
        if st.button("🔄 Reload Documents", use_container_width=True):
            st.session_state.documents_ingested = False
            st.rerun()
    
    # Retrieval Settings
    st.markdown("### 🔍 Retrieval Settings")
    
    top_k = st.slider(
        "Number of Results (top-k)",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        help="Number of relevant documents to retrieve"
    )
    
    retrieval_method = st.selectbox(
        "Retrieval Method",
        ["Hybrid (FAISS + BM25)", "Semantic (FAISS Only)", "Lexical (BM25 Only)"],
        help="Choose retrieval strategy"
    )
    
    if retrieval_method == "Hybrid (FAISS + BM25)":
        faiss_weight = st.slider(
            "FAISS Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.1,
            help="Weight for semantic search"
        )
        bm25_weight = 1.0 - faiss_weight
        st.caption(f"BM25 Weight: {bm25_weight:.1f}")
    else:
        faiss_weight = None
        bm25_weight = None
    
    # Chat Controls
    st.markdown("### 💬 Chat Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.success("History cleared!")
            st.rerun()
    
    with col2:
        if st.button("🆕 New Session", use_container_width=True):
            st.session_state.bot.end_session(st.session_state.session_id)
            st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
            st.session_state.bot.start_session(st.session_state.session_id)
            st.session_state.chat_history = []
            st.session_state.documents_ingested = False
            st.success("New session started!")
            st.rerun()
    
    # System Stats
    st.markdown("### 📊 System Statistics")
    
    try:
        stats = st.session_state.bot.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div style="font-size: 2em; color: #2d5aa6;">📚</div>
                <div style="font-size: 0.9em; color: #666;">Documents</div>
                <div style="font-size: 1.5em; font-weight: bold;">{stats.get('indexed_documents', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <div style="font-size: 2em; color: #4caf50;">💾</div>
                <div style="font-size: 0.9em; color: #666;">Queries</div>
                <div style="font-size: 1.5em; font-weight: bold;">{len(st.session_state.chat_history) // 2}</div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Unable to load stats: {str(e)}")

# ============================================================================
# MAIN CONTENT AREA - TABS
# ============================================================================

st.markdown('<div class="main-header">⚖️ Legal Advisor Bot</div>', unsafe_allow_html=True)

# Create tabs for different sections
if has_legal_database:
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📚 Legal Database", "⚙️ Settings"])
else:
    tab1, tab3 = st.tabs(["💬 Chat", "⚙️ Settings"])

with tab1:
    st.markdown("""
    A RAG-powered legal advisor that retrieves relevant legal information and provides guidance.
    Uses **hybrid search** combining semantic (FAISS) and lexical (BM25) retrieval methods.
    """)

    # Check if documents are ingested
    if not st.session_state.documents_ingested:
        st.warning("⚠️ Please ingest documents first using the sidebar before asking questions.")
    else:
        # ========================================================================
        # CHAT INTERFACE
        # ========================================================================
        st.markdown('<div class="section-header">💬 Chat Interface</div>', unsafe_allow_html=True)
        
        # Display chat history
        chat_container = st.container()
        
        with chat_container:
            for i, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="query-box">
                        <b>You:</b> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="response-box">
                        <b>Bot:</b> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'metadata' in message:
                        with st.expander("📋 Response Details"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Category", message['metadata'].get('category', 'N/A'))
                            with col2:
                                confidence = message['metadata'].get('confidence', 0)
                                st.metric("Confidence", f"{confidence:.2%}")
                            with col3:
                                st.metric("Retrieved Docs", message['metadata'].get('retrieved_count', 0))
                            
                            if 'sources' in message['metadata']:
                                st.markdown("**Sources:**")
                                for source in message['metadata']['sources']:
                                    st.caption(f"• {source}")
        
        # ========================================================================
        # INPUT AREA
        # ========================================================================
        st.markdown('<div class="section-header">📝 Ask a Question</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            user_query = st.text_input(
                "Enter your legal question",
                placeholder="e.g., What is the punishment for cheating under Section 420?",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.button("🚀 Send", use_container_width=True)
        
        # Process query
        if submit_button and user_query:
            # Add user query to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_query
            })
            
            # Get response
            with st.spinner("🔍 Searching and generating response..."):
                try:
                    response = st.session_state.bot.query(
                        user_query,
                        session_id=st.session_state.session_id
                    )
                    
                    # Extract metadata
                    metadata = {
                        'category': response.get('category', 'Unknown'),
                        'confidence': response.get('category_confidence', 0),
                        'retrieved_count': response.get('retrieved_count', 0),
                        'sources': response.get('sources', [])
                    }
                    
                    # Add bot response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response.get('response', 'No response generated'),
                        'metadata': metadata
                    })
                    
                    logger.info(f"Query processed: {user_query[:50]}...")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
                    logger.error(f"Error processing query: {e}")
                    st.session_state.chat_history.pop()  # Remove failed query
        
        # ========================================================================
        # EXAMPLE QUERIES
        # ========================================================================
        st.markdown('<div class="section-header">💡 Example Queries</div>', unsafe_allow_html=True)
        
        example_queries = [
            "What is the punishment for cheating under Section 420?",
            "How do I file an FIR?",
            "What is the punishment for murder?",
            "What are the procedures in the Criminal Procedure Code?",
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(example_queries):
            with cols[i % 2]:
                if st.button(query, use_container_width=True, key=f"example_{i}"):
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': query
                    })
                    
                    with st.spinner("🔍 Searching and generating response..."):
                        try:
                            response = st.session_state.bot.query(
                                query,
                                session_id=st.session_state.session_id
                            )
                            
                            metadata = {
                                'category': response.get('category', 'Unknown'),
                                'confidence': response.get('category_confidence', 0),
                                'retrieved_count': response.get('retrieved_count', 0),
                                'sources': response.get('sources', [])
                            }
                            
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': response.get('response', 'No response generated'),
                                'metadata': metadata
                            })
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            st.session_state.chat_history.pop()

if has_legal_database:
    with tab2:
        st.markdown('<div class="section-header">📚 Legal Database</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([0.6, 0.4])
        
        with col1:
            # Search functionality
            search_query = st.text_input(
                "🔍 Search legal sections",
                placeholder="Search by title or keywords...",
                label_visibility="collapsed"
            )
        
        with col2:
            # Category filter
            categories = sorted(set(
                section.get('category', 'Unknown') for section in legal_sections 
                if section is not None
            ))
            selected_category = st.selectbox(
                "Filter by category",
                ["All Categories"] + categories,
                label_visibility="collapsed"
            )
        
        # Filter legal sections
        filtered_sections = []
        for section in legal_sections:
            if section is None:
                continue
            
            # Category filter
            if selected_category != "All Categories" and section.get('category') != selected_category:
                continue
            
            # Search filter
            if search_query:
                search_lower = search_query.lower()
                title_match = search_lower in section.get('title', '').lower()
                content_match = search_lower in section.get('content', '').lower()
                if not (title_match or content_match):
                    continue
            
            filtered_sections.append(section)
        
        # Display results
        st.markdown(f"**Found {len(filtered_sections)} sections**")
        
        if filtered_sections:
            for i, section in enumerate(filtered_sections):
                if section is None:
                    continue
                
                with st.expander(
                    f"📄 {section.get('title', 'Unknown')} - {section.get('category', 'N/A')}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.caption(f"**ID:** {section.get('id', 'N/A')}")
                    with col2:
                        st.caption(f"**Year:** {section.get('year', 'N/A')}")
                    with col3:
                        st.caption(f"**Jurisdiction:** {section.get('jurisdiction', 'N/A')}")
                    
                    st.markdown("**Content:**")
                    st.markdown(section.get('content', 'No content available'))
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                            "❓ Ask about this",
                            key=f"ask_{section.get('id')}",
                            use_container_width=True
                        ):
                            query = f"Tell me about {section.get('title')} - {section.get('id')}"
                            st.session_state.chat_history.append({
                                'role': 'user',
                                'content': query
                            })
                            st.switch_to(tab1)
                    
                    with col2:
                        if st.button(
                            "📋 View Details",
                            key=f"details_{section.get('id')}",
                            use_container_width=True
                        ):
                            st.json(section)
        else:
            st.info("No sections match your search or filter criteria.")

with tab3:
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # Retrieval method settings
    st.markdown("### 🔍 Retrieval Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_k = st.slider(
            "Number of Results (top-k)",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="Number of relevant documents to retrieve"
        )
    
    with col2:
        retrieval_method = st.selectbox(
            "Retrieval Method",
            ["Hybrid (FAISS + BM25)", "Semantic (FAISS Only)", "Lexical (BM25 Only)"],
            help="Choose retrieval strategy"
        )
    
    if retrieval_method == "Hybrid (FAISS + BM25)":
        faiss_weight = st.slider(
            "FAISS Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.1,
            help="Weight for semantic search"
        )
        bm25_weight = 1.0 - faiss_weight
        st.info(f"FAISS: {faiss_weight:.1%} | BM25: {bm25_weight:.1%}")
    
    # Temperature settings
    st.markdown("### 🎯 LLM Configuration")
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controls randomness: lower is more focused, higher is more creative"
    )
    
    # Chat settings
    st.markdown("### 💬 Chat Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Settings", use_container_width=True):
            st.session_state.clear()
            st.success("Settings reset!")
            st.rerun()
    
    # Display current settings summary
    st.markdown("### 📊 Current Settings Summary")
    st.json({
        "Retrieval Method": retrieval_method,
        "Top-K Results": top_k,
        "Temperature": temperature,
        "Chat History Length": len(st.session_state.chat_history),
        "Session ID": st.session_state.session_id[:8] + "..."
    })

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.85em;">
    <p>RAG-Based Legal Advisor Bot • Built with Streamlit, LangChain & FAISS</p>
    <p>Session: <code>{}</code></p>
</div>
""".format(st.session_state.session_id), unsafe_allow_html=True)
