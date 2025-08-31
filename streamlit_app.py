# streamlit_app.py - Video Editor Pure Python
import streamlit as st
import tempfile
import os
import uuid
import json
from datetime import datetime
import shutil
import base64
from pathlib import Path

# === CONFIG ===
st.set_page_config(
    page_title="🎬 Video Editor Pure Python",
    page_icon="🎬",
    layout="wide"
)

# === DIRECTORIES ===
PROJECTS_DIR = "video_projects"
TEMP_DIR = "temp_video_files"
EXPORTS_DIR = "exported_videos"

for dir_name in [PROJECTS_DIR, TEMP_DIR, EXPORTS_DIR]:
    os.makedirs(dir_name, exist_ok=True)

# === CSS STYLING ===
st.markdown("""
<style>
    .stApp { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .main-header { 
        text-align: center; 
        font-size: 3.5rem; 
        font-weight: 900; 
        color: white; 
        margin-bottom: 1rem;
        padding: 40px 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .feature-card {
        background: rgba(255,255,255,0.15);
        padding: 25px;
        border-radius: 15px;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .section-header {
        background: rgba(255,255,255,0.2);
        padding: 20px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        margin: 25px 0;
        color: white;
        font-weight: 600;
    }
    .media-item {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4ECDC4;
    }
    .timeline-item {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .export-section {
        background: rgba(255,255,255,0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        margin: 25px 0;
        border: 2px solid rgba(255,255,255,0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        padding: 15px 35px !important;
        border-radius: 30px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
    }
    .success-message {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-weight: 600;
        margin: 20px 0;
    }
    .warning-message {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-weight: 600;
        margin: 20px 0;
    }
    .info-card {
        background: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: white;
        border-left: 5px solid #4ECDC4;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# === UTILS ===
def save_uploaded_file(uploaded_file, file_type="media"):
    """Sauvegarde un fichier uploadé"""
    file_extension = uploaded_file.name.split(".")[-1].lower()
    unique_filename = f"{file_type}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(TEMP_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    
    return file_path

def get_file_size_mb(file_path):
    """Retourne la taille du fichier en MB"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0

def create_download_link(file_path, filename):
    """Crée un lien de téléchargement pour un fichier"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 Télécharger {filename}</a>'
        return href
    return ""

def save_project_data():
    """Sauvegarde les données du projet"""
    project_data = {
        "name": st.session_state.get("project_name", "Mon_Projet"),
        "video_clips": st.session_state.get("video_clips", []),
        "audio_clips": st.session_state.get("audio_clips", []),
        "timeline": st.session_state.get("timeline", []),
        "created_at": datetime.now().isoformat()
    }
    
    project_file = os.path.join(PROJECTS_DIR, f"{project_data['name']}.json")
    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)
    
    return project_file

# === SESSION STATE INITIALIZATION ===
if "project_name" not in st.session_state:
    st.session_state.project_name = f"Projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "video_clips" not in st.session_state:
    st.session_state.video_clips = []

if "audio_clips" not in st.session_state:
    st.session_state.audio_clips = []

if "timeline" not in st.session_state:
    st.session_state.timeline = []

if "current_step" not in st.session_state:
    st.session_state.current_step = 1

# === HEADER ===
st.markdown('''
<div class="main-header">
    🎬 Video Editor Pure Python
    <div style="font-size: 1.2rem; margin-top: 10px; font-weight: 400;">
        Éditeur vidéo simple sans dépendances externes
    </div>
</div>
''', unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    
    # Stepper visuel
    steps = [
        ("📥", "Import", 1),
        ("✂️", "Montage", 2), 
        ("🎵", "Audio", 3),
        ("🎨", "Organisation", 4),
        ("📦", "Export", 5)
    ]
    
    current_step = st.radio(
        "Étapes du projet:",
        options=range(1, 6),
        format_func=lambda x: f"{steps[x-1][0]} {steps[x-1][1]}",
        index=st.session_state.current_step - 1
    )
    st.session_state.current_step = current_step
    
    st.markdown("---")
    
    # Gestion de projet
    st.markdown("## 📁 Projet")
    
    project_name = st.text_input(
        "Nom du projet:", 
        value=st.session_state.project_name,
        key="project_name_input"
    )
    st.session_state.project_name = project_name
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Sauver", use_container_width=True):
            project_file = save_project_data()
            st.success(f"✅ Sauvé!")
    
    with col2:
        if st.button("🆕 Nouveau", use_container_width=True):
            # Reset tout
            for key in ["video_clips", "audio_clips", "timeline"]:
                st.session_state[key] = []
            st.session_state.project_name = f"Projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.current_step = 1
            st.success("🆕 Nouveau projet!")
            st.rerun()
    
    st.markdown("---")
    
    # Statistiques du projet
    st.markdown("## 📊 Statistiques")
    
    video_count = len(st.session_state.video_clips)
    audio_count = len(st.session_state.audio_clips)
    timeline_count = len(st.session_state.timeline)
    
    st.metric("🎬 Vidéos", video_count)
    st.metric("🎵 Audio", audio_count)  
    st.metric("⏱️ Timeline", timeline_count)
    
    # Espace disque utilisé
    total_size = 0
    for clip in st.session_state.video_clips + st.session_state.audio_clips:
        if os.path.exists(clip.get("path", "")):
            total_size += get_file_size_mb(clip["path"])
    
    st.metric("💾 Espace", f"{total_size:.1f} MB")

# === CONTENU PRINCIPAL BASÉ SUR L'ÉTAPE ===

# === ÉTAPE 1: IMPORT ===
if current_step == 1:
    st.markdown('<div class="section-header"><h2>📥 Étape 1 : Import de Médias</h2></div>', unsafe_allow_html=True)
    
    # Guide rapide
    st.markdown('''
    <div class="info-card">
        <h4>🎯 Objectif de cette étape</h4>
        <p>Importez vos vidéos et fichiers audio. Tous les formats courants sont supportés !</p>
        <ul>
            <li><strong>Vidéos :</strong> MP4, AVI, MOV, MKV, WebM, M4V</li>
            <li><strong>Audio :</strong> MP3, WAV, AAC, OGG, M4A</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎬 Import Vidéos")
        
        uploaded_videos = st.file_uploader(
            "Glissez-déposez vos vidéos ici",
            type=["mp4", "avi", "mov", "mkv", "webm", "m4v"],
            accept_multiple_files=True,
            key="video_uploader",
            help="Vous pouvez sélectionner plusieurs vidéos à la fois"
        )
        
        if uploaded_videos:
            for video in uploaded_videos:
                if video.name not in [clip["name"] for clip in st.session_state.video_clips]:
                    if st.button(f"➕ Ajouter {video.name}", key=f"add_video_{video.name}"):
                        with st.spinner(f"📂 Import de {video.name} en cours..."):
                            try:
                                video_path = save_uploaded_file(video, "video")
                                file_size = get_file_size_mb(video_path)
                                
                                clip_data = {
                                    "name": video.name,
                                    "path": video_path,
                                    "type": "video",
                                    "size_mb": file_size,
                                    "imported_at": datetime.now().isoformat()
                                }
                                
                                st.session_state.video_clips.append(clip_data)
                                st.success(f"✅ {video.name} importée avec succès!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Erreur lors de l'import de {video.name}: {str(e)}")
                else:
                    st.info(f"📝 {video.name} déjà importée")
    
    with col2:
        st.markdown("### 🎵 Import Audio")
        
        uploaded_audios = st.file_uploader(
            "Glissez-déposez vos fichiers audio ici",
            type=["mp3", "wav", "aac", "ogg", "m4a"],
            accept_multiple_files=True,
            key="audio_uploader",
            help="Musiques, voix-off, effets sonores..."
        )
        
        if uploaded_audios:
            for audio in uploaded_audios:
                if audio.name not in [clip["name"] for clip in st.session_state.audio_clips]:
                    if st.button(f"➕ Ajouter {audio.name}", key=f"add_audio_{audio.name}"):
                        with st.spinner(f"🎵 Import de {audio.name} en cours..."):
                            try:
                                audio_path = save_uploaded_file(audio, "audio")
                                file_size = get_file_size_mb(audio_path)
                                
                                clip_data = {
                                    "name": audio.name,
                                    "path": audio_path,
                                    "type": "audio", 
                                    "size_mb": file_size,
                                    "imported_at": datetime.now().isoformat()
                                }
                                
                                st.session_state.audio_clips.append(clip_data)
                                st.success(f"✅ {audio.name} importé avec succès!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Erreur lors de l'import de {audio.name}: {str(e)}")
                else:
                    st.info(f"📝 {audio.name} déjà importé")
    
    # Bibliothèque de médias
    if st.session_state.video_clips or st.session_state.audio_clips:
        st.markdown("### 📚 Bibliothèque de Médias")
        
        tab_videos, tab_audios = st.tabs(["🎬 Vidéos", "🎵 Audio"])
        
        with tab_videos:
            if st.session_state.video_clips:
                for i, clip in enumerate(st.session_state.video_clips):
                    with st.container():
                        st.markdown(f'<div class="media-item">', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            st.markdown(f"**🎬 {clip['name']}**")
                            if os.path.exists(clip["path"]):
                                st.video(clip["path"])
                            else:
                                st.error("⚠️ Fichier non trouvé")
                        
                        with col2:
                            st.write(f"**Taille:** {clip['size_mb']:.1f} MB")
                            st.write(f"**Type:** {clip['type'].upper()}")
                            imported_date = datetime.fromisoformat(clip['imported_at'])
                            st.write(f"**Importé:** {imported_date.strftime('%d/%m/%Y %H:%M')}")
                        
                        with col3:
                            if st.button("🗑️", key=f"del_video_{i}", help="Supprimer cette vidéo"):
                                if os.path.exists(clip["path"]):
                                    try:
                                        os.remove(clip["path"])
                                    except:
                                        pass
                                st.session_state.video_clips.pop(i)
                                st.success("🗑️ Vidéo supprimée!")
                                st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("📝 Aucune vidéo importée pour le moment")
        
        with tab_audios:
            if st.session_state.audio_clips:
                for i, clip in enumerate(st.session_state.audio_clips):
                    with st.container():
                        st.markdown(f'<div class="media-item">', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            st.markdown(f"**🎵 {clip['name']}**")
                            if os.path.exists(clip["path"]):
                                st.audio(clip["path"])
                            else:
                                st.error("⚠️ Fichier non trouvé")
                        
                        with col2:
                            st.write(f"**Taille:** {clip['size_mb']:.1f} MB")
                            st.write(f"**Type:** {clip['type'].upper()}")
                            imported_date = datetime.fromisoformat(clip['imported_at'])
                            st.write(f"**Importé:** {imported_date.strftime('%d/%m/%Y %H:%M')}")
                        
                        with col3:
                            if st.button("🗑️", key=f"del_audio_{i}", help="Supprimer cet audio"):
                                if os.path.exists(clip["path"]):
                                    try:
                                        os.remove(clip["path"])
                                    except:
                                        pass
                                st.session_state.audio_clips.pop(i)
                                st.success("🗑️ Audio supprimé!")
                                st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("📝 Aucun fichier audio importé pour le moment")
    
    # Navigation
    if st.session_state.video_clips:
        st.markdown("### ➡️ Étape suivante")
        if st.button("🎬 Aller au Montage", type="primary", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()

# === ÉTAPE 2: MONTAGE ===
elif current_step == 2:
    st.markdown('<div class="section-header"><h2>✂️ Étape 2 : Montage et Timeline</h2></div>', unsafe_allow_html=True)
    
    if not st.session_state.video_clips:
        st.markdown('''
        <div class="warning-message">
            ⚠️ <strong>Aucune vidéo importée !</strong><br>
            Retournez à l'étape 1 pour importer vos vidéos.
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("📥 Retour à l'Import", type="primary"):
            st.session_state.current_step = 1
            st.rerun()
    
    else:
        st.markdown('''
        <div class="info-card">
            <h4>🎯 Objectif de cette étape</h4>
            <p>Organisez vos vidéos dans l'ordre souhaité pour créer votre montage final.</p>
            <ul>
                <li>Glissez les vidéos dans la timeline</li>
                <li>Changez l'ordre en réorganisant</li>
                <li>Prévisualisez le résultat</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📚 Vidéos Disponibles")
            
            for i, clip in enumerate(st.session_state.video_clips):
                with st.container():
                    st.markdown(f'<div class="media-item">', unsafe_allow_html=True)
                    
                    col_info, col_action = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**🎬 {clip['name']}**")
                        st.write(f"Taille: {clip['size_mb']:.1f} MB")
                    
                    with col_action:
                        if st.button("➕", key=f"add_to_timeline_{i}", help=f"Ajouter {clip['name']} à la timeline"):
                            timeline_clip = clip.copy()
                            timeline_clip["timeline_position"] = len(st.session_state.timeline)
                            timeline_clip["added_at"] = datetime.now().isoformat()
                            
                            st.session_state.timeline.append(timeline_clip)
                            st.success(f"✅ {clip['name']} ajoutée à la timeline!")
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🎬 Timeline de Montage")
            
            if st.session_state.timeline:
                total_size = sum(clip["size_mb"] for clip in st.session_state.timeline)
                st.info(f"📊 Timeline: {len(st.session_state.timeline)} clip(s) - {total_size:.1f} MB total")
                
                # Réorganisation
                st.markdown("**Ordre des vidéos dans la timeline:**")
                
                for i, t_clip in enumerate(st.session_state.timeline):
                    st.markdown(f'<div class="timeline-item">', unsafe_allow_html=True)
                    
                    col_pos, col_name, col_actions = st.columns([1, 4, 2])
                    
                    with col_pos:
                        st.markdown(f"**#{i+1}**")
                    
                    with col_name:
                        st.markdown(f"🎬 **{t_clip['name']}**")
                        st.write(f"{t_clip['size_mb']:.1f} MB")
                    
                    with col_actions:
                        col_up, col_down, col_del = st.columns(3)
                        
                        with col_up:
                            if i > 0 and st.button("⬆️", key=f"up_{i}", help="Monter"):
                                st.session_state.timeline[i], st.session_state.timeline[i-1] = st.session_state.timeline[i-1], st.session_state.timeline[i]
                                st.rerun()
                        
                        with col_down:
                            if i < len(st.session_state.timeline)-1 and st.button("⬇️", key=f"down_{i}", help="Descendre"):
                                st.session_state.timeline[i], st.session_state.timeline[i+1] = st.session_state.timeline[i+1], st.session_state.timeline[i]
                                st.rerun()
                        
                        with col_del:
                            if st.button("🗑️", key=f"remove_{i}", help="Retirer"):
                                st.session_state.timeline.pop(i)
                                st.success("🗑️ Retiré de la timeline!")
                                st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Actions sur la timeline
                st.markdown("### 🎬 Actions Timeline")
                
                col_clear, col_preview = st.columns(2)
                
                with col_clear:
                    if st.button("🗑️ Vider la Timeline", use_container_width=True):
                        st.session_state.timeline = []
                        st.success("🗑️ Timeline vidée!")
                        st.rerun()
                
                with col_preview:
                    st.markdown("**Prévisualisation:**")
                    st.info("🎥 Les vidéos seront assemblées dans l'ordre de la timeline lors de l'export")
                
            else:
                st.markdown('''
                <div class="info-card">
                    <p>📝 <strong>Timeline vide</strong></p>
                    <p>Ajoutez des vidéos depuis la colonne de gauche pour commencer votre montage.</p>
                </div>
                ''', unsafe_allow_html=True)
        
        # Navigation
        if st.session_state.timeline:
            st.markdown("### ➡️ Étape suivante") 
            col_back, col_next = st.columns(2)
            
            with col_back:
                if st.button("⬅️ Retour Import", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()
            
            with col_next:
                if st.button("🎵 Ajouter l'Audio", type="primary", use_container_width=True):
                    st.session_state.current_step = 3
                    st.rerun()

# === ÉTAPE 3: AUDIO ===
elif current_step == 3:
    st.markdown('<div class="section-header"><h2>🎵 Étape 3 : Gestion Audio</h2></div>', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="info-card">
        <h4>🎯 Objectif de cette étape</h4>
        <p>Sélectionnez les fichiers audio à ajouter à votre vidéo finale.</p>
        <ul>
            <li>Musique de fond</li>
            <li>Voix-off ou narration</li>
            <li>Effets sonores</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.audio_clips:
        st.markdown('''
        <div class="warning-message">
            ℹ️ <strong>Aucun fichier audio importé</strong><br>
            Vous pouvez continuer sans audio ou retourner à l'import pour ajouter des fichiers audio.
        </div>
        ''', unsafe_allow_html=True)
        
        col_import, col_skip = st.columns(2)
        
        with col_import:
            if st.button("📥 Retour à l'Import Audio", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        with col_skip:
            if st.button("⏭️ Continuer sans Audio", type="primary", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
    
    else:
        st.markdown("### 🎵 Fichiers Audio Disponibles")
        
        # Sélection multiple des fichiers audio
        selected_audio = st.multiselect(
            "Choisissez les fichiers audio à inclure dans votre vidéo:",
            options=[clip["name"] for clip in st.session_state.audio_clips],
            default=st.session_state.get("selected_audio_files", []),
            help="Vous pouvez sélectionner plusieurs fichiers audio"
        )
        
        st.session_state.selected_audio_files = selected_audio
        
        # Prévisualisation des fichiers sélectionnés
        if selected_audio:
            st.markdown("### 🎧 Prévisualisation des Fichiers Sélectionnés")
            
            for audio_name in selected_audio:
                audio_clip = next((clip for clip in st.session_state.audio_clips if clip["name"] == audio_name), None)
                if audio_clip and os.path.exists(audio_clip["path"]):
                    with st.container():
                        st.markdown(f'<div class="media-item">', unsafe_allow_html=True)
                        
                        col1, col2 =
