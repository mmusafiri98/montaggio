import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from gradio_client import Client
import time
import io
import base64
import os

# -------------------------
# Configuration Streamlit
# -------------------------
st.set_page_config(page_title="Vision AI Chat - Typing Effect", layout="wide")

SYSTEM_PROMPT = """You are Vision AI.
You were created by Pepe Musafiri, an Artificial Intelligence Engineer,
with contributions from Meta AI.
Your role is to help users with any task they need, from image analysis
and editing to answering questions clearly and helpfully.
Always answer naturally as Vision AI.

When you receive an image description starting with [IMAGE], you should:
1. Acknowledge that you can see and analyze the image
2. Provide detailed analysis of what you observe
3. Answer any specific questions about the image
4. Be helpful and descriptive in your analysis"""

# -------------------------
# BLIP
# -------------------------
@st.cache_resource
def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

def generate_caption(image, processor, model):
    inputs = processor(image, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = inputs.to("cuda")
        model = model.to("cuda")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=50, num_beams=5)
    return processor.decode(out[0], skip_special_tokens=True)

# -------------------------
# Image <-> Base64
# -------------------------
def image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def base64_to_image(img_str):
    return Image.open(io.BytesIO(base64.b64decode(img_str)))

# -------------------------
# LLaMA Client
# -------------------------
@st.cache_resource
def load_llama():
    try:
        return Client("muryshev/LLaMA-3.1-70b-it-NeMo")
    except Exception as e:
        st.error(f"Erreur lors du chargement de LLaMA: {e}")
        return None

llama_client = load_llama()

def get_ai_response(prompt):
    if not llama_client:
        return "Vision AI non disponible."
    try:
        resp = llama_client.predict(
            message=str(prompt),
            max_tokens=8192,
            temperature=0.7,
            top_p=0.95,
            api_name="/chat"
        )
        return str(resp)
    except Exception as e:
        return f"Erreur modèle: {e}"

# ======================================================
# ===============  ÉDITION D’IMAGE =====================
# ======================================================

EDITED_IMAGES_DIR = "edited_images"
os.makedirs(EDITED_IMAGES_DIR, exist_ok=True)

def edit_image_with_qwen(image, edit_instruction, client):
    """
    Édite une image en utilisant Qwen-Image-Edit.
    Retourne l'image éditée et un message de statut.
    """
    try:
        # Convertir l'image en format acceptable par Gradio
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        result = client.predict(
            image=img_bytes,
            prompt=edit_instruction,
            seed=0,
            randomize_seed=True,
            true_guidance_scale=4,
            num_inference_steps=50,
            rewrite_prompt=True,
            api_name="/infer"
        )
        
        if isinstance(result, tuple) and len(result) >= 1:
            edited_image = Image.open(io.BytesIO(result[0]))
            return edited_image, f"✅ Image éditée selon : '{edit_instruction}'"
        else:
            return None, f"❌ Résultat inattendu : {result}"
    except Exception as e:
        return None, f"Erreur édition : {e}"

# -------------------------
# Streamlit App
# -------------------------
def main():
    st.title("Vision AI Chat")
    
    # Charger les modèles
    processor, model = load_blip()
    qwen_client = Client("Qwen-Image-Edit-model-path")  # Remplacez par le bon chemin
    
    # Interface utilisateur
    uploaded_file = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])
    edit_instruction = st.text_input("Instructions d'édition...")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Image uploadée.', use_column_width=True)
        
        if st.button("Éditer l'image"):
            edited_image, status = edit_image_with_qwen(image, edit_instruction, qwen_client)
            if edited_image:
                st.image(edited_image, caption=status, use_column_width=True)
            else:
                st.error(status)

if __name__ == "__main__":
    main()
