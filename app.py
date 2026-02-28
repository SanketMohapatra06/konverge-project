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

# Ensure the logged-in user is actually 'online' in the current room
if st.session_state.authenticated:
    current_room.join(st.session_state.username)

# --- THE SIDEBAR FIX ---
@st.fragment(run_every="5s")
def sync_member_status(room):
    """Refreshes ONLY the status dots without crashing Streamlit."""
    st.caption(f"ONLINE — {len([m for m in room.members.values() if m == 'online'])}")
    for user, status in room.members.items():
        if status == "online":
            st.markdown(f"🟢 **{user}**")
        else:
            st.markdown(f"⚪ {user}")

with st.sidebar:
    st.subheader("DevSync AI")
    st.write("---")
    
    # 1. THE CREATE ROOM "MODAL"
    with st.expander("➕ Create New Room"):
        new_name = st.text_input("Room Name", placeholder="e.g., React Bug Bash")
        new_lang = st.selectbox("Language", ["TypeScript", "Python", "JavaScript", "C++", "Go"])
        
        if st.button("Create Room", type="primary", use_container_width=True):
            if new_name:
                # Calls Asmit's manager to add the room to the 'database'
                st.session_state.manager.create_room(new_name, language=new_lang)
                st.session_state.active_room = new_name
                st.success(f"Room {new_name} created!")
                st.rerun()

    st.write("---")
    st.caption("CHANNELS")
    # Dynamically lists all rooms, including the ones you just created
    for room_info in st.session_state.manager.list_rooms():
        if st.button(f"# {room_info['name']}", key=f"nav_{room_info['name']}", use_container_width=True):
            st.session_state.active_room = room_info['name']
            st.rerun()
            
    st.write("---")
    # CALL THE FRAGMENT HERE
    sync_member_status(current_room)
    
    st.write("---")
    if st.button("🚪 Log Out", use_container_width=True):
        current_room.leave(st.session_state.username)
        st.session_state.authenticated = False
        st.rerun()
    
    st.caption("CHANNELS")
    for room_info in st.session_state.manager.list_rooms():
        # Clean ghost buttons for rooms
        if st.button(f"# {room_info['name']}", key=f"nav_{room_info['name']}", use_container_width=True):
            st.session_state.active_room = room_info['name']
            st.rerun()
            
    st.write("---")
    
    # 1. CALL THE FRAGMENT HERE (Fixed the StreamlitAPIException)
    sync_member_status(current_room)
    
    st.write("---")
    # 2. LOGOUT BUTTON
    if st.button("🚪 Log Out", use_container_width=True):
        current_room.leave(st.session_state.username)
        st.session_state.authenticated = False
        st.rerun()

# --- MAIN WORKSPACE LAYOUT ---
chat_col, ai_col = st.columns([2.5, 1.2], gap="large")

with chat_col:
    st.header(f"# {current_room.name}")
    st.caption(f"{current_room.language} • {len(current_room.members)} members")
    st.write("---")

    # Scrollable Chat Stream
    for msg in current_room.messages:
        role = "assistant" if msg["user"] == "AI_Assistant" else "user"
        with st.chat_message(role):
            st.markdown(f"**{msg['user']}** <span style='color:gray; font-size:12px;'>{msg['timestamp']}</span>", unsafe_allow_html=True)
            st.markdown(msg["content"])

    # VS CODE STYLE INPUT & SHADOW TYPING
    if prompt := st.chat_input("Paste code or type @ai to debug..."):
        # Immediate display
        with st.chat_message("user"):
            st.markdown(f"**{st.session_state.username}**")
            st.markdown(prompt)

        if "@ai" in prompt.lower():
            with st.chat_message("assistant"):
                # Simulated typing/shadow typing
                with st.spinner("Arknok AI is analyzing context..."):
                    ai_response = current_room.add_message(st.session_state.username, prompt)
            
            # Update Right Panel with AI Fix
            if ai_response: 
                st.session_state.latest_ai_fix = ai_response["content"]
        else:
            current_room.add_message(st.session_state.username, prompt)
        st.rerun()

with ai_col:
    # THE HERO PANEL
    st.subheader("✨ AI Assistant")
    st.caption("Monitoring # " + current_room.name)
    st.write("---")
    
    with st.container(border=True):
        st.markdown("**Current Analysis:**")
        # Renders the fix from Asmit's engine in a code block
        st.markdown(st.session_state.latest_ai_fix)
        
        st.write("---")
        # THE DEVSYNC ORANGE BUTTON
        if st.button("Apply Fix 🛠️", type="primary", use_container_width=True):
            st.success("Code correction applied to local buffer!")
