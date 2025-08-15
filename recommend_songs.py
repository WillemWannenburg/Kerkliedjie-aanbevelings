import streamlit as st
import json
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Kerkliedjies aanbevelings",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .song-card {
        background: white;
        border: 1px solid #bdc3c7;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recommendation-header {
        color: #27ae60;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .song-title {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_songs_data(file_path: str = "combined_songs.json") -> List[Dict[str, Any]]:
    """Load songs data from JSON file with caching."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            songs = json.load(f)
        logger.info(f"Loaded {len(songs)} songs from {file_path}")
        return songs
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        st.error(f"Lieddata lêer nie gevind nie: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading songs: {e}")
        st.error(f"Fout by laai van lieddata: {e}")
        return []

@st.cache_data
def preprocess_songs(songs: List[Dict[str, Any]]) -> tuple:
    """Preprocess songs for faster vectorization."""
    song_texts = []
    song_names = []
    
    for song in songs:
        # Combine all lyrics into a single text
        lyrics_text = " ".join(song.get('lyrics', []))
        if lyrics_text.strip():
            song_texts.append(lyrics_text)
            song_names.append(song.get('filename', 'Unknown'))
    
    return song_texts, song_names

@st.cache_resource
def get_song_embeddings(song_texts: List[str], _model) -> tuple:
    """Cache song embeddings for faster recommendations."""
    if not _model or not song_texts:
        return None, None
    
    # Create embeddings
    embeddings = _model.encode(song_texts, convert_to_tensor=True, show_progress_bar=False)
    return embeddings, song_texts

@st.cache_resource
def initialize_model():
    """Initialize the sentence transformer model with caching."""
    try:
        with st.spinner("Laai AI model..."):
            # Use a faster, lighter model for better performance
            model = SentenceTransformer('all-MiniLM-L6-v2')
            # Set model to evaluation mode for faster inference
            model.eval()
        logger.info("Sentence transformer model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        st.error(f"Fout by laai van AI model: {e}")
        return None

def get_recommendations_fast(sermon_text: str, songs: List[Dict[str, Any]], _model, top_k: int = 5) -> List[Dict[str, Any]]:
    """Get song recommendations using cached embeddings for faster performance."""
    if not _model or not songs:
        return []
    
    # Get preprocessed data
    song_texts, song_names = preprocess_songs(songs)
    if not song_texts:
        return []
    
    # Get cached embeddings
    song_embeddings, _ = get_song_embeddings(song_texts, _model)
    if song_embeddings is None:
        return []
    
    # Vectorize sermon text (this is fast since it's just one text)
    sermon_embedding = _model.encode([sermon_text], convert_to_tensor=True, show_progress_bar=False)
    
    # Calculate similarities
    similarities = cosine_similarity(
        sermon_embedding.cpu().numpy(), 
        song_embeddings.cpu().numpy()
    )[0]
    
    # Get top recommendations
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    recommendations = []
    for idx in top_indices:
        song_name = song_names[idx]
        similarity_score = similarities[idx]
        
        # Find the original song data
        song_data = next((s for s in songs if s.get('filename') == song_name), None)
        if song_data:
            recommendations.append({
                'filename': song_name,
                'lyrics': song_data.get('lyrics', []),
                'similarity_score': round(similarity_score, 3)
            })
    
    return recommendations

# Legacy function - kept for compatibility but not used
def get_recommendations(sermon_text: str, songs: List[Dict[str, Any]], _model, top_k: int = 5) -> List[Dict[str, Any]]:
    """Legacy function - use get_recommendations_fast instead."""
    return get_recommendations_fast(sermon_text, songs, _model, top_k)

def main():
    """Main Streamlit app function."""
    
    # Header
    st.markdown('<h1 class="main-header">🎵 Kerkliedjies aanbevelings toep</h1>', unsafe_allow_html=True)
    
    # Load data and model with progress
    with st.spinner("🔄 Laai lieddata en AI model..."):
        songs_data = load_songs_data()
        model = initialize_model()
    
    if not songs_data or not model:
        st.error("Kon nie lieddata of AI model laai nie. Kontroleer jou internetverbinding en lêers.")
        return
    
    # Preload embeddings in background
    if songs_data and model:
        with st.spinner("⚡ Berei AI model voor vir vinnige aanbevelings..."):
            song_texts, _ = preprocess_songs(songs_data)
            get_song_embeddings(song_texts, model)
    
    # Display song count
    st.success(f"📚 {len(songs_data)} liedjies gelaai en gereed vir aanbevelings")
    
    # Input section
    st.markdown("### 📝 Voer jou preek/boodskap in:")
    
    sermon_text = st.text_area(
        "Plak jou preek/boodskap hier...",
        height=200,
        placeholder="Voer jou preek/boodskap hier in om liedaanbevelings te kry..."
    )
    
    # Recommendation button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎼 Kry Liedaanbevelings", use_container_width=True):
            if not sermon_text or not sermon_text.strip():
                st.warning("⚠️ Voer asseblief 'n preek/boodskap in")
            else:
                with st.spinner("🔄 Ontleed preek en soek aanbevelings..."):
                    try:
                        # Get recommendations (using fast method)
                        recommendations = get_recommendations_fast(sermon_text.strip(), songs_data, model, top_k=5)
                        
                        if not recommendations:
                            st.error("❌ Geen aanbevelings gevind. Kontroleer of die lieddata korrek gelaai is.")
                        else:
                            # Display recommendations
                            st.markdown('<h3 class="recommendation-header">🎼 Liedjie aanbevelings:</h3>', unsafe_allow_html=True)
                            
                            for i, rec in enumerate(recommendations):
                                with st.container():
                                    st.markdown(f"""
                                    <div class="song-card">
                                        <div class="song-title">#{i+1}: {rec['filename']}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            st.success(f"✅ {len(recommendations)} liedjies aanbeveel gebaseer op jou preek")
                            
                    except Exception as e:
                        logger.error(f"Error getting recommendations: {e}")
                        st.error(f"❌ Fout het voorgekom tydens die verwerking van jou versoek: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; font-size: 0.9rem;'>
        Kerkliedjies aanbevelings - AI-aangedrewe liedjies aanbevelings vir jou preek
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


