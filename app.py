import streamlit as st
import time
import os
from dotenv import load_dotenv
from streamlit_ace import st_ace  # The Monaco-based editor component

# 1. IMPORT ASMIT'S ENGINES
from chat_engine import ChatRoomManager
from auth_engine import AuthManager

load_dotenv()

# ---------------------------------------------------------
# 2. THE MASTER "ARNOK" STYLESHEET
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #0E1116 !important; color: #E6EDF3 !important; font-family: 'Inter', sans-serif; }
    
    /* Login Card Styles */
    .login-container { max-width: 400px; margin: 10vh auto; padding: 40px; background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; }

    /* Sidebar: Stealth & Status */
    [data-testid="stSidebar"] { background-color: #0D0D0D !important; border-right: 1px solid #1F1F1F !important; }
    
    /* VS Code Style Chat Input */
    .stChatInput textarea { font-family: 'Courier New', monospace !important; font-size: 14px !important; background-color: #0D1117 !important; color: #58A6FF !important; }
    
    /* Right Panel: Glowing AI Assistant */
    [data-testid="column"]:nth-of-type(2) { background-color: #161412 !important; border-left: 1px solid #302A24 !important; padding: 24px !important; border-radius: 12px; }
    .ai-header { color: #FF6B00; font-weight: 700; font-size: 18px; margin-bottom: 10px; }
    .ai-fix-card { background-color: #1C1917; border: 1px solid #44372B; border-radius: 12px; padding: 15px; }
    
    /* Action Buttons (Orange Gradient) */
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
            log_user = st.text_input("Username", key="log_user", placeholder="") # Placeholder removed
            log_pass = st.text_input("Password", type="password", key="log_pass", placeholder="")
            if st.button("Sign In →", type="primary", use_container_width=True, key="login_btn"):
                success, msg = st.session_state.auth_manager.login(log_user, log_pass)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = log_user
                    st.rerun()
                else: st.error(msg)
        with tab2:
            reg_user = st.text_input("New Username", key="reg_user")
            reg_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Create Account", use_container_width=True, key="signup_btn"):
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

@st.fragment(run_every="5s")
def sync_member_status(room):
    """Refreshes status dots in the sidebar"""
    st.caption(f"ONLINE — {len([m for m in room.members.values() if m == 'online'])}")
    for user, status in room.members.items():
        color = "#23A559" if status == "online" else "#80848E"
        st.markdown(f"<span style='color:{color}'>●</span> **{user}**", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### DevSync AI")
    st.caption("Collaborative Coding Hub")
    st.write("---")
    
    with st.expander("➕ Create New Room"):
        new_name = st.text_input("Room Name", placeholder="e.g., Bug Hunt", key="sidebar_new_room")
        new_lang = st.selectbox("Language", ["TypeScript", "Python", "JavaScript", "C++", "Go"], key="sidebar_lang")
        if st.button("Create Room", type="primary", use_container_width=True, key="create_btn"):
            if new_name:
                st.session_state.manager.create_room(new_name, language=new_lang)
                st.session_state.active_room = new_name
                st.rerun()

    st.write("---")
    st.caption("MY ROOMS")
    for room in st.session_state.manager.list_rooms():
        if st.button(f"#{room['name']}", key=f"nav_{room['name']}", use_container_width=True):
            st.session_state.active_room = room['name']
            st.rerun()
    
    st.write("---")
    sync_member_status(current_room)
    
    st.write("---")
    if st.button("🚪 Log Out", use_container_width=True, key="logout_btn"):
        current_room.leave(st.session_state.username)
        st.session_state.authenticated = False
        st.rerun()

# Workspace Layout: 2.5 : 1.2
chat_col, ai_col = st.columns([2.5, 1.2], gap="large")

with chat_col:
    st.markdown(f"### # {current_room.name}")
    st.caption(f"{current_room.language} • {len(current_room.members)} members")
    st.write("---")

    # THE VS CODE WORKSPACE TABS
    chat_tab, editor_tab = st.tabs(["💬 Team Chat", "💻 VS Code Workspace"])

    with chat_tab:
        for msg in current_room.messages:
            is_ai = msg["user"] == "AI_Assistant"
            with st.chat_message("assistant" if is_ai else "user"):
                st.markdown(f"<span style='color:gray; font-size:12px;'>{msg['user']} • {msg['timestamp']}</span>", unsafe_allow_html=True)
                st.markdown(msg["content"])

        if prompt := st.chat_input("Type a message or use @ai to debug..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            if "@ai" in prompt.lower():
                with st.chat_message("assistant"):
                    with st.spinner("Arknok AI is analyzing..."):
                        ai_response = current_room.add_message(st.session_state.username, prompt)
                if ai_response: st.session_state.latest_ai_fix = ai_response["content"]
            else:
                current_room.add_message(st.session_state.username, prompt)
            st.rerun()

    with editor_tab:
        # THE EMBEDDED CODE EDITOR
        st.caption(f"Syncing with #{current_room.name} context...")
        lang_map = {"TypeScript": "typescript", "Python": "python", "JavaScript": "javascript", "C++": "c_cpp", "Go": "golang", "Node.js": "javascript"}
        
        # ACE Editor Instance
        raw_code = st_ace(
            language=lang_map.get(current_room.language, "python"),
            theme="monokai",
            keybinding="vscode",
            font_size=14,
            height=400,
            key=f"editor_v1_{current_room.name}"
        )
        
        if st.button("Send Code to Arknok AI 🚀", use_container_width=True, key="send_to_ai_btn"):
            if raw_code:
                hidden_p = f"@ai Analyze and fix this {current_room.language} code:\n\n```{raw_code}```"
                with st.spinner("Arknok AI is reviewing editor content..."):
                    ai_response = current_room.add_message(st.session_state.username, hidden_p)
                if ai_response: 
                    st.session_state.latest_ai_fix = ai_response["content"]
                st.success("Code sent! Check the Arknok AI panel.")
            else: st.warning("Editor is empty!")

with ai_col:
    # REBRANDED TO ARKNOK AI
    st.markdown("<div class='ai-header'>✨ Arknok AI</div>", unsafe_allow_html=True)
    st.caption("Monitoring session context")
    
    st.markdown("<div class='ai-fix-card'>", unsafe_allow_html=True)
    st.markdown("**Latest Insight:**")
    st.markdown(st.session_state.latest_ai_fix)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("---")
    if st.button("Apply Fix 🛠️", type="primary", use_container_width=True, key="apply_fix_btn"):
        st.success("Correction applied to local buffer!")
