import streamlit as st
import time
import os
from dotenv import load_dotenv

# 1. IMPORT ASMIT'S ENGINES
from chat_engine import ChatRoomManager
from auth_engine import AuthManager

load_dotenv()

# ---------------------------------------------------------
# 2. PAGE SETUP & UI FIDELITY
# ---------------------------------------------------------
st.set_page_config(page_title="Arknok DevSync", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0E1116 !important; color: #E6EDF3 !important; }
    .login-container { max-width: 400px; margin: 10vh auto; padding: 40px; background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; }
    [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363D !important; }
    .stChatInput textarea { font-family: 'Courier New', monospace !important; font-size: 14px !important; background-color: #0D1117 !important; color: #58A6FF !important; }
    div.stButton > button[kind="primary"] { background-color: #FF6B00 !important; color: white !important; border: none !important; font-weight: bold !important; border-radius: 8px !important; }
    [data-testid="column"]:nth-of-type(2) { background-color: #13171C !important; border-left: 1px solid #30363D !important; padding: 20px !important; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. PERSISTENT BACKEND INITIALIZATION
# ---------------------------------------------------------
# We use st.session_state to ensure these objects aren't recreated on every click
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()

if 'manager' not in st.session_state:
    st.session_state.manager = ChatRoomManager()
    st.session_state.manager.create_room("React Hooks Deep Dive", language="TypeScript")
    st.session_state.manager.create_room("Python ML Pipeline", language="Python")
    st.session_state.manager.create_room("Backend API", language="Node.js")
    st.session_state.active_room = "React Hooks Deep Dive"
    st.session_state.latest_ai_fix = "No bugs detected yet. Paste code and tag @ai to begin."

# ---------------------------------------------------------
# 4. FUNCTIONAL AUTHENTICATION FLOW
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.header("🚀 DevSync AI")
        st.caption("Sign in to start coding")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            log_user = st.text_input("Username", key="log_user")
            log_pass = st.text_input("Password", type="password", key="log_pass")
            if st.button("Sign In →", type="primary", use_container_width=True):
                success, msg = st.session_state.auth_manager.login(log_user, log_pass)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = log_user
                    st.rerun()
                else:
                    st.error(msg)
        with tab2:
            reg_user = st.text_input("New Username", key="reg_user")
            reg_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Create Account", use_container_width=True):
                success, msg = st.session_state.auth_manager.signup(reg_user, reg_pass)
                if success: st.success("Account created! Now log in.")
                else: st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# 5. CORE WORKSPACE & LOGIC
# ---------------------------------------------------------
current_room = st.session_state.manager.get_room(st.session_state.active_room)
current_room.join(st.session_state.username)

# RENDER SIDEBAR (Polling fragment for live status)
@st.fragment(run_every="5s")
def render_sidebar():
    with st.sidebar:
        st.subheader("DevSync AI")
        st.write("---")
        st.caption("CHANNELS")
        for room_info in st.session_state.manager.list_rooms():
            if st.button(f"# {room_info['name']}", key=f"nav_{room_info['name']}"):
                st.session_state.active_room = room_info['name']
                st.rerun()
        st.write("---")
        st.caption(f"ONLINE — {len(current_room.members)}")
        for user, status in current_room.members.items():
            st.markdown(f"🟢 **{user}**" if status == "online" else f"⚪ {user}")

render_sidebar()

# MAIN CHAT & AI PANEL
chat_col, ai_col = st.columns([2.5, 1.2], gap="large")

with chat_col:
    st.header(f"# {current_room.name}")
    st.write("---")
    for msg in current_room.messages:
        role = "assistant" if msg["user"] == "AI_Assistant" else "user"
        with st.chat_message(role):
            st.markdown(f"**{msg['user']}** <span style='color:gray; font-size:12px;'>{msg['timestamp']}</span>", unsafe_allow_html=True)
            st.markdown(msg["content"])

    # VS CODE STYLE INPUT & SHADOW TYPING
    if prompt := st.chat_input("Paste code or type @ai..."):
        with st.chat_message("user"):
            st.markdown(f"**{st.session_state.username}**")
            st.markdown(prompt)

        if "@ai" in prompt.lower():
            with st.chat_message("assistant"):
                with st.spinner("Arknok AI is generating a fix..."):
                    # THIS HOOKS ASMIT'S AI_ENGINE DIRECTLY
                    ai_response = current_room.add_message(st.session_state.username, prompt)
            if ai_response: st.session_state.latest_ai_fix = ai_response["content"]
        else:
            current_room.add_message(st.session_state.username, prompt)
        st.rerun()

with ai_col:
    st.subheader("✨ AI Assistant")
    st.caption("Monitoring session")
    st.write("---")
    st.markdown("**Current Analysis:**")
    st.markdown(st.session_state.latest_ai_fix)
    st.write("---")
    st.button("Apply Fix 🛠️", type="primary", use_container_width=True)
