import streamlit as st
from urllib.parse import urlencode
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

oauth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://oauth2.googleapis.com/token"

def get_google_login_url():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{oauth_base_url}?{urlencode(params)}"

def exchange_code_for_tokens(code: str):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    return response.json()

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
            "picture": id_info.get("picture")
        }
    except Exception as e:
        st.error(f"❌ Failed to verify token: {e}")
        return None

def login_user():
    query = st.query_params
    if "code" in query:
        tokens = exchange_code_for_tokens(query["code"])
        id_token_str = tokens.get("id_token")
        if id_token_str:
            user = get_user_info(id_token_str)
            if user:
                st.session_state.user = user
                st.query_params.clear()

    if "user" not in st.session_state:
        login_url = get_google_login_url()
        st.markdown(f"[🔐 Log in with Google]({login_url})", unsafe_allow_html=True)
        st.stop()
    return st.session_state.user

def logout_user():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
