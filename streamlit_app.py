# streamlit_app.py - Video Editor
import streamlit as st
import moviepy.editor as mp
import tempfile
import os
import uuid
import json
from datetime import datetime
import shutil
import zipfile

# === CONFIG ===
st.set_page_config(
    page_title="🎬 Video Editor Pro",
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
    }
    .main-header { 
        text-align: center; 
        font-size: 3rem; 
        font-weight: 800; 
        color: white; 
        margin-bottom: 1rem;
        padding: 30px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .section-header {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 20px 0;
    }
    .video-timeline {
        background: #2c3e50;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: white;
    }
    .audio-track {
        background: #27ae60;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        color: white;
    }
    .video-track {
        background: #3498db;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        color: white;
    }
    .export-section {
        background: rgba(255,255,255,0.9);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# === UTILS ===
def save_project(project_data, project_name):
    """Sauvegarde un projet vidéo"""
    project_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
    with open(project_path, "w", encoding="utf-8") as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)

def load_project(project_name):
    """Charge un projet vidéo"""
    project_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
    if os.path.exists(project_path):
        with open(project_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def list_projects():
    """Liste tous les projets disponibles"""
    if not os.path.exists(PROJECTS_DIR):
        return []
    files = [f.replace(".json", "") for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]
    return sorted(files, reverse=True)

def save_uploaded_file(uploaded_file, file_type="video"):
    """Sauvegarde un fichier uploadé"""
    file_extension = uploaded_file.name.split(".")[-1]
    unique_filename = f"{file_type}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(TEMP_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    
    return file_path

def get_video_info(video_path):
    """Obtient les informations d'une vidéo"""
    try:
        clip = mp.VideoFileClip(video_path)
        info = {
            "duration": clip.duration,
            "fps": clip.fps,
            "size": clip.size,
            "width": clip.w,
            "height": clip.h
        }
        clip.close()
        return info
    except Exception as e:
        return {"error": str(e)}

def get_audio_info(audio_path):
    """Obtient les informations d'un fichier audio"""
    try:
        clip = mp.AudioFileClip(audio_path)
        info = {
            "duration": clip.duration,
        }
        clip.close()
        return info
    except Exception as e:
        return {"error": str(e)}

# === SESSION STATE ===
if "current_project" not in st.session_state:
    st.session_state.current_project = {
        "name": f"Projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "video_clips": [],
        "audio_clips": [],
        "effects": [],
        "timeline": []
    }

if "preview_video" not in st.session_state:
    st.session_state.preview_video = None

# === HEADER ===
st.markdown('<h1 class="main-header">🎬 Video Editor Pro</h1>', unsafe_allow_html=True)

# === SIDEBAR - GESTION PROJETS ===
with st.sidebar:
    st.markdown("## 📁 Gestion des Projets")
    
    # Nom du projet actuel
    project_name = st.text_input("Nom du projet:", value=st.session_state.current_project["name"])
    st.session_state.current_project["name"] = project_name
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Sauvegarder", use_container_width=True):
            save_project(st.session_state.current_project, project_name)
            st.success("Projet sauvegardé!")
    
    with col2:
        if st.button("🆕 Nouveau", use_container_width=True):
            st.session_state.current_project = {
                "name": f"Projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "video_clips": [],
                "audio_clips": [],
                "effects": [],
                "timeline": []
            }
            st.rerun()
    
    # Chargement de projet
    st.markdown("### Projets existants:")
    projects = list_projects()
    if projects:
        selected_project = st.selectbox("Charger un projet:", [""] + projects)
        if selected_project and st.button("🔄 Charger"):
            loaded_project = load_project(selected_project)
            if loaded_project:
                st.session_state.current_project = loaded_project
                st.success(f"Projet '{selected_project}' chargé!")
                st.rerun()
    
    st.markdown("---")
    
    # Paramètres d'export
    st.markdown("## ⚙️ Export Settings")
    export_format = st.selectbox("Format:", ["mp4", "avi", "mov", "webm"])
    export_quality = st.selectbox("Qualité:", ["Basse (480p)", "Moyenne (720p)", "Haute (1080p)", "Ultra (4K)"])
    export_fps = st.slider("FPS:", 15, 60, 30)

# === MAIN CONTENT ===
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 Import", "✂️ Montage", "🎵 Audio", "🎨 Effets", "🚀 Export"])

# === TAB 1: IMPORT ===
with tab1:
    st.markdown('<div class="section-header"><h2>📥 Import de Médias</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎬 Vidéos")
        uploaded_videos = st.file_uploader(
            "Choisir des vidéos:",
            type=["mp4", "avi", "mov", "mkv", "webm", "m4v"],
            accept_multiple_files=True,
            key="video_uploader"
        )
        
        if uploaded_videos:
            for video in uploaded_videos:
                if st.button(f"➕ Ajouter {video.name}", key=f"add_video_{video.name}"):
                    with st.spinner(f"Traitement de {video.name}..."):
                        video_path = save_uploaded_file(video, "video")
                        video_info = get_video_info(video_path)
                        
                        clip_data = {
                            "id": str(uuid.uuid4()),
                            "name": video.name,
                            "path": video_path,
                            "type": "video",
                            "info": video_info,
                            "start_time": 0,
                            "end_time": video_info.get("duration", 0),
                            "position": len(st.session_state.current_project["video_clips"])
                        }
                        
                        st.session_state.current_project["video_clips"].append(clip_data)
                        st.success(f"✅ {video.name} ajoutée!")
                        st.rerun()
    
    with col2:
        st.markdown("### 🎵 Audio")
        uploaded_audios = st.file_uploader(
            "Choisir des fichiers audio:",
            type=["mp3", "wav", "aac", "ogg", "m4a"],
            accept_multiple_files=True,
            key="audio_uploader"
        )
        
        if uploaded_audios:
            for audio in uploaded_audios:
                if st.button(f"➕ Ajouter {audio.name}", key=f"add_audio_{audio.name}"):
                    with st.spinner(f"Traitement de {audio.name}..."):
                        audio_path = save_uploaded_file(audio, "audio")
                        audio_info = get_audio_info(audio_path)
                        
                        clip_data = {
                            "id": str(uuid.uuid4()),
                            "name": audio.name,
                            "path": audio_path,
                            "type": "audio",
                            "info": audio_info,
                            "start_time": 0,
                            "end_time": audio_info.get("duration", 0),
                            "position": len(st.session_state.current_project["audio_clips"])
                        }
                        
                        st.session_state.current_project["audio_clips"].append(clip_data)
                        st.success(f"✅ {audio.name} ajouté!")
                        st.rerun()
    
    # Affichage des médias importés
    if st.session_state.current_project["video_clips"] or st.session_state.current_project["audio_clips"]:
        st.markdown("### 📚 Bibliothèque de Médias")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.current_project["video_clips"]:
                st.markdown("**🎬 Vidéos disponibles:**")
                for clip in st.session_state.current_project["video_clips"]:
                    with st.expander(f"🎬 {clip['name']}", expanded=False):
                        if os.path.exists(clip["path"]):
                            st.video(clip["path"])
                            st.write(f"**Durée:** {clip['info'].get('duration', 0):.2f}s")
                            st.write(f"**Résolution:** {clip['info'].get('width', 'N/A')}x{clip['info'].get('height', 'N/A')}")
                            st.write(f"**FPS:** {clip['info'].get('fps', 'N/A')}")
        
        with col2:
            if st.session_state.current_project["audio_clips"]:
                st.markdown("**🎵 Audio disponible:**")
                for clip in st.session_state.current_project["audio_clips"]:
                    with st.expander(f"🎵 {clip['name']}", expanded=False):
                        if os.path.exists(clip["path"]):
                            st.audio(clip["path"])
                            st.write(f"**Durée:** {clip['info'].get('duration', 0):.2f}s")

# === TAB 2: MONTAGE ===
with tab2:
    st.markdown('<div class="section-header"><h2>✂️ Montage Vidéo</h2></div>', unsafe_allow_html=True)
    
    if not st.session_state.current_project["video_clips"]:
        st.warning("Aucune vidéo importée. Allez dans l'onglet Import pour ajouter des vidéos.")
    else:
        # Timeline de montage
        st.markdown('<div class="video-timeline">', unsafe_allow_html=True)
        st.markdown("### 🎞️ Timeline de Montage")
        
        # Sélection des clips pour la timeline
        st.markdown("**Ajouter à la timeline:**")
        
        for i, clip in enumerate(st.session_state.current_project["video_clips"]):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"🎬 {clip['name']}")
            
            with col2:
                start_time = st.number_input(
                    f"Début (s)", 
                    min_value=0.0,
                    max_value=clip['info'].get('duration', 0),
                    value=clip.get('trim_start', 0.0),
                    step=0.1,
                    key=f"start_{clip['id']}"
                )
                clip['trim_start'] = start_time
            
            with col3:
                end_time = st.number_input(
                    f"Fin (s)", 
                    min_value=start_time,
                    max_value=clip['info'].get('duration', 0),
                    value=clip.get('trim_end', clip['info'].get('duration', 0)),
                    step=0.1,
                    key=f"end_{clip['id']}"
                )
                clip['trim_end'] = end_time
            
            with col4:
                if st.button("➕", key=f"timeline_{clip['id']}"):
                    timeline_clip = clip.copy()
                    timeline_clip['timeline_position'] = len(st.session_state.current_project["timeline"])
                    st.session_state.current_project["timeline"].append(timeline_clip)
                    st.success("Ajouté à la timeline!")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Affichage de la timeline
        if st.session_state.current_project["timeline"]:
            st.markdown("### 🎬 Timeline Actuelle")
            
            total_duration = 0
            for i, timeline_clip in enumerate(st.session_state.current_project["timeline"]):
                duration = timeline_clip.get('trim_end', 0) - timeline_clip.get('trim_start', 0)
                total_duration += duration
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f'<div class="video-track">🎬 {timeline_clip["name"]}</div>', unsafe_allow_html=True)
                
                with col2:
                    st.write(f"⏱️ {duration:.2f}s")
                
                with col3:
                    st.write(f"📍 Position {i+1}")
                
                with col4:
                    if st.button("🗑️", key=f"remove_timeline_{i}"):
                        st.session_state.current_project["timeline"].pop(i)
                        st.rerun()
            
            st.info(f"**Durée totale de la timeline:** {total_duration:.2f} secondes")
            
            # Prévisualisation
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🔍 Générer Prévisualisation", type="primary"):
                    with st.spinner("Génération de la prévisualisation..."):
                        try:
                            clips_to_concatenate = []
                            
                            for timeline_clip in st.session_state.current_project["timeline"]:
                                if os.path.exists(timeline_clip["path"]):
                                    clip = mp.VideoFileClip(timeline_clip["path"])
                                    
                                    # Découpage
                                    start = timeline_clip.get('trim_start', 0)
                                    end = timeline_clip.get('trim_end', clip.duration)
                                    
                                    if end > start:
                                        trimmed_clip = clip.subclip(start, end)
                                        clips_to_concatenate.append(trimmed_clip)
                                    
                                    clip.close()
                            
                            if clips_to_concatenate:
                                final_clip = mp.concatenate_videoclips(clips_to_concatenate)
                                
                                preview_path = os.path.join(TEMP_DIR, f"preview_{uuid.uuid4().hex}.mp4")
                                final_clip.write_videofile(
                                    preview_path, 
                                    codec='libx264',
                                    audio_codec='aac',
                                    temp_audiofile='temp-audio.m4a',
                                    remove_temp=True,
                                    verbose=False,
                                    logger=None
                                )
                                
                                st.session_state.preview_video = preview_path
                                final_clip.close()
                                
                                for clip in clips_to_concatenate:
                                    clip.close()
                                
                                st.success("✅ Prévisualisation générée!")
                                st.rerun()
                            else:
                                st.error("Aucun clip valide dans la timeline")
                                
                        except Exception as e:
                            st.error(f"Erreur lors de la génération: {str(e)}")
            
            with col2:
                if st.button("🗑️ Vider Timeline"):
                    st.session_state.current_project["timeline"] = []
                    st.session_state.preview_video = None
                    st.rerun()
        
        # Affichage de la prévisualisation
        if st.session_state.preview_video and os.path.exists(st.session_state.preview_video):
            st.markdown("### 👀 Prévisualisation")
            st.video(st.session_state.preview_video)

# === TAB 3: AUDIO ===
with tab3:
    st.markdown('<div class="section-header"><h2>🎵 Gestion Audio</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.current_project["audio_clips"]:
        st.markdown("### 🎵 Pistes Audio Disponibles")
        
        for audio_clip in st.session_state.current_project["audio_clips"]:
            with st.expander(f"🎵 {audio_clip['name']}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if os.path.exists(audio_clip["path"]):
                        st.audio(audio_clip["path"])
                
                with col2:
                    volume = st.slider(
                        "Volume (%)", 
                        0, 200, 100, 
                        key=f"volume_{audio_clip['id']}"
                    )
                    audio_clip['volume'] = volume / 100.0
                    
                    fade_in = st.number_input(
                        "Fade In (s)", 
                        0.0, 5.0, 0.0, 0.1,
                        key=f"fadein_{audio_clip['id']}"
                    )
                    audio_clip['fade_in'] = fade_in
                    
                    fade_out = st.number_input(
                        "Fade Out (s)", 
                        0.0, 5.0, 0.0, 0.1,
                        key=f"fadeout_{audio_clip['id']}"
                    )
                    audio_clip['fade_out'] = fade_out
        
        st.markdown("### 🎚️ Mixage Audio")
        
        if st.session_state.current_project["timeline"]:
            audio_options = st.multiselect(
                "Sélectionner les pistes audio à ajouter:",
                options=[clip['name'] for clip in st.session_state.current_project["audio_clips"]],
                key="selected_audio_tracks"
            )
            
            if st.button("🎵 Appliquer Audio à la Timeline"):
                st.session_state.current_project["selected_audio"] = audio_options
                st.success(f"✅ {len(audio_options)} piste(s) audio sélectionnée(s)")
        
        else:
            st.warning("Créez d'abord une timeline vidéo dans l'onglet Montage")
    
    else:
        st.warning("Aucun fichier audio importé. Allez dans l'onglet Import pour ajouter de l'audio.")

# === TAB 4: EFFETS ===
with tab4:
    st.markdown('<div class="section-header"><h2>🎨 Effets Visuels</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✨ Effets de Base")
        
        # Luminosité et contraste
        brightness = st.slider("💡 Luminosité", -50, 50, 0)
        contrast = st.slider("🔆 Contraste", 0.5, 2.0, 1.0, 0.1)
        
        # Couleurs
        saturation = st.slider("🌈 Saturation", 0.0, 2.0, 1.0, 0.1)
        
        # Vitesse
        speed_factor = st.slider("⚡ Vitesse", 0.25, 4.0, 1.0, 0.25)
    
    with col2:
        st.markdown("### 🎭 Effets Avancés")
        
        # Filtres
        apply_blur = st.checkbox("🌫️ Flou gaussien")
        if apply_blur:
            blur_sigma = st.slider("Intensité du flou", 1, 10, 3)
        
        apply_mirror = st.checkbox("🪞 Effet miroir")
        mirror_axis = st.selectbox("Axe du miroir:", ["horizontal", "vertical"]) if apply_mirror else None
        
        # Transitions
        st.markdown("### 🔄 Transitions")
        transition_type = st.selectbox(
            "Type de transition:",
            ["Aucune", "Fondu", "Glissement", "Zoom"]
        )
        
        if transition_type != "Aucune":
            transition_duration = st.slider("Durée transition (s)", 0.5, 3.0, 1.0, 0.1)
    
    # Sauvegarder les effets
    effects_data = {
        "brightness": brightness,
        "contrast": contrast,
        "saturation": saturation,
        "speed_factor": speed_factor,
        "blur": {"apply": apply_blur, "sigma": blur_sigma if apply_blur else 0},
        "mirror": {"apply": apply_mirror, "axis": mirror_axis if apply_mirror else None},
        "transition": {"type": transition_type, "duration": transition_duration if transition_type != "Aucune" else 0}
    }
    
    st.session_state.current_project["effects"] = effects_data

# === TAB 5: EXPORT ===
with tab5:
    st.markdown('<div class="section-header"><h2>🚀 Export Final</h2></div>', unsafe_allow_html=True)
    
    if not st.session_state.current_project["timeline"]:
        st.warning("⚠️ Aucune timeline créée. Allez dans l'onglet Montage pour créer votre vidéo.")
    else:
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        
        # Résumé du projet
        st.markdown("### 📊 Résumé du Projet")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎬 Clips Vidéo", len(st.session_state.current_project["timeline"]))
        
        with col2:
            audio_count = len(st.session_state.current_project.get("selected_audio", []))
            st.metric("🎵 Pistes Audio", audio_count)
        
        with col3:
            total_duration = sum([
                clip.get('trim_end', 0) - clip.get('trim_start', 0) 
                for clip in st.session_state.current_project["timeline"]
            ])
            st.metric("⏱️ Durée Totale", f"{total_duration:.1f}s")
        
        # Configuration d'export
        st.markdown("### ⚙️ Configuration d'Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            output_name = st.text_input(
                "Nom du fichier de sortie:",
                value=f"{st.session_state.current_project['name']}_final"
            )
        
        with col2:
            quality_settings = {
                "Basse (480p)": {"resolution": (854, 480), "bitrate": "1000k"},
                "Moyenne (720p)": {"resolution": (1280, 720), "bitrate": "2500k"},
                "Haute (1080p)": {"resolution": (1920, 1080), "bitrate": "5000k"},
                "Ultra (4K)": {"resolution": (3840, 2160), "bitrate": "15000k"}
            }
        
        # Bouton d'export
        if st.button("🚀 EXPORTER LA VIDÉO", type="primary", use_container_width=True):
            with st.spinner("🎬 Export en cours... Cela peut prendre plusieurs minutes."):
                try:
                    # Création du clip vidéo final
                    video_clips = []
                    
                    for timeline_clip in st.session_state.current_project["timeline"]:
                        if os.path.exists(timeline_clip["path"]):
                            clip = mp.VideoFileClip(timeline_clip["path"])
                            
                            # Découpage
                            start = timeline_clip.get('trim_start', 0)
                            end = timeline_clip.get('trim_end', clip.duration)
                            
                            if end > start:
                                trimmed_clip = clip.subclip(start, end)
                                
                                # Application des effets
                                effects = st.session_state.current_project.get("effects", {})
                                
                                # Luminosité et contraste
                                if effects.get("brightness", 0) != 0 or effects.get("contrast", 1) != 1:
                                    gamma = 1.0 + effects.get("brightness", 0) / 100.0
                                    trimmed_clip = trimmed_clip.fx(mp.vfx.gamma_corr, gamma)
                                
                                # Vitesse
                                speed = effects.get("speed_factor", 1.0)
                                if speed != 1.0:
                                    trimmed_clip = trimmed_clip.fx(mp.vfx.speedx, speed)
                                
                                # Flou
                                if effects.get("blur", {}).get("apply", False):
                                    blur_sigma = effects["blur"].get("sigma", 3)
                                    trimmed_clip = trimmed_clip.fx(mp.vfx.blur, blur_sigma)
                                
                                # Miroir
                                if effects.get("mirror", {}).get("apply", False):
                                    axis = effects["mirror"].get("axis", "horizontal")
                                    if axis == "horizontal":
                                        trimmed_clip = trimmed_clip.fx(mp.vfx.mirror_x)
                                    else:
                                        trimmed_clip = trimmed_clip.fx(mp.vfx.mirror_y)
                                
                                video_clips.append(trimmed_clip)
                            
                            clip.close()
                    
                    if video_clips:
                        # Concaténation des clips
                        final_video = mp.concatenate_videoclips(video_clips)
                        
                        # Ajout de l'audio si sélectionné
                        selected_audio = st.session_state.current_project.get("selected_audio", [])
                        if selected_audio:
                            audio_clips = []
                            
                            for audio_name in selected_audio:
                                for audio_clip in st.session_state.current_project["audio_clips"]:
                                    if audio_clip["name"] == audio_name and os.path.exists(audio_clip["path"]):
                                        audio = mp.AudioFileClip(audio_clip["path"])
                                        
                                        # Application des effets audio
                                        volume = audio_clip.get('volume', 1.0)
                                        if volume != 1.0:
                                            audio = audio.volumex(volume)
                                        
                                        # Fade in/out
                                        fade_in = audio_clip.get('fade_in', 0)
                                        fade_out = audio_clip.get('fade_out', 0)
                                        
                                        if fade_in > 0:
                                            audio = audio.fadein(fade_in)
                                        if fade_out > 0:
                                            audio = audio.fadeout(fade_out)
                                        
                                        # Ajuster la durée de l'audio à la vidéo
                                        if audio.duration > final_video.duration:
                                            audio = audio.subclip(0, final_video.duration)
                                        elif audio.duration < final_video.duration:
                                            # Boucler l'audio si plus court
                                            loops_needed = int(final_video.duration / audio.duration) + 1
                                            audio = mp.concatenate_audioclips([audio] * loops_needed)
                                            audio = audio.subclip(0, final_video.duration)
                                        
                                        audio_clips.append(audio)
                            
                            if audio_clips:
                                # Mélanger toutes les pistes audio
                                if len(audio_clips) == 1:
                                    final_audio = audio_clips[0]
                                else:
                                    final_audio = mp.CompositeAudioClip(audio_clips)
                                
                                # Combiner vidéo et audio
                                final_video = final_video.set_audio(final_audio)
                        
                        # Configuration de la qualité
                        quality_config = quality_settings[export_quality]
                        target_resolution = quality_config["resolution"]
                        
                        # Redimensionnement si nécessaire
                        if final_video.size != target_resolution:
                            final_video = final_video.resize(target_resolution)
                        
                        # Chemin de sortie
                        output_filename = f"{output_name}.{export_format}"
                        output_path = os.path.join(EXPORTS_DIR, output_filename)
                        
                        # Export final
                        final_video.write_videofile(
                            output_path,
                            fps=export_fps,
                            codec='libx264' if export_format == 'mp4' else 'libxvid',
                            audio_codec='aac' if export_format == 'mp4' else 'mp3',
                            bitrate=quality_config["bitrate"],
                            temp_audiofile='temp-audio.m4a',
                            remove_temp=True,
                            verbose=False,
                            logger=None
                        )
                        
                        # Nettoyage
                        final_video.close()
                        for clip in video_clips:
                            clip.close()
                        if selected_audio and 'final_audio' in locals():
                            final_audio.close()
                        
                        st.success(f"🎉 Export terminé! Fichier sauvegardé: {output_filename}")
                        
                        # Affichage du fichier exporté
                        if os.path.exists(output_path):
                            st.video(output_path)
                            
                            # Bouton de téléchargement
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    f"📥 Télécharger {output_filename}",
                                    data=f.read(),
                                    file_name=output_filename,
                                    mime=f"video/{export_format}",
                                    use_container_width=True
                                )
                        
                        # Statistiques du fichier
                        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                        st.info(f"📊 Taille du fichier: {file_size:.1f} MB")
                    
                    else:
                        st.error("❌ Aucun clip vidéo valide trouvé")
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'export: {str(e)}")
                    st.error("Vérifiez que tous les fichiers existent et que vous avez suffisamment d'espace disque.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Fichiers exportés précédemment
        st.markdown("### 📁 Exports Précédents")
        
        if os.path.exists(EXPORTS_DIR):
            exported_files = [f for f in os.listdir(EXPORTS_DIR) if f.endswith(('.mp4', '.avi', '.mov', '.webm'))]
            
            if exported_files:
                for file in exported_files:
                    file_path = os.path.join(EXPORTS_DIR, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"📹 {file}")
                    
                    with col2:
                        st.write(f"{file_size:.1f} MB")
                    
                    with col3:
                        with open(file_path, "rb") as f:
                            st.download_button(
                                "📥",
                                data=f.read(),
                                file_name=file,
                                mime=f"video/{file.split('.')[-1]}",
                                key=f"download_{file}"
                            )
            else:
                st.info("Aucun export précédent trouvé")

# === SECTION STATUS ET DEBUG ===
st.markdown("---")

with st.expander("🔧 Informations de Debug", expanded=False):
    st.markdown("### 📊 État du Projet Actuel")
    st.json(st.session_state.current_project)
    
    st.markdown("### 📁 Fichiers Temporaires")
    if os.path.exists(TEMP_DIR):
        temp_files = os.listdir(TEMP_DIR)
        st.write(f"Fichiers dans temp: {len(temp_files)}")
        for file in temp_files[:10]:  # Afficher seulement les 10 premiers
            file_path = os.path.join(TEMP_DIR, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                st.write(f"- {file}: {size:.2f} MB")
        
        if len(temp_files) > 10:
            st.write(f"... et {len(temp_files) - 10} autres fichiers")
    
    # Bouton de nettoyage
    if st.button("🧹 Nettoyer les fichiers temporaires"):
        try:
            for file in os.listdir(TEMP_DIR):
                file_path = os.path.join(TEMP_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            st.success("✅ Fichiers temporaires supprimés!")
        except Exception as e:
            st.error(f"Erreur lors du nettoyage: {e}")

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 20px;">
    <h4>🎬 Video Editor Pro</h4>
    <p>Un éditeur vidéo complet créé avec Streamlit et MoviePy</p>
    <p><strong>Fonctionnalités:</strong> Import • Montage • Audio • Effets • Export</p>
</div>
""", unsafe_allow_html=True)

# === RACCOURCIS CLAVIER INFO ===
st.sidebar.markdown("---")
st.sidebar.markdown("""
## ⌨️ Tips
- **Import**: Drag & drop multiple files
- **Timeline**: Ajustez les temps précisément
- **Audio**: Plusieurs pistes supportées
- **Export**: Haute qualité disponible
- **Sauvegarde**: Auto-sauvegarde recommandée
""")

# === AIDE ===
with st.sidebar.expander("❓ Aide"):
    st.markdown("""
    **🚀 Guide Rapide:**
    
    1. **Import** des médias (vidéos/audio)
    2. **Montage** timeline avec découpage
    3. **Audio** ajout et mixage
    4. **Effets** visuels et transitions
    5. **Export** en haute qualité
    
    **💡 Conseils:**
    - Sauvegardez régulièrement
    - Utilisez des vidéos courtes pour les tests
    - L'export peut prendre du temps
    - Vérifiez l'espace disque disponible
    """)

# === GESTION DES ERREURS GLOBALES ===
if "error_log" not in st.session_state:
    st.session_state.error_log = []

def log_error(error_msg):
    st.session_state.error_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": str(error_msg)
    })

# === AUTO-SAVE ===
if st.button("💾 Sauvegarde Auto", key="auto_save_hidden", help="Sauvegarde automatique"):
    save_project(st.session_state.current_project, st.session_state.current_project["name"])
    st.toast("✅ Projet sauvegardé automatiquement!")
