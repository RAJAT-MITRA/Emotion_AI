import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import base64
import io
import time

# Page configuration
st.set_page_config(
    page_title="EmotionAI - Real-time Emotion Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
    
    * {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    :root {
        --joy: #FFD166;
        --sadness: #6C9EFF;
        --anger: #FF6B6B;
        --neutral: #A8B2C3;
        --bg: #0d0d0f;
        --surface: #141418;
        --surface2: #1c1c22;
        --border: rgba(255, 255, 255, 0.07);
        --text: #f0ede8;
        --muted: #8a8a9a;
        --accent: #FF6B35;
        --accent2: #FFD166;
    }
    
    .stApp {
        background: var(--bg);
        color: var(--text);
    }
    
    /* Header styling */
    .main-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1.5rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
    }
    
    .brand-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: linear-gradient(135deg, var(--accent), #ff9a65);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 18px rgba(255, 107, 53, 0.4);
    }
    
    .brand-name {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--text);
    }
    
    .brand-accent {
        color: var(--accent);
    }
    
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--muted);
        background: var(--surface2);
        border: 1px solid var(--border);
        padding: 0.35rem 0.85rem;
        border-radius: 99px;
        margin-left: auto;
    }
    
    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #4ade80;
        box-shadow: 0 0 8px #4ade80;
        animation: pulse-dot 2s ease-in-out infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(0.8); }
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: var(--surface) !important;
    }
    
    .sidebar-label {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Emotion legend */
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border);
        font-size: 0.8rem;
        color: var(--muted);
    }
    
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
        flex-shrink: 0;
    }
    
    .legend-dot-joy { background: var(--joy); }
    .legend-dot-sadness { background: var(--sadness); }
    .legend-dot-anger { background: var(--anger); }
    .legend-dot-neutral { background: var(--neutral); }
    
    /* Main content area */
    .block-container {
        padding-top: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Upload section */
    .upload-zone {
        border: 2px dashed rgba(255, 107, 53, 0.3);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: var(--surface);
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .upload-zone:hover {
        border-color: rgba(255, 107, 53, 0.6);
        background: rgba(255, 107, 53, 0.03);
    }
    
    .upload-emoji {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    /* Status chip */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 0.4rem 0.9rem;
        border-radius: 99px;
        border: 1px solid;
        margin: 1rem 0;
    }
    
    .status-idle {
        color: var(--muted);
        border-color: var(--border);
        background: var(--surface2);
    }
    
    .status-processing {
        color: #60a5fa;
        border-color: rgba(96, 165, 250, 0.3);
        background: rgba(96, 165, 250, 0.08);
    }
    
    .status-completed {
        color: #4ade80;
        border-color: rgba(74, 222, 128, 0.3);
        background: rgba(74, 222, 128, 0.08);
    }
    
    /* Dominant emotion card */
    .dominant-card {
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .dominant-card-joy {
        background: rgba(255, 209, 102, 0.08);
    }
    
    .dominant-card-sadness {
        background: rgba(108, 158, 255, 0.08);
    }
    
    .dominant-card-anger {
        background: rgba(255, 107, 107, 0.08);
    }
    
    .dominant-card-neutral {
        background: rgba(168, 178, 195, 0.08);
    }
    
    .dominant-tag {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }
    
    .dominant-tag-joy { color: var(--joy); }
    .dominant-tag-sadness { color: var(--sadness); }
    .dominant-tag-anger { color: var(--anger); }
    .dominant-tag-neutral { color: var(--neutral); }
    
    .dominant-emoji {
        font-size: 3rem;
        margin-right: 1rem;
    }
    
    .dominant-label {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: var(--text);
    }
    
    .dominant-subtitle {
        font-size: 0.8rem;
        color: var(--muted);
    }
    
    .confidence-score {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: var(--text);
    }
    
    /* Section headers */
    .section-label {
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--muted);
        margin: 1.5rem 0 1rem;
    }
    
    /* Emotion bars */
    .emotion-bar {
        margin: 0.75rem 0;
        padding: 0.6rem 0;
        border-bottom: 1px solid var(--border);
    }
    
    .emotion-label-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .emotion-name {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text);
    }
    
    .emotion-score {
        font-family: 'Syne', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--text);
    }
    
    /* Tip card */
    .tip-card {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        font-size: 0.78rem;
        color: var(--muted);
        line-height: 1.6;
        margin-top: 1.5rem;
    }
    
    .tip-title {
        color: var(--text);
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: var(--muted);
    }
    
    .empty-emoji {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 4s ease-in-out infinite;
    }
    
    .empty-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.5rem;
    }
    
    .empty-desc {
        font-size: 0.8rem;
        color: var(--muted);
        line-height: 1.6;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent), #ff9a65) !important;
        color: white !important;
        border: none !important;
        border-radius: 99px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.8rem !important;
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 28px rgba(255, 107, 53, 0.5) !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stRadio label {
        background: var(--surface2);
        padding: 0.9rem 1rem;
        border-radius: 14px;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    
    .stRadio label:hover {
        background: var(--surface);
        border-color: rgba(255, 107, 53, 0.3);
    }
    
    /* Progress bar customization */
    .stProgress > div > div > div {
        background: var(--accent) !important;
    }
    
    /* Image styling */
    img {
        border-radius: 20px;
        border: 1px solid var(--border);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Title styling */
    h1 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        color: var(--text) !important;
    }
    
    h2, h3 {
        font-family: 'Syne', sans-serif !important;
        color: var(--text) !important;
    }
    
</style>
""", unsafe_allow_html=True)

# Emotion metadata
EMOTION_META = {
    'joy': {'emoji': '😄', 'label': 'Joy', 'cls': 'joy', 'tip': 'You look genuinely happy right now!'},
    'happy': {'emoji': '😄', 'label': 'Joy', 'cls': 'joy', 'tip': 'You look genuinely happy right now!'},
    'sadness': {'emoji': '😢', 'label': 'Sadness', 'cls': 'sadness', 'tip': "It's okay — emotions are data, not destiny."},
    'sad': {'emoji': '😢', 'label': 'Sadness', 'cls': 'sadness', 'tip': "It's okay — emotions are data, not destiny."},
    'anger': {'emoji': '😠', 'label': 'Anger', 'cls': 'anger', 'tip': 'High intensity detected. Take a breath.'},
    'angry': {'emoji': '😠', 'label': 'Anger', 'cls': 'anger', 'tip': 'High intensity detected. Take a breath.'},
    'neutral': {'emoji': '😶', 'label': 'Neutral', 'cls': 'neutral', 'tip': 'Calm and composed — a great baseline.'},
    'fear': {'emoji': '😨', 'label': 'Fear', 'cls': 'neutral', 'tip': 'Uncertainty detected. Everything will be okay.'},
    'surprise': {'emoji': '😲', 'label': 'Surprise', 'cls': 'joy', 'tip': 'Unexpected moment captured!'},
    'disgust': {'emoji': '🤢', 'label': 'Disgust', 'cls': 'anger', 'tip': 'Strong reaction detected.'},
}

def get_emotion_meta(label):
    """Get emotion metadata"""
    return EMOTION_META.get(label.lower(), EMOTION_META['neutral'])

def analyze_emotion(image):
    """Analyze emotion from image"""
    try:
        # Convert PIL image to numpy array
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Analyze using DeepFace
        result = DeepFace.analyze(img_array, actions=['emotion'], enforce_detection=False)
        
        if isinstance(result, list):
            result = result[0]
        
        # Extract emotions
        emotions = result['emotion']
        region = result.get('region', {'x': 0, 'y': 0, 'w': 0, 'h': 0})
        
        # Sort emotions by score
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'emotions': [{'label': label, 'score': score} for label, score in sorted_emotions],
            'region': region,
            'dominant': sorted_emotions[0][0],
            'image_width': img_array.shape[1],
            'image_height': img_array.shape[0]
        }
    except Exception as e:
        print(f"Error analyzing emotion: {str(e)}")  # Log to terminal
        st.error(f"❌ Analysis error: {str(e)}")
        return None

def draw_bounding_box(image, region):
    """Draw bounding box on image"""
    img_copy = image.copy()
    if region['w'] > 0 and region['h'] > 0:
        x, y, w, h = region['x'], region['y'], region['w'], region['h']
        # Draw rectangle
        cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 209, 102), 3)
        # Draw corner markers
        corner_size = 15
        cv2.line(img_copy, (x, y), (x+corner_size, y), (255, 255, 255), 3)
        cv2.line(img_copy, (x, y), (x, y+corner_size), (255, 255, 255), 3)
        cv2.line(img_copy, (x+w, y), (x+w-corner_size, y), (255, 255, 255), 3)
        cv2.line(img_copy, (x+w, y), (x+w, y+corner_size), (255, 255, 255), 3)
        cv2.line(img_copy, (x, y+h), (x+corner_size, y+h), (255, 255, 255), 3)
        cv2.line(img_copy, (x, y+h), (x, y+h-corner_size), (255, 255, 255), 3)
        cv2.line(img_copy, (x+w, y+h), (x+w-corner_size, y+h), (255, 255, 255), 3)
        cv2.line(img_copy, (x+w, y+h), (x+w, y+h-corner_size), (255, 255, 255), 3)
    return img_copy

def render_emotion_results(data):
    """Render emotion analysis results"""
    if not data:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-emoji">🧠</div>
            <div class="empty-title">Nothing yet</div>
            <div class="empty-desc">Upload a portrait or start your webcam scan to see results.</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get dominant emotion
    dominant = data['emotions'][0]
    meta = get_emotion_meta(dominant['label'])
    
    # Dominant emotion card
    st.markdown(f"""
    <div class="dominant-card dominant-card-{meta['cls']}">
        <div class="dominant-tag dominant-tag-{meta['cls']}">DOMINANT EMOTION</div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span class="dominant-emoji">{meta['emoji']}</span>
                <span class="dominant-label">{meta['label']}</span>
                <div class="dominant-subtitle">Detected with confidence</div>
            </div>
            <div>
                <div class="confidence-score">{dominant['score']:.0f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Full spectrum
    st.markdown('<div class="section-label">FULL SPECTRUM</div>', unsafe_allow_html=True)
    
    for emotion in data['emotions']:
        emo_meta = get_emotion_meta(emotion['label'])
        
        # Emotion bar header
        st.markdown(f"""
        <div class="emotion-bar">
            <div class="emotion-label-row">
                <span class="emotion-name">{emo_meta['emoji']} {emo_meta['label']}</span>
                <span class="emotion-score">{emotion['score']:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar - convert to Python float
        st.progress(float(max(emotion['score'] / 100, 0.005)))
    
    # Tip card
    st.markdown(f"""
    <div class="tip-card">
        <div class="tip-title">💡 Insight</div>
        {meta['tip']}
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'status' not in st.session_state:
    st.session_state.status = 'idle'
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False
if 'last_capture_time' not in st.session_state:
    st.session_state.last_capture_time = time.time()

# Header
st.markdown("""
<div class="main-header">
    <div class="brand-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a10 10 0 1 0 10 10" />
            <path d="M12 8v4l3 3" />
        </svg>
    </div>
    <span class="brand-name">Emotion<span class="brand-accent">AI</span></span>
    <span class="live-badge">
        <span class="live-dot"></span>
        DeepFace · Live
    </span>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-label">INPUT MODE</div>', unsafe_allow_html=True)
    
    input_mode = st.radio(
        "Select Input Mode",
        ["📤 Upload Image", "📷 Live Webcam"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="sidebar-label">EMOTION PALETTE</div>', unsafe_allow_html=True)
    
    # Emotion legend
    for emotion_key in ['joy', 'sadness', 'anger', 'neutral']:
        meta = EMOTION_META[emotion_key]
        st.markdown(f"""
        <div class="legend-item">
            <div class="legend-dot legend-dot-{meta['cls']}"></div>
            <span>{meta['emoji']} {meta['label']}</span>
        </div>
        """, unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([1.5, 1])

with col1:
    if "Upload" in input_mode:
        st.markdown("""
        <h1>Drop a <em style="background: linear-gradient(90deg, #FF6B35, #FFD166); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">face photo</em>.</h1>
        <p style="color: var(--muted); margin-bottom: 1.5rem;">
            Upload any portrait and DeepFace will map every micro-expression in real time.
        </p>
        """, unsafe_allow_html=True)
        
        # Status indicator
        status_class = f"status-{st.session_state.status}"
        status_text = {
            'idle': 'Waiting',
            'processing': 'Analyzing…',
            'completed': 'Done'
        }
        st.markdown(f'<div class="status-chip {status_class}">{status_text.get(st.session_state.status, "Waiting")}</div>', unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['jpg', 'jpeg', 'png', 'webp'],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Display uploaded image first
            image = Image.open(uploaded_file)
            
            # Process image
            st.session_state.status = 'processing'
            
            # Analyze emotion
            with st.spinner("🧠 Running DeepFace analysis..."):
                data = analyze_emotion(image)
                
            if data:
                st.session_state.analysis_data = data
                st.session_state.status = 'completed'
                
                # Draw bounding box
                img_with_box = draw_bounding_box(np.array(image), data['region'])
                
                # Display image with overlay
                st.image(img_with_box, use_container_width=True)
                
                # Show emotion label on image
                if data['region']['w'] > 0:
                    dominant = data['emotions'][0]
                    meta = get_emotion_meta(dominant['label'])
                    st.success(f"✓ Detected: {meta['emoji']} {meta['label']} · {dominant['score']:.0f}%")
                else:
                    st.info("ℹ️ Analyzing face...")
            else:
                # Show original image even if analysis fails
                st.image(image, use_container_width=True)
                st.error("⚠ Could not detect a face. Please try another image with a clear, well-lit face.")
                st.session_state.status = 'idle'
                st.session_state.analysis_data = None
        else:
            # Empty state
            st.markdown("""
            <div class="upload-zone">
                <div class="upload-emoji">🖼️</div>
                <h3 style="margin-bottom: 0.5rem;">Drop your photo here</h3>
                <p style="color: var(--muted); margin-bottom: 1rem;">
                    Portrait works best — make sure a face<br>is visible and well-lit.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.analysis_data = None
            st.session_state.status = 'idle'
    
    else:  # Webcam mode
        st.markdown("""
        <h1>Go <em style="background: linear-gradient(90deg, #FF6B35, #FFD166); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">live</em>, smile big.</h1>
        <p style="color: var(--muted); margin-bottom: 1.5rem;">
            Your webcam feed is analyzed frame-by-frame at ~800ms intervals.
        </p>
        """, unsafe_allow_html=True)
        
        # Status indicator
        status_class = f"status-{st.session_state.status}"
        status_text = {
            'idle': 'Waiting',
            'processing': 'Analyzing…',
            'completed': 'Done'
        }
        st.markdown(f'<div class="status-chip {status_class}">{status_text.get(st.session_state.status, "Waiting")}</div>', unsafe_allow_html=True)
        
        # Webcam controls
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("▶ Start Scan" if not st.session_state.webcam_running else "⏹ Stop Scan", key="webcam_toggle"):
                st.session_state.webcam_running = not st.session_state.webcam_running
                if not st.session_state.webcam_running:
                    st.session_state.analysis_data = None
                    st.session_state.status = 'idle'
                st.rerun()
        
        if st.session_state.webcam_running:
            st.markdown("---")
            st.markdown("### 📸 Live Camera Feed")
            
            # Camera input - always visible when scanning
            picture = st.camera_input(
                "Take a photo to analyze emotion", 
                key="webcam_live"
            )
            
            if picture is not None:
                # Process webcam frame
                st.session_state.status = 'processing'
                
                with st.spinner("🧠 Analyzing..."):
                    image = Image.open(picture)
                    
                    # Analyze emotion
                    data = analyze_emotion(image)
                
                if data:
                    st.session_state.analysis_data = data
                    st.session_state.status = 'completed'
                    
                    # Draw bounding box on image
                    img_with_box = draw_bounding_box(np.array(image), data['region'])
                    
                    col_img, col_info = st.columns([2, 1])
                    
                    with col_img:
                        st.image(img_with_box, use_container_width=True)
                    
                    with col_info:
                        dominant = get_emotion_meta(data['emotions'][0]['label'])
                        st.markdown(f"""
                        ### {dominant['emoji']} {dominant['label']}
                        **{data['emotions'][0]['score']:.1f}%** confidence
                        """)
                        
                        st.caption("📊 Full analysis available in the right panel →")
                else:
                    st.image(image, use_container_width=True)
                    st.warning("⚠ No face detected - please adjust position")
                    st.session_state.status = 'idle'
                
                st.info("💡 Take another photo to update results")
            else:
                st.info("📸 No photo captured yet - click the camera button above")
        else:
            st.session_state.status = 'idle'
            st.info("👆 Click 'Start Scan' to begin real-time emotion detection")

# Right panel - Analysis results
with col2:
    st.markdown("""
    <div style="padding: 1rem;">
        <p style="font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.4rem;">
            NEURAL OUTPUT
        </p>
        <h2 style="font-size: 1.25rem; margin-bottom: 1.5rem;">Emotion Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    render_emotion_results(st.session_state.analysis_data)

# Footer info
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--muted); font-size: 0.75rem; padding: 1rem;">
    Powered by DeepFace • Real-time emotion recognition using deep learning
</div>
""", unsafe_allow_html=True)
