import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from gradio_client import Client
import io
import os
import base64

# -------------------------
# Configuration Streamlit
# -------------------------
st.set_page_config(page_title="Vision AI Chat - Typing Effect", layout="wide")

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
# Édition d’image avec Qwen
# -------------------------
EDITED_IMAGES_DIR = "edited_images"
os.makedirs(EDITED_IMAGES_DIR, exist_ok=True)

def edit_image_with_qwen(image, edit_instruction, client):
    try:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
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
    
    processor, model = load_blip()

    # Remplacez par votre vrai espace Hugging Face
    qwen_client = Client("muryshev/Qwen-Image-Edit")  

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
