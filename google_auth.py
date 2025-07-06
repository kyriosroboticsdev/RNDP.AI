# google_auth.py

import time
import streamlit as st
from urllib.parse import urlencode
import requests
import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv()

GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

# OAuth URLs
OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

# Generate the login URL for OAuth
def get_google_login_url():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{OAUTH_AUTH_URL}?{urlencode(params)}"

# Exchange auth code for tokens
def exchange_code_for_tokens(code: str):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(OAUTH_TOKEN_URL, data=data)
    return response.json()

# Get user info from id_token
def get_user_info(id_token_str: str):
    try:
        id_info = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return {
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
            "sub": id_info.get("sub")
        }
    except Exception as e:
        st.error("❌ Token validation failed. Possible issues:\n"
                 " - Clock skew (token used too early or late)\n"
                 " - Wrong client ID (audience mismatch)\n"
                 " - Expired token")
        st.caption(f"💥 Validation error: {e}")
        return None

# Main login logic
def login_user():
    query_params = st.query_params

    # Handle callback from Google
    if "code" in query_params:
        code = query_params["code"]
        token_data = exchange_code_for_tokens(code)
        id_token_str = token_data.get("id_token")

        if id_token_str:
            user_info = get_user_info(id_token_str)
            if user_info:
                st.session_state["user"] = user_info
                st.session_state["login_time"] = time.time()
                st.query_params.clear()
                return user_info

    # Already logged in
    if "user" in st.session_state:
        return st.session_state["user"]

    # Not logged in yet — show styled login section
    login_url = get_google_login_url()
    with st.container():
        st.markdown("## Log in to RNDP.AI")
        st.markdown("Please log in with your Google account to access the slide generator.")
        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 20px;'>
                <a href="{login_url}" style='
                    background-color: #4285F4;
                    color: white;
                    padding: 10px 25px;
                    text-decoration: none;
                    font-weight: bold;
                    border-radius: 5px;
                    font-size: 16px;
                    display: inline-block;
                '>Log in with Google</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.stop()

# Logout
def logout_user():
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
