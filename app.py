import streamlit as st
import time
import os
from dotenv import load_dotenv

# 1. IMPORT ASMIT'S ENGINES
from chat_engine import ChatRoomManager
from auth_engine import AuthManager

load_dotenv()

# ---------------------------------------------------------
# 2. PAGE SETUP & FIGMA-STRICT CSS
# ---------------------------------------------------------
st.set_page_config(page_title="Arknok DevSync", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #0E1116 !important; color: #E6EDF3 !important; }
    
    /* Figma Login Card */
    .login-card {
        background-color: #161B22; padding: 50px; border-radius: 16px;
        border: 1px solid #30363D; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .login-header { font-size: 32px; font-weight: 700; color: #FFFFFF; margin-bottom: 5px; }
    .login-subtitle { color: #8B949E; margin-bottom: 30px; }
    
    /* DevSync Orange Action Buttons */
    div.stButton > button[kind="primary"] {
        background-color: #FF6B00 !important; color: white !important;
        height: 50px !important; font-size: 18px !important; 
        border: none !important; font-weight: bold !important; border-radius: 10px !important;
    }
    div.stButton > button[kind="primary"]:hover { background-color: #E65C00 !important; }

    /* VS Code Style Elements */
    [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363D !important; }
    .stChatInput textarea { font-family: 'Courier New', monospace !important; font-size: 14px !important; background-color: #0D1117 !important; color: #58A6FF !important; }
    [data-testid="column"]:nth-of-type(2) { background-color: #13171C !important; border-left: 1px solid #30363D !important; padding: 20px !important; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. PERSISTENT BACKEND INITIALIZATION
# ---------------------------------------------------------
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
# 4. FIGMA-MATCHED AUTHENTICATION FLOW
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<div class='login-header'>Welcome back</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-subtitle'>Sign in to continue coding</div>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            log_user = st.text_input("Email", placeholder="you@example.com", key="log_user")
            log_pass = st.text_input("Password", type="password", placeholder="Enter password", key="log_pass")
            st.write("")
            if st.button("Sign In →", type="primary", use_container_width=True, key="login_submit"):
                success, msg = st.session_state.auth_manager.login(log_user, log_pass)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = log_user
                    st.rerun()
                else: st.error(msg)
        with tab2:
            reg_user = st.text_input("New Username", placeholder="e.g., SanketMohapatra06", key="reg_user")
            reg_pass = st.text_input("New Password", type="password", placeholder="Minimum 8 characters", key="reg_pass")
            if st.button("Create Account", use_container_width=True, key="signup_submit"):
                success, msg = st.session_state.auth_manager.signup(reg_user, reg_pass)
                if success: st.success("Account created! Switch to Login.")
                else: st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# 5. CORE WORKSPACE & LOGIC
# ---------------------------------------------------------
current_room = st.session_state.manager.get_room(st.session_state.active_room)
current_room.join(st.session_state.username)

@st.fragment(run_every="5s")
def sync_member_status(room):
    st.caption(f"ONLINE — {len([m for m in room.members.values() if m == 'online'])}")
    for user, status in room.members.items():
        st.markdown(f"🟢 **{user}**" if status == "online" else f"⚪ {user}")

with st.sidebar:
    st.subheader("DevSync AI")
    st.write("---")
    with st.expander("➕ Create New Room"):
        new_name = st.text_input("Room Name", placeholder="e.g., React Bug Bash", key="new_room_name")
        new_lang = st.selectbox("Language", ["TypeScript", "Python", "JavaScript", "C++"], key="new_room_lang")
        if st.button("Create Room", type="primary", use_container_width=True, key="sidebar_create"):
            if new_name:
                st.session_state.manager.create_room(new_name, language=new_lang)
                st.session_state.active_room = new_name
                st.rerun()
    st.write("---")
    st.caption("CHANNELS")
    for room_info in st.session_state.manager.list_rooms():
        if st.button(f"# {room_info['name']}", key=f"nav_v2_{room_info['name']}", use_container_width=True):
            st.session_state.active_room = room_info['name']
            st.rerun()
    st.write("---")
    sync_member_status(current_room)
    st.write("---")
    if st.button("🚪 Log Out", use_container_width=True, key="logout_btn"):
        current_room.leave(st.session_state.username)
        st.session_state.authenticated = False
        st.rerun()

chat_col, ai_col = st.columns([2.5, 1.2], gap="large")
with chat_col:
    st.header(f"# {current_room.name}")
    st.caption(f"{current_room.language} • {len(current_room.members)} members")
    st.write("---")
    for msg in current_room.messages:
        role = "assistant" if msg["user"] == "AI_Assistant" else "user"
        with st.chat_message(role):
            st.markdown(f"**{msg['user']}** <span style='color:gray; font-size:12px;'>{msg['timestamp']}</span>", unsafe_allow_html=True)
            st.markdown(msg["content"])
    if prompt := st.chat_input("Paste code or type @ai to debug..."):
        with st.chat_message("user"):
            st.markdown(f"**{st.session_state.username}**")
            st.markdown(prompt)
        if "@ai" in prompt.lower():
            with st.chat_message("assistant"):
                with st.spinner("Arknok AI analyzing..."):
                    ai_response = current_room.add_message(st.session_state.username, prompt)
            if ai_response: st.session_state.latest_ai_fix = ai_response["content"]
        else: current_room.add_message(st.session_state.username, prompt)
        st.rerun()

with ai_col:
    st.subheader("✨ AI Assistant")
    st.write("---")
    with st.container(border=True):
        st.markdown("**Current Analysis:**")
        st.markdown(st.session_state.latest_ai_fix)
        st.write("---")
        if st.button("Apply Fix 🛠️", type="primary", use_container_width=True, key="apply_fix"):
            st.success("Code staged to local buffer!")
