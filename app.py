import streamlit as st
import time
from chat_engine import ChatRoomManager
from auth_engine import AuthManager

# IMPORT ASMIT'S BACKEND ENGINE
from chat_engine import ChatRoomManager

# ---------------------------------------------------------
# 1. PAGE SETUP & DEVSYNC CSS
# ---------------------------------------------------------
st.set_page_config(page_title="DevSync AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp { background-color: #0E1116 !important; color: #E6EDF3 !important; }
    
    /* Login Card */
    .login-container { max-width: 400px; margin: 10vh auto; padding: 40px; background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; }
    
    /* Sidebar Stealth Mode */
    [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363D !important; }
    
    /* VS Code Style Chat Input */
    .stChatInput textarea { font-family: 'Courier New', monospace !important; font-size: 14px !important; background-color: #0D1117 !important; color: #58A6FF !important; }
    
    /* DevSync Orange Action Buttons */
    div.stButton > button[kind="primary"] { background-color: #FF6B00 !important; color: white !important; border: none !important; font-weight: bold !important; border-radius: 8px !important; }
    div.stButton > button[kind="primary"]:hover { background-color: #E65C00 !important; }
    
    /* Right AI Panel Container */
    [data-testid="column"]:nth-of-type(2) { background-color: #13171C !important; border-left: 1px solid #30363D !important; padding: 20px !important; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. FUNCTIONAL AUTHENTICATION (Integrated with AuthManager)
# ---------------------------------------------------------
# Initialize AuthManager in session state so it remembers users
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.header("🚀 DevSync AI")
        st.caption("Sign in to continue coding")
        
        # Create Tabs for Login and Sign Up
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
                    st.error(msg) # Shows red error box for wrong password
                    
        with tab2:
            reg_user = st.text_input("New Username", key="reg_user")
            reg_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Create Account", use_container_width=True):
                success, msg = st.session_state.auth_manager.signup(reg_user, reg_pass)
                if success:
                    st.success("Account created! You can now log in.")
                else:
                    st.error(msg)
                    
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Halts the script here if not logged in

# ---------------------------------------------------------
# 3. INITIALIZE ASMIT'S BACKEND
# ---------------------------------------------------------
if 'manager' not in st.session_state:
    # This boots up Asmit's backend ONCE when the app starts
    st.session_state.manager = ChatRoomManager()
    st.session_state.manager.create_room("React Hooks Deep Dive", language="TypeScript")
    st.session_state.manager.create_room("Python ML Pipeline", language="Python")
    st.session_state.manager.create_room("Backend API", language="Node.js")
    
    st.session_state.active_room = "React Hooks Deep Dive"
    st.session_state.latest_ai_fix = "No bugs detected yet. Paste code and tag @ai to begin."

# Get the current room object and make sure the user is in it
current_room = st.session_state.manager.get_room(st.session_state.active_room)
if st.session_state.username not in current_room.members:
    current_room.join(st.session_state.username)

# ---------------------------------------------------------
# 4. DYNAMIC SIDEBAR (Fragment for Real-Time Status)
# ---------------------------------------------------------
@st.fragment(run_every="5s")
def render_sidebar():
    with st.sidebar:
        st.subheader("DevSync AI")
        st.write("---")
        
        st.caption("CHANNELS")
        for room_info in st.session_state.manager.list_rooms():
            # Standard buttons acting as navigation links
            if st.button(f"# {room_info['name']}", key=f"nav_{room_info['name']}"):
                st.session_state.active_room = room_info['name']
                st.rerun()
                
        st.write("---")
        st.caption(f"ONLINE — {len(current_room.members)}")
        
        # Reads Asmit's member dictionary dynamically
        for user, status in current_room.members.items():
            if status == "online":
                st.markdown(f"🟢 **{user}**")
            else:
                st.markdown(f"⚪ {user}")

render_sidebar()

# ---------------------------------------------------------
# 5. MAIN WORKSPACE (Chat & AI Panel)
# ---------------------------------------------------------
chat_col, ai_col = st.columns([2.5, 1.2], gap="large")

with chat_col:
    st.header(f"# {current_room.name}")
    st.write("---")

    # Render history from Asmit's ChatRoom object
    for msg in current_room.messages:
        role = "assistant" if msg["user"] == "AI_Assistant" else "user"
        with st.chat_message(role):
            st.markdown(f"**{msg['user']}** <span style='color:gray; font-size:12px;'>{msg['timestamp']}</span>", unsafe_allow_html=True)
            st.markdown(msg["content"])

    # VS Code Style Chat Input
    if prompt := st.chat_input("Type a message or paste code. Use @ai to debug..."):
        
        # Immediate UI update for the user's message
        with st.chat_message("user"):
            st.markdown(f"**{st.session_state.username}**")
            st.markdown(prompt)

        if "@ai" in prompt.lower():
            # SIMULATED TYPING EFFECT
            with st.chat_message("assistant"):
                with st.spinner("Arknok AI is analyzing context and writing fix..."):
                    # This calls Asmit's backend -> which calls Groq -> which returns the fix
                    ai_response = current_room.add_message(st.session_state.username, prompt)
            
            # Store the result so the right panel can display it
            if ai_response:
                st.session_state.latest_ai_fix = ai_response["content"]
        else:
            # Standard message without AI trigger
            current_room.add_message(st.session_state.username, prompt)
            
        st.rerun()

with ai_col:
    st.subheader("✨ AI Assistant")
    st.caption("Powered by Groq LLM")
    st.write("---")
    
    # Display the latest fix generated by Asmit's backend
    st.markdown("**Current Analysis:**")
    st.markdown(st.session_state.latest_ai_fix)
    
    st.write("---")
    st.button("Apply Fix 🛠️", type="primary", use_container_width=True)
