import streamlit as st
import os, uuid, json, base64
from datetime import datetime

st.set_page_config(page_title="🎬 Video Editor", layout="wide")

# === UTILS ===
def save_file(uploaded_file, folder="uploads"):
    os.makedirs(folder, exist_ok=True)
    ext = uploaded_file.name.split(".")[-1]
    fname = f"{uuid.uuid4().hex}.{ext}"
    fpath = os.path.join(folder, fname)
    with open(fpath, "wb") as f:
        f.write(uploaded_file.read())
    return fpath

def download_link(path, name):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<a href="data:file/zip;base64,{b64}" download="{name}">📥 Télécharger</a>'

# === INIT STATE ===
for key, val in {
    "videos": [],
    "audios": [],
    "timeline": [],
    "step": 1
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# === HEADER ===
st.title("🎬 Video Editor Pure Python")

# === NAVIGATION ===
steps = ["Import", "Montage", "Audio", "Export"]
st.session_state.step = st.sidebar.radio("Étapes", range(1, 5), format_func=lambda i: steps[i-1])

# === ÉTAPE 1: IMPORT ===
if st.session_state.step == 1:
    st.header("📥 Import")
    vids = st.file_uploader("Importer des vidéos", ["mp4","mov","avi"], accept_multiple_files=True)
    for v in vids:
        path = save_file(v, "videos")
        st.session_state.videos.append({"name": v.name, "path": path})
    auds = st.file_uploader("Importer des audios", ["mp3","wav"], accept_multiple_files=True)
    for a in auds:
        path = save_file(a, "audios")
        st.session_state.audios.append({"name": a.name, "path": path})

# === ÉTAPE 2: MONTAGE ===
elif st.session_state.step == 2:
    st.header("✂️ Montage")
    st.subheader("📚 Vidéos disponibles")
    for i, clip in enumerate(st.session_state.videos):
        st.write(f"🎬 {clip['name']}")
        st.video(clip["path"])
        if st.button(f"Ajouter {clip['name']} à la timeline", key=f"add{i}"):
            st.session_state.timeline.append(clip)

    st.subheader("🎬 Timeline")
    if st.session_state.timeline:
        for i, tclip in enumerate(st.session_state.timeline):
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.write(f"#{i+1} - {tclip['name']}")
                st.video(tclip["path"])
            with col2:
                if i > 0 and st.button("⬆️", key=f"up{i}"):
                    st.session_state.timeline[i], st.session_state.timeline[i-1] = st.session_state.timeline[i-1], st.session_state.timeline[i]
                    st.experimental_rerun()
                if i < len(st.session_state.timeline)-1 and st.button("⬇️", key=f"down{i}"):
                    st.session_state.timeline[i], st.session_state.timeline[i+1] = st.session_state.timeline[i+1], st.session_state.timeline[i]
                    st.experimental_rerun()
            with col3:
                if st.button("🗑️", key=f"del{i}"):
                    st.session_state.timeline.pop(i)
                    st.experimental_rerun()
    else:
        st.info("Timeline vide. Ajoutez des vidéos pour commencer.")

# === ÉTAPE 3: AUDIO ===
elif st.session_state.step == 3:
    st.header("🎵 Audio")
    choices = st.multiselect("Choisir audio:", [a["name"] for a in st.session_state.audios])
    for a in st.session_state.audios:
        if a["name"] in choices:
            st.audio(a["path"])

# === ÉTAPE 4: EXPORT ===
elif st.session_state.step == 4:
    st.header("📦 Export")
    proj = {
        "videos": st.session_state.timeline,
        "audios": st.session_state.audios,
        "date": datetime.now().isoformat()
    }
    path = "project.json"
    with open(path, "w", encoding="utf-8") as f: json.dump(proj, f, indent=2)
    st.markdown(download_link(path, "project.json"), unsafe_allow_html=True)


