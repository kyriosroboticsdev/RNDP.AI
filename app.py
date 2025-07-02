# app.py

import streamlit as st
import os
import uuid
import tempfile
from pydantic import BaseModel
from pdf2image import convert_from_bytes

from google_auth import login_user, logout_user
from helpers import structured_generator, get_ai_recommended_image
from db import initialize_db, save_slide, get_user_slides, add_user

# Set Streamlit page layout
st.set_page_config(page_title="Robotics Slide Generator", layout="centered")

# Initialize local database
initialize_db()

# Authenticate with Google and register user
user = login_user()
username = user["email"].split("@")[0].lower()
add_user(username, user["name"], user["email"])

# Sidebar logout
st.sidebar.markdown(f"👤 Logged in as `{user['email']}`")
logout_user()

# AI output model
class SlideOutput(BaseModel):
    pptx_bytes: bytes

# App title + menu
st.title("🤖 AI-Powered Robotics Slide Generator")
menu = st.selectbox("📚 Choose a Page:", ["Generate Slide", "My Slides"])

if menu == "Generate Slide":
    st.subheader("📝 Generate a New Slide")

    input_text = st.text_area("Slide content:", placeholder="Our robot passed the claw test.")
    template_file = st.file_uploader("Upload a .pptx template", type=["pptx"])
    image_file = st.file_uploader("Optional image", type=["png", "jpg", "jpeg"])

    fallback_images = os.listdir("images") if os.path.exists("images") else []
    fallback_image_choice = st.selectbox("Fallback image (if no upload):", fallback_images)

    font_name = st.selectbox("Font:", ["Calibri", "Arial", "Times New Roman", "Verdana"])
    font_color = st.color_picker("Font color", "#000000")[1:]

    if st.button("🚀 Generate Slide"):
        if not input_text or not template_file:
            st.warning("Please upload a template and write slide content.")
        else:
            result = structured_generator(
                model_name="gpt-4",
                prompt="Generate robotics content",
                output_model=SlideOutput,
                template_file=template_file,
                content_text=input_text,
                image_file=image_file,
                font_name=font_name,
                font_color=font_color,
                fallback_image_filename=fallback_image_choice
            )

            title = input_text.split("\n")[0][:40]
            filename = f"slides/{username}_page{uuid.uuid4().hex[:4]}.pptx"
            with open(filename, "wb") as f:
                f.write(result.pptx_bytes)

            save_slide(username, title, filename)
            st.success("✅ Slide generated and saved!")

            # Preview each slide
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_pptx:
                    temp_pptx.write(result.pptx_bytes)
                    temp_pptx.flush()
                    slides = convert_from_bytes(open(temp_pptx.name, "rb").read(), dpi=150)
                    for i, img in enumerate(slides):
                        st.image(img, caption=f"Slide {i+1}", use_column_width=True)
            except Exception as e:
                st.warning(f"⚠️ Preview error: {e}")

            st.download_button("⬇️ Download Slide", result.pptx_bytes, file_name=os.path.basename(filename))

elif menu == "My Slides":
    st.subheader("📁 Your Slides")
    slides = get_user_slides(username)
    if not slides:
        st.info("No slides yet.")
    else:
        for title, date_created, path in slides:
            st.markdown(f"### 📄 {title}")
            st.caption(f"_Created on {date_created}_")

            try:
                with open(path, "rb") as f:
                    pptx_data = f.read()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_pptx:
                    temp_pptx.write(pptx_data)
                    temp_pptx.flush()
                    images = convert_from_bytes(open(temp_pptx.name, "rb").read(), dpi=150)
                    for i, img in enumerate(images):
                        st.image(img, caption=f"Slide {i+1}", use_column_width=True)
            except Exception as e:
                st.warning(f"⚠️ Could not preview: {e}")

            with open(path, "rb") as f:
                st.download_button("⬇️ Download", f, file_name=os.path.basename(path))
