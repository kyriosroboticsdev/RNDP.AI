# app.py

import streamlit as st
import os
import time
import uuid
import tempfile
from pydantic import BaseModel
from helpers import (
    structured_generator,
    get_ai_recommended_image,
    extract_text_from_slide_file
)
from db import initialize_db, save_slide, get_user_slides, add_user
from google_auth import login_user, logout_user

# App setup
st.set_page_config(page_title="RNDP.AI", layout="centered")

# Initialize DB
initialize_db()

# Session timeout config
SESSION_TIMEOUT = 30 * 60
if "login_time" in st.session_state:
    if time.time() - st.session_state["login_time"] > SESSION_TIMEOUT:
        st.session_state.clear()
        st.warning("Session expired. Please log in again.")
        st.stop()

# Authenticate user
user_info = login_user()
if not user_info:
    st.stop()

# Register user if not in DB
username = user_info["email"].split("@")[0].lower()
add_user(username, user_info["name"], user_info["email"])

# Sidebar logout
st.sidebar.markdown(f"Logged in as: `{user_info['email']}`")
logout_user()

# Navigation
st.title("RNDP.AI")
menu = st.selectbox("Select a page", ["Generate Slide", "My Slides"])

# Output model
class SlideOutput(BaseModel):
    pptx_bytes: bytes

# Page: Generate Slide
if menu == "Generate Slide":
    st.subheader("Generate a New Slide")

    input_text = st.text_area("Slide Topic", help="Enter a brief notebook entry or description")
    template_file = st.file_uploader("Upload Template (.pptx)", type=["pptx"])
    image_file = st.file_uploader("Upload Image (optional)", type=["png", "jpg", "jpeg"])

    fallback_images = os.listdir("images") if os.path.exists("images") else []
    fallback_image_choice = None
    if not image_file and fallback_images:
        ai_choice = get_ai_recommended_image(input_text, fallback_images)
        fallback_image_choice = st.selectbox("Select fallback image", fallback_images, index=fallback_images.index(ai_choice))

    font_name = st.selectbox("Font Style", ["Calibri", "Arial", "Times New Roman", "Verdana"])
    font_color = st.color_picker("Font Color", "#000000")[1:]

    if st.button("Generate Slide"):
        if not input_text or not template_file:
            st.warning("Both a topic and a template are required.")
            st.stop()

        result = structured_generator(
            model_name="gpt-4",
            prompt="Generate robotics notebook content.",
            output_model=SlideOutput,
            template_file=template_file,
            content_text=input_text,
            image_file=image_file,
            font_name=font_name,
            font_color=font_color,
            fallback_image_filename=fallback_image_choice
        )

        os.makedirs("slides", exist_ok=True)
        slide_filename = f"slides/{username}_page{uuid.uuid4().hex[:4]}.pptx"
        with open(slide_filename, "wb") as f:
            f.write(result.pptx_bytes)

        title = input_text.split("\n")[0][:40]
        save_slide(username, title, slide_filename)

        st.success("Slide successfully generated and saved.")
        st.download_button("Download Slide", result.pptx_bytes, file_name=os.path.basename(slide_filename))

# Page: My Slides
elif menu == "My Slides":
    st.subheader("My Saved Slides")

    slides = get_user_slides(username)
    if not slides:
        st.info("No saved slides found.")
        st.stop()

    for title, date_created, path in slides:
        st.markdown(f"**{title}**  \n_Created on {date_created}_")
        with open(path, "rb") as f:
            st.download_button("Download", f, file_name=os.path.basename(path))
