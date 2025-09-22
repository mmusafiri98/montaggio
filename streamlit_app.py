from diffusers import StableDiffusionInpaintPipeline

# === PIPELINE INPAINT (editor) ===
@st.cache_resource
def load_inpaint_model():
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",
        torch_dtype=torch.float16
    )
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    return pipe

if "inpaint_pipe" not in st.session_state:
    st.session_state.inpaint_pipe = load_inpaint_model()


# === SUBMIT LOGIC ===
if submit:
    # IMAGE UPLOAD
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        image_path = os.path.join(CHAT_DIR, f"img_{uuid.uuid4().hex}.png")
        image.save(image_path)

        if st.session_state.mode == "describe":
            # DESCRIZIONE
            caption = generate_caption(image, st.session_state.processor, st.session_state.model)
            query = f"Description image: {caption}. {user_message}" if user_message else f"Description image: {caption}"
            response = llama_predict(query)

            st.session_state.chat_history.append({
                "role": "user",
                "content": user_message or "Image envoyée",
                "image": image_path,
                "type": "describe"
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "type": "describe"
            })

        else:  # EDIT MODE
            # Genera una maschera vuota (intera immagine modificabile)
            mask = Image.new("L", image.size, 255)  # 255 = area da modificare

            prompt = user_message if user_message else "Make some edits"
            edited_image = st.session_state.inpaint_pipe(prompt=prompt, image=image, mask_image=mask).images[0]
            edited_image_path = os.path.join(EDITED_IMAGES_DIR, f"edited_{uuid.uuid4().hex}.png")
            edited_image.save(edited_image_path)

            st.session_state.chat_history.append({
                "role": "user",
                "content": user_message,
                "image": image_path,
                "type": "edit"
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Image modifiée selon l'instruction: {user_message}",
                "edited_image": edited_image_path,
                "type": "edit"
            })

        save_chat_history(st.session_state.chat_history, st.session_state.chat_id)

    # TEXT ONLY
    elif user_message:
        response = llama_predict(user_message)
        st.session_state.chat_history.append({"role": "user", "content": user_message, "type": "text"})
        st.session_state.chat_history.append({"role": "assistant", "content": response, "type": "text"})
        save_chat_history(st.session_state.chat_history, st.session_state.chat_id)
