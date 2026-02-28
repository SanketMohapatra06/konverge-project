import streamlit as st
import time
import os
from dotenv import load_dotenv

# 1. IMPORT ASMIT'S ENGINES
from chat_engine import ChatRoomManager
from auth_engine import AuthManager

load_dotenv()

# ---------------------------------------------------------
# 2. THE MASTER "ARNOK" STYLESHEET
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 1. Global Background & Typography */
    .stApp { background-color: #0E1116 !important; color: #E6EDF3 !important; font-family: 'Inter', sans-serif; }
    
    /* 2. Sidebar: Stealth & Status */
    [data-testid="stSidebar"] { background-color: #0D0D0D !important; border-right: 1px solid #1F1F1F !important; }
    
    /* 3. Login Card */
    .login-container { max-width: 400px; margin: 10vh auto; padding: 40px; background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; }

    /* 4. Center Chat: VS Code Vibe */
    .user-msg-header { color: #8B949E; font-size: 12px; margin-bottom: 4px; }
    
    /* 5. The "Ask AI" Input Bar */
    .stChatInputContainer { background-color: #161B22 !important; border: 1px solid #30363D !important; border-radius: 12px !important; }
    
    /* 6. Right Panel: Glowing AI Assistant */
    [data-testid="column"]:nth-of-type(2) { background-color: #161412 !important; border-left: 1px solid #302A24 !important; padding: 24px !important; border-radius: 12px; }
    .ai-header { color: #FF6B00; font-weight: 700; font-size: 18px; margin-bottom: 10px; }
    .ai-fix-card { background-color: #1C1917; border: 1px solid #44372B; border-radius: 12px; padding: 15px; }
    
    /* 7. Action Buttons (Orange Gradient) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B00 0%, #E65C00 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        height: 48px !important; border-radius: 8px !important;
    }
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
# 4. FUNCTIONAL AUTHENTICATION FLOW
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.header("Welcome back")
        st.caption("Sign in to start coding")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            # Placeholder removed as requested
            log_user = st.text_input("Username", key="log_user", placeholder="")
            log_pass = st.text_input("Password", type="password", key="log_pass", placeholder="")
            if st.button("Sign In →", type="primary", use_container_width=True):
                success, msg = st.session_state.auth_manager.login(log_user, log_pass)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = log_user
                    st.rerun()
                else: st.error(msg)
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
# 5. THE MAIN WORKSPACE (Integrated Logic)
# ---------------------------------------------------------
current_room = st.session_state.manager.get_room(st.session_state.active_room)
current_room.join(st.session_state.username)

# SIDEBAR: Rooms & Online Status
with st.sidebar:
    st.markdown("### DevSync AI")
    st.caption("Collaborative Coding Hub")
    st.write("---")
    
    st.caption("MY ROOMS")
    for room in st.session_state.manager.list_rooms():
        if st.button(f"#{room['name']}", key=f"nav_{room['name']}", use_container_width=True):
            st.session_state.active_room = room['name']
            st.rerun()
    
    st.write("---")
    st.caption(f"ONLINE — {len(current_room.members)}")
    for user, status in current_room.members.items():
        color = "#23A559" if status == "online" else "#80848E"
        st.markdown(f"<span style='color:{color}'>●</span> **{user}**", unsafe_allow_html=True)

# MAIN LAYOUT: Split 2.5 : 1.2
chat_col, ai_col = st.columns([2.5, 1.2], gap="large")

with chat_col:
    st.markdown(f"### # {current_room.name}")
    st.caption(f"{current_room.language} • {len(current_room.members)} members")
    st.write("---")

    for msg in current_room.messages:
        is_ai = msg["user"] == "AI_Assistant"
        with st.chat_message("assistant" if is_ai else "user"):
            st.markdown(f"<div class='user-msg-header'>{msg['user']} • {msg['timestamp']}</div>", unsafe_allow_html=True)
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type a message... (use @ai to ask Arknok AI)"):
        with st.chat_message("user"):
            st.markdown(prompt)
            
        if "@ai" in prompt.lower():
            with st.chat_message("assistant"):
                with st.spinner("Arknok AI is analyzing context..."):
                    ai_response = current_room.add_message(st.session_state.username, prompt)
            if ai_response: st.session_state.latest_ai_fix = ai_response["content"]
        else:
            current_room.add_message(st.session_state.username, prompt)
        st.rerun()

with ai_col:
    # REBRANDED TO ARKNOK AI
    st.markdown("<div class='ai-header'>✨ Arknok AI</div>", unsafe_allow_html=True)
    st.caption("Monitoring session context")
    
    st.markdown("<div class='ai-fix-card'>", unsafe_allow_html=True)
    st.markdown("**Latest Insight:**")
    st.markdown(st.session_state.latest_ai_fix)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("---")
    # ONLY PRIMARY ACTION REMAINING
    if st.button("Apply Fix 🛠️", type="primary", use_container_width=True):
        st.success("Correction applied to local buffer!")
