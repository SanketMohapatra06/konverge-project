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
# 2. GLOBAL PERSISTENCE (Shared engine for all users)
# ---------------------------------------------------------
@st.cache_resource
def get_global_engines():
    auth = AuthManager()
    manager = ChatRoomManager()
    manager.create_room("React Hooks Deep Dive", language="TypeScript")
    manager.create_room("Python ML Pipeline", language="Python")
    return auth, manager

auth_engine, chat_engine = get_global_engines()

# ---------------------------------------------------------
# 3. MASTER STYLESHEET (Fixed Ghost Box)
# ---------------------------------------------------------
st.set_page_config(page_title="Arknok DevSync", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0E1116 !important; color: #E6EDF3 !important; font-family: 'Inter', sans-serif; }
    
    /* GHOST BOX KILLER: Target the native container directly */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 16px !important;
        padding: 40px !important;
    }

    [data-testid="stSidebar"] { background-color: #0D0D0D !important; border-right: 1px solid #1F1F1F !important; }
    .stChatInput textarea { font-family: 'Courier New', monospace !important; background-color: #0D1117 !important; color: #58A6FF !important; }
    [data-testid="column"]:nth-of-type(2) { background-color: #161412 !important; border-left: 1px solid #302A24 !important; padding: 24px !important; border-radius: 12px; }
    .ai-fix-card { background-color: #1C1917; border: 1px solid #44372B; border-radius: 12px; padding: 15px; margin-top: 10px; }
    
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B00 0%, #E65C00 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        height: 48px !important; border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. AUTHENTICATION (Figma-Strict & Box-Free)
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        # Use native container with border to kill the ghost box
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Welcome back</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #8B949E; margin-bottom: 25px;'>Sign in to continue coding</p>", unsafe_allow_html=True)
            
            t1, t2 = st.tabs(["Login", "Sign Up"])
            with t1:
                u = st.text_input("Username", key="l_u", placeholder="")
                p = st.text_input("Password", type="password", key="l_p", placeholder="")
                if st.button("Sign In →", type="primary", use_container_width=True):
                    success, _ = auth_engine.login(u, p)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = u
                        st.rerun()
                    else: st.error("Invalid credentials")
            with t2:
                nu = st.text_input("New Username", key="r_u")
                np = st.text_input("New Password", type="password", key="r_p")
                if st.button("Create Account", use_container_width=True):
                    auth_engine.signup(nu, np)
                    st.success("Account created!")
    st.stop()

# ---------------------------------------------------------
# 5. WORKSPACE (Active Content)
# ---------------------------------------------------------
if 'active_room' not in st.session_state:
    st.session_state.active_room = "React Hooks Deep Dive"

current_room = chat_engine.get_room(st.session_state.active_room)
current_room.join(st.session_state.username)

@st.fragment(run_every="5s")
def sync_status(room):
    st.caption(f"ONLINE — {len([m for m in room.members.values() if m == 'online'])}")
    for u, s in room.members.items():
        color = "#23A559" if s == "online" else "#80848E"
        st.markdown(f"<span style='color:{color}'>●</span> **{u}**", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("DevSync AI")
    with st.expander("➕ Create New Room"):
        n = st.text_input("Room Name", key="sn")
        l = st.selectbox("Language", ["TypeScript", "Python", "JavaScript", "C++"], key="sl")
        if st.button("Create", type="primary", use_container_width=True):
            chat_engine.create_room(n, language=l)
            st.session_state.active_room = n
            st.rerun()
    st.write("---")
    for r in chat_engine.list_rooms():
        if st.button(f"#{r['name']}", key=f"nav_{r['name']}", use_container_width=True):
            st.session_state.active_room = r['name']
            st.rerun()
    st.write("---")
    sync_status(current_room)

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
            current_room.add_message(st.session_state.username, prompt)
            st.rerun()
    with e_tab:
        raw_code = st_ace(language=current_room.language.lower(), theme="monokai", height=400, key=f"ace_{current_room.name}")
        if st.button("Send to Arknok AI 🚀", use_container_width=True):
            if raw_code:
                current_room.add_message(st.session_state.username, f"@ai Fix this code:\n\n```{raw_code}```")
                st.rerun()

with ai_col:
    st.markdown("<div class='ai-header'>✨ Arknok AI</div>", unsafe_allow_html=True)
    ai_history = [m for m in current_room.messages if m["user"] == "AI_Assistant"]
    insight = ai_history[-1]["content"] if ai_history else "No bugs detected yet."
    st.markdown(f"<div class='ai-fix-card'>{insight}</div>", unsafe_allow_html=True)
    st.write("---")
    if st.button("Apply Fix 🛠️", type="primary", use_container_width=True):
        st.success("Correction applied!")
