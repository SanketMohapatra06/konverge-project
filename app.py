import streamlit as st
import time
import os
from dotenv import load_dotenv
from streamlit_ace import st_ace

# 1. ENGINES INTEGRATION
from chat_engine import ChatRoomManager
from auth_engine import AuthManager

load_dotenv()

# ---------------------------------------------------------
# 2. GLOBAL PERSISTENCE (The "Asmit Fix")
# ---------------------------------------------------------

@st.cache_resource
def get_global_engines():
    """
    This keeps one single instance of the backend alive for ALL users.
    If Asmit signs up, his data is stored here globally.
    """
    auth = AuthManager()
    manager = ChatRoomManager()
    # Seed default rooms globally
    manager.create_room("React Hooks Deep Dive", language="TypeScript")
    manager.create_room("Python ML Pipeline", language="Python")
    return auth, manager

# Initialize global engines
auth_engine, chat_engine = get_global_engines()

# ---------------------------------------------------------
# 3. MASTER STYLESHEET (Clean Fidelity)
# ---------------------------------------------------------
st.set_page_config(page_title="Arknok DevSync", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0E1116 !important; color: #E6EDF3 !important; font-family: 'Inter', sans-serif; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
    
    /* Login Card Fix */
    .login-card {
        background-color: #161B22; padding: 40px; border-radius: 16px;
        border: 1px solid #30363D; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .login-header { font-size: 32px; font-weight: 700; color: #FFFFFF; text-align: center; }
    .login-subtitle { color: #8B949E; text-align: center; margin-bottom: 20px; }
    
    [data-testid="stSidebar"] { background-color: #0D0D0D !important; border-right: 1px solid #1F1F1F !important; }
    .stChatInput textarea { font-family: 'Courier New', monospace !important; background-color: #0D1117 !important; color: #58A6FF !important; }
    [data-testid="column"]:nth-of-type(2) { background-color: #161412 !important; border-left: 1px solid #302A24 !important; padding: 24px !important; border-radius: 12px; }
    .ai-fix-card { background-color: #1C1917; border: 1px solid #44372B; border-radius: 12px; padding: 15px; margin-top: 10px; }
    
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B00 0%, #E65C00 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        height: 48px !important; border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. AUTHENTICATION (Figma-Strict)
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<div class='login-header'>Welcome back</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-subtitle'>Sign in to continue coding</div>", unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["Login", "Sign Up"])
        with t1:
            log_user = st.text_input("Username", key="log_user")
            log_pass = st.text_input("Password", type="password", key="log_pass")
            if st.button("Sign In →", type="primary", use_container_width=True):
                # Uses the GLOBAL engine
                success, msg = auth_engine.login(log_user, log_pass)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = log_user
                    st.rerun()
                else: st.error(msg)
        with t2:
            reg_user = st.text_input("Choose Username", key="reg_user")
            reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
            if st.button("Create Account", use_container_width=True):
                # Stores in the GLOBAL engine
                success, msg = auth_engine.signup(reg_user, reg_pass)
                if success: st.success("Account created! Switch to Login.")
                else: st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# 5. WORKSPACE (Global Sync)
# ---------------------------------------------------------
if 'active_room' not in st.session_state:
    st.session_state.active_room = "React Hooks Deep Dive"

current_room = chat_engine.get_room(st.session_state.active_room)
current_room.join(st.session_state.username)

@st.fragment(run_every="5s")
def sync_member_status(room):
    st.caption(f"ONLINE — {len([m for m in room.members.values() if m == 'online'])}")
    for user, status in room.members.items():
        color = "#23A559" if status == "online" else "#80848E"
        st.markdown(f"<span style='color:{color}'>●</span> **{user}**", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### DevSync AI")
    with st.expander("➕ Create New Room"):
        n_name = st.text_input("Room Name", key="r_input")
        n_lang = st.selectbox("Language", ["TypeScript", "Python", "JavaScript", "C++"], key="l_input")
        if st.button("Create", type="primary", use_container_width=True):
            if n_name:
                chat_engine.create_room(n_name, language=n_lang)
                st.session_state.active_room = n_name
                st.rerun()
    st.write("---")
    for room_info in chat_engine.list_rooms():
        if st.button(f"# {room_info['name']}", key=f"nav_{room_info['name']}", use_container_width=True):
            st.session_state.active_room = room_info['name']
            st.rerun()
    st.write("---")
    sync_member_status(current_room)
    st.write("---")
    if st.button("🚪 Log Out", use_container_width=True):
        current_room.leave(st.session_state.username)
        st.session_state.authenticated = False
        st.rerun()

# LAYOUT
chat_col, ai_col = st.columns([2.5, 1.2], gap="large")

with chat_col:
    st.markdown(f"### # {current_room.name}")
    c_tab, e_tab = st.tabs(["💬 Team Chat", "💻 VS Code Workspace"])

    with c_tab:
        for msg in current_room.messages:
            with st.chat_message("assistant" if msg["user"] == "AI_Assistant" else "user"):
                st.markdown(f"<span style='color:gray; font-size:12px;'>{msg['user']} • {msg['timestamp']}</span>", unsafe_allow_html=True)
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask Arknok AI..."):
            with st.chat_message("user"): st.markdown(prompt)
            current_room.add_message(st.session_state.username, prompt)
            st.rerun()

    with e_tab:
        raw_code = st_ace(language=current_room.language.lower(), theme="monokai", height=400, key=f"ace_{current_room.name}")
        if st.button("Send to Arknok AI 🚀", use_container_width=True):
            if raw_code:
                current_room.add_message(st.session_state.username, f"@ai Fix this code:\n\n```{raw_code}```")
                st.toast("✨ Arknok AI insight generated!")
                st.rerun()

with ai_col:
    st.markdown("<div style='color: #FF6B00; font-weight: 700; font-size: 18px;'>✨ Arknok AI</div>", unsafe_allow_html=True)
    st.caption("Monitoring session context")
    
    ai_history = [m for m in current_room.messages if m["user"] == "AI_Assistant"]
    current_insight = ai_history[-1]["content"] if ai_history else "No bugs detected yet. Use @ai to begin."
    
    st.markdown(f"<div class='ai-fix-card'>{current_insight}</div>", unsafe_allow_html=True)
    st.write("---")
    if st.button("Apply Fix 🛠️", type="primary", use_container_width=True):
        st.success("Correction staged!")
