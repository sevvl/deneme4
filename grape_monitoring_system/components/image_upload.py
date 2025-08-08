import streamlit as st
from PIL import Image
import io

def image_upload_component():
    st.header("📷 Görüntü Yükle")

    uploaded_file = st.file_uploader("Görüntü Yükle", type=["png", "jpg", "jpeg", "webp"])

    camera_image = st.camera_input("Veya kameradan görüntü çek")

    image_data = None
    image_name = None

    if uploaded_file is not None:
        image_data = uploaded_file.read()
        image_name = uploaded_file.name
        st.image(image_data, caption='Yüklenen Görüntü', use_container_width=True)
    elif camera_image is not None:
        image_data = camera_image.read()
        image_name = f"camera_capture_{len(st.session_state.get('analyses', [])) + 1}.jpeg"
        st.image(image_data, caption='Kameradan Çekilen Görüntü', use_container_width=True)
    
    return image_data, image_name

