# streamlit_app.py - Video Editor Simple
import streamlit as st
import subprocess
import tempfile
import os
import uuid
import json
from datetime import datetime
import shutil

# === CONFIG ===
st.set_page_config(
    page_title="🎬 Video Editor Lite",
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
</style>
""", unsafe_allow_html=True)

# === UTILS ===
def save_uploaded_file(uploaded_file, file_type="video"):
    """Sauvegarde un fichier uploadé"""
    file_extension = uploaded_file.name.split(".")[-1]
    unique_filename = f"{file_type}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(TEMP_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    
    return file_path

def get_video_info_ffprobe(video_path):
    """Obtient les informations vidéo avec ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            # Chercher le stream vidéo
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    return {
                        "duration": float(data.get('format', {}).get('duration', 0)),
                        "width": stream.get('width', 0),
                        "height": stream.get('height', 0),
                        "fps": eval(stream.get('r_frame_rate', '0/1'))
                    }
        return {"error": "Impossible de lire la vidéo"}
    except:
        return {"error": "FFprobe non disponible"}

def merge_videos_ffmpeg(video_paths, output_path):
    """Fusionne les vidéos avec FFmpeg"""
    try:
        # Créer un fichier de liste temporaire
        list_file = os.path.join(TEMP_DIR, f"list_{uuid.uuid4().hex}.txt")
        with open(list_file, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{os.path.abspath(video_path)}'\n")
        
        # Commande FFmpeg
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', 
            '-i', list_file, '-c', 'copy', output_path, '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Nettoyage
        if os.path.exists(list_file):
            os.remove(list_file)
        
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def add_audio_to_video_ffmpeg(video_path, audio_path, output_path):
    """Ajoute l'audio à la vidéo avec FFmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path, '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', output_path, '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def trim_video_ffmpeg(input_path, start_time, end_time, output_path):
    """Découpe une vidéo avec FFmpeg"""
    try:
        duration = end_time - start_time
        cmd = [
            'ffmpeg', '-i', input_path, '-ss', str(start_time), 
            '-t', str(duration), '-c', 'copy', output_path, '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

# === SESSION STATE ===
if "video_clips" not in st.session_state:
    st.session_state.video_clips = []

if "audio_clips" not in st.session_state:
    st.session_state.audio_clips = []

if "timeline" not in st.session_state:
    st.session_state.timeline = []

# === HEADER ===
st.markdown('<h1 class="main-header">🎬 Video Editor Lite</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: white; font-size: 1.2rem;">Édition vidéo simple avec FFmpeg</p>', unsafe_allow_html=True)

# === VÉRIFICATION FFMPEG ===
def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

if not check_ffmpeg():
    st.error("""
    ❌ **FFmpeg non détecté !**
    
    Pour utiliser cet éditeur, vous devez installer FFmpeg :
    
    **Windows :** Téléchargez depuis https://ffmpeg.org/download.html
    **macOS :** `brew install ffmpeg`
    **Linux :** `sudo apt install ffmpeg` ou `sudo yum install ffmpeg`
    """)
    st.stop()
else:
    st.success("✅ FFmpeg détecté et prêt !")

# === TABS ===
tab1, tab2, tab3, tab4 = st.tabs(["📥 Import", "✂️ Montage", "🎵 Audio", "🚀 Export"])

# === TAB 1: IMPORT ===
with tab1:
    st.markdown('<div class="section-header"><h2>📥 Import de Médias</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎬 Vidéos")
        uploaded_videos = st.file_uploader(
            "Choisir des vidéos:",
            type=["mp4", "avi", "mov", "mkv", "webm"],
            accept_multiple_files=True,
            key="video_uploader"
        )
        
        if uploaded_videos:
            for video in uploaded_videos:
                if st.button(f"➕ Ajouter {video.name}", key=f"add_video_{video.name}"):
                    with st.spinner(f"Traitement de {video.name}..."):
                        video_path = save_uploaded_file(video, "video")
                        video_info = get_video_info_ffprobe(video_path)
                        
                        clip_data = {
                            "name": video.name,
                            "path": video_path,
                            "info": video_info,
                            "start_time": 0,
                            "end_time": video_info.get("duration", 0)
                        }
                        
                        st.session_state.video_clips.append(clip_data)
                        st.success(f"✅ {video.name} ajoutée!")
                        st.rerun()
    
    with col2:
        st.markdown("### 🎵 Audio")
        uploaded_audios = st.file_uploader(
            "Choisir des fichiers audio:",
            type=["mp3", "wav", "aac", "ogg"],
            accept_multiple_files=True,
            key="audio_uploader"
        )
        
        if uploaded_audios:
            for audio in uploaded_audios:
                if st.button(f"➕ Ajouter {audio.name}", key=f"add_audio_{audio.name}"):
                    audio_path = save_uploaded_file(audio, "audio")
                    
                    clip_data = {
                        "name": audio.name,
                        "path": audio_path
                    }
                    
                    st.session_state.audio_clips.append(clip_data)
                    st.success(f"✅ {audio.name} ajouté!")
                    st.rerun()
    
    # Affichage des médias
    if st.session_state.video_clips:
        st.markdown("### 🎬 Vidéos Importées")
        for i, clip in enumerate(st.session_state.video_clips):
            with st.expander(f"🎬 {clip['name']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                with col1:
                    if os.path.exists(clip["path"]):
                        st.video(clip["path"])
                with col2:
                    info = clip.get("info", {})
                    st.write(f"**Durée:** {info.get('duration', 0):.2f}s")
                    st.write(f"**Résolution:** {info.get('width', 'N/A')}x{info.get('height', 'N/A')}")
                    if st.button("🗑️ Supprimer", key=f"del_video_{i}"):
                        st.session_state.video_clips.pop(i)
                        st.rerun()
    
    if st.session_state.audio_clips:
        st.markdown("### 🎵 Audio Importé")
        for i, clip in enumerate(st.session_state.audio_clips):
            with st.expander(f"🎵 {clip['name']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                with col1:
                    if os.path.exists(clip["path"]):
                        st.audio(clip["path"])
                with col2:
                    if st.button("🗑️ Supprimer", key=f"del_audio_{i}"):
                        st.session_state.audio_clips.pop(i)
                        st.rerun()

# === TAB 2: MONTAGE ===
with tab2:
    st.markdown('<div class="section-header"><h2>✂️ Montage Vidéo</h2></div>', unsafe_allow_html=True)
    
    if not st.session_state.video_clips:
        st.warning("Aucune vidéo importée. Allez dans l'onglet Import.")
    else:
        st.markdown("### ⏱️ Découpage des Clips")
        
        for i, clip in enumerate(st.session_state.video_clips):
            with st.expander(f"✂️ {clip['name']}", expanded=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                max_duration = clip["info"].get("duration", 0)
                
                with col1:
                    st.write(f"Durée originale: {max_duration:.2f}s")
                
                with col2:
                    start = st.number_input(
                        "Début (s)", 
                        min_value=0.0,
                        max_value=max_duration,
                        value=clip.get("start_time", 0.0),
                        step=0.1,
                        key=f"start_{i}"
                    )
                    clip["start_time"] = start
                
                with col3:
                    end = st.number_input(
                        "Fin (s)", 
                        min_value=start,
                        max_value=max_duration,
                        value=clip.get("end_time", max_duration),
                        step=0.1,
                        key=f"end_{i}"
                    )
                    clip["end_time"] = end
                
                # Ajout à la timeline
                if st.button(f"➕ Ajouter à la Timeline", key=f"timeline_{i}"):
                    timeline_clip = clip.copy()
                    timeline_clip["timeline_pos"] = len(st.session_state.timeline)
                    st.session_state.timeline.append(timeline_clip)
                    st.success("Ajouté à la timeline!")
                    st.rerun()
        
        # Timeline actuelle
        if st.session_state.timeline:
            st.markdown("### 🎬 Timeline Actuelle")
            
            total_duration = 0
            for i, t_clip in enumerate(st.session_state.timeline):
                duration = t_clip["end_time"] - t_clip["start_time"]
                total_duration += duration
                
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.write(f"🎬 {t_clip['name']}")
                with col2:
                    st.write(f"⏱️ {duration:.2f}s")
                with col3:
                    st.write(f"📍 #{i+1}")
                with col4:
                    if st.button("🗑️", key=f"remove_timeline_{i}"):
                        st.session_state.timeline.pop(i)
                        st.rerun()
            
            st.info(f"**Durée totale:** {total_duration:.2f}s")
            
            if st.button("🗑️ Vider Timeline"):
                st.session_state.timeline = []
                st.rerun()

# === TAB 3: AUDIO ===
with tab3:
    st.markdown('<div class="section-header"><h2>🎵 Gestion Audio</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.audio_clips:
        selected_audio = st.selectbox(
            "Choisir une piste audio:",
            options=["Aucune"] + [clip["name"] for clip in st.session_state.audio_clips]
        )
        
        if selected_audio != "Aucune":
            st.success(f"🎵 Audio sélectionné: {selected_audio}")
        
        # Prévisualisation audio
        for clip in st.session_state.audio_clips:
            if clip["name"] == selected_audio:
                st.audio(clip["path"])
                break
    else:
        st.warning("Aucun fichier audio importé.")
        selected_audio = "Aucune"

# === TAB 4: EXPORT ===
with tab4:
    st.markdown('<div class="section-header"><h2>🚀 Export Final</h2></div>', unsafe_allow_html=True)
    
    if not st.session_state.timeline:
        st.warning("Aucune timeline créée. Allez dans l'onglet Montage.")
    else:
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        
        # Configuration d'export
        col1, col2 = st.columns(2)
        
        with col1:
            output_name = st.text_input("Nom du fichier:", value="video_final")
            export_format = st.selectbox("Format:", ["mp4", "avi", "mov"])
        
        with col2:
            quality = st.selectbox("Qualité:", ["Originale", "Haute", "Moyenne", "Basse"])
            
            # Paramètres selon la qualité
            quality_params = {
                "Originale": ["-c", "copy"],
                "Haute": ["-crf", "18", "-preset", "slow"],
                "Moyenne": ["-crf", "23", "-preset", "medium"],
                "Basse": ["-crf", "28", "-preset", "fast"]
            }
        
        # Bouton d'export
        if st.button("🚀 EXPORTER LA VIDÉO", type="primary", use_container_width=True):
            with st.spinner("🎬 Export en cours..."):
                try:
                    # Étape 1: Découper les clips individuels
                    trimmed_clips = []
                    
                    for i, t_clip in enumerate(st.session_state.timeline):
                        trimmed_path = os.path.join(TEMP_DIR, f"trimmed_{i}_{uuid.uuid4().hex}.{export_format}")
                        
                        success, error = trim_video_ffmpeg(
                            t_clip["path"],
                            t_clip["start_time"],
                            t_clip["end_time"],
                            trimmed_path
                        )
                        
                        if success:
                            trimmed_clips.append(trimmed_path)
                        else:
                            st.error(f"Erreur découpage {t_clip['name']}: {error}")
                            break
                    
                    if len(trimmed_clips) == len(st.session_state.timeline):
                        # Étape 2: Fusionner les clips
                        merged_path = os.path.join(TEMP_DIR, f"merged_{uuid.uuid4().hex}.{export_format}")
                        
                        if len(trimmed_clips) == 1:
                            # Un seul clip
                            shutil.copy2(trimmed_clips[0], merged_path)
                        else:
                            # Fusion multiple
                            success, error = merge_videos_ffmpeg(trimmed_clips, merged_path)
                            if not success:
                                st.error(f"Erreur fusion: {error}")
                                raise Exception("Échec de la fusion")
                        
                        # Étape 3: Ajouter l'audio si sélectionné
                        final_path = os.path.join(EXPORTS_DIR, f"{output_name}.{export_format}")
                        
                        if selected_audio != "Aucune":
                            audio_clip = next(
                                (clip for clip in st.session_state.audio_clips if clip["name"] == selected_audio), 
                                None
                            )
                            
                            if audio_clip:
                                success, error = add_audio_to_video_ffmpeg(
                                    merged_path, audio_clip["path"], final_path
                                )
                                if not success:
                                    st.error(f"Erreur audio: {error}")
                                    # Copier sans audio en cas d'échec
                                    shutil.copy2(merged_path, final_path)
                            else:
                                shutil.copy2(merged_path, final_path)
                        else:
                            shutil.copy2(merged_path, final_path)
                        
                        # Nettoyage des fichiers temporaires
                        for temp_file in trimmed_clips + [merged_path]:
                            if os.path.exists(temp_file):
                                try:
                                    os.remove(temp_file)
                                except:
                                    pass
                        
                        if os.path.exists(final_path):
                            st.success(f"🎉 Export terminé! {output_name}.{export_format}")
                            
                            # Affichage du résultat
                            st.video(final_path)
                            
                            # Téléchargement
                            with open(final_path, "rb") as f:
                                st.download_button(
                                    f"📥 Télécharger {output_name}.{export_format}",
                                    data=f.read(),
                                    file_name=f"{output_name}.{export_format}",
                                    mime=f"video/{export_format}",
                                    use_container_width=True
                                )
                            
                            # Statistiques
                            file_size = os.path.getsize(final_path) / (1024 * 1024)
                            st.info(f"📊 Taille: {file_size:.1f} MB")
                        
                        else:
                            st.error("❌ Échec de l'export")
                    
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 20px;">
    <h4>🎬 Video Editor Lite</h4>
    <p>Éditeur vidéo simple utilisant FFmpeg</p>
    <p><strong>Fonctions:</strong> Import • Découpage • Timeline • Audio • Export</p>
</div>
""", unsafe_allow_html=True)
