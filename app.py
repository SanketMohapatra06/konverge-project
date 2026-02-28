import streamlit as st
import os
from dotenv import load_dotenv

# Import Asmit's Backend Engine
from chat_engine import ChatRoomManager

load_dotenv()

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="DevSync AI", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# 2. DEVSYNC CUSTOM UI STYLING
st.markdown("""
    <style>
    .stApp { background-color: #0D1117; color: #E6EDF3; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363d; }
    
    /* Room Buttons (Orange Hover) */
    .stButton>button {
        width: 100%; border-radius: 8px; border: 1px solid #30363d;
        background-color: #21262d; color: #E6EDF3; transition: 0.3s; text-align: left;
    }
    .stButton>button:hover { border-color: #FF6B00; color: #FF6B00; }
    
    /* Primary Action Buttons (DevSync Orange) */
    div.stButton > button:first-child[kind="primary"] {
        background-color: #FF6B00; border: none; color: white; font-weight: bold;
    }

    /* AI Panel Container */
    .ai-container { background-color: #161B22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; }
    </style>
""", unsafe_allow_html=True)

# 3. INITIALIZE BACKEND IN SESSION STATE
if 'manager' not in st.session_state:
    # Boot up Asmit's manager
    manager = ChatRoomManager()
    # Seed some default rooms
    manager.create_room("React Hooks Deep Dive", language="TypeScript")
    manager.create_room("Python ML Pipeline", language="Python")
    manager.create_room("Node.js API Design", language="JavaScript")
    
    # Add fake users so the rooms aren't empty
    manager.get_room("React Hooks Deep Dive").join("Sanket")
    manager.get_room("React Hooks Deep Dive").join("Aditi")
    
    st.session_state.manager = manager
    st.session_state.active_room = "React Hooks Deep Dive"
    st.session_state.username = "Sanket"

# Holds the data for the right-hand AI Panel
if 'ai_display' not in st.session_state:
    st.session_state.ai_display = "No code analyzed yet. Tag @ai in the chat to start."

# Get the current room object
current_room = st.session_state.manager.get_room(st.session_state.active_room)

# ---------------------------------------------------------
# PANEL 1: SIDEBAR (Navigation)
# ---------------------------------------------------------
with st.sidebar:
    st.title("🚀 DevSync AI")
    st.caption("Collaborative Coding Hub")
    st.write("---")
    
    st.subheader("My Rooms")
    # Dynamically list rooms from Asmit's manager
    for room_info in st.session_state.manager.list_rooms():
        # If clicked, change the active room
        if st.button(f"#{room_info['name']}"):
            st.session_state.active_room = room_info['name']
            st.rerun()

    st.write("---")
    
    # Fake Create Room Modal (Expander)
    with st.expander("+ Create New Room"):
        new_room_name = st.text_input("Room Name")
        new_room_lang = st.selectbox("Language", ["Python", "JavaScript", "TypeScript", "Auto"])
        if st.button("Create", type="primary"):
            if new_room_name:
                st.session_state.manager.create_room(new_room_name, language=new_room_lang)
                st.session_state.active_room = new_room_name
                st.rerun()

# ---------------------------------------------------------
# PANEL 2 & 3: MAIN WORKSPACE
# ---------------------------------------------------------
chat_col, ai_col = st.columns([2.2, 1], gap="large")

# --- PANEL 2: CENTRAL CHAT ---
with chat_col:
    # Room Header
    st.header(f"# {current_room.name}")
    st.caption(f"{current_room.language} • {len(current_room.members)} members online")
    st.write("---")

    # Render Chat History directly from Asmit's ChatRoom object
    for msg in current_room.messages:
        # Check if the message is from the AI to change the avatar
        is_ai = msg["user"] == "AI_Assistant"
        with st.chat_message("assistant" if is_ai else "user"):
            st.write(f"**{msg['user']}** `{msg['timestamp']}`")
            st.markdown(msg["content"])

    # Chat Input Box
    if prompt := st.chat_input(f"Message #{current_room.name} or use @ai to debug..."):
        # Asmit's logic: add_message returns a value IF @ai is tagged
        ai_response = current_room.add_message(st.session_state.username, prompt)
        
        # If Asmit's backend caught an @ai tag and processed it
        if ai_response:
            # Update the right-hand panel with the raw AI output
            st.session_state.ai_display = ai_response["content"]
            
        st.rerun()

# --- PANEL 3: RIGHT AI ASSISTANT PANEL ---
with ai_col:
    st.subheader("✨ AI Assistant")
    st.caption("Powered by Groq LLM")
    
    with st.container(border=True):
        st.markdown("**Current Analysis:**")
        
        # Display the AI output generated from Asmit's backend
        st.markdown(st.session_state.ai_display)
        
        st.write("---")
        # Action Buttons
        st.button("Apply Fix 🛠️", type="primary")
        
        # Extra feature: Manually trigger Asmit's modes without chatting
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Explain 📖"):
                # Grab the last message to explain
                if current_room.messages:
                    last_msg = current_room.messages[-1]["content"]
                    exp_resp = current_room.trigger_ai(last_msg, mode="explain")
                    st.session_state.ai_display = exp_resp
                    st.rerun()
        with col_b:
            if st.button("Optimize ⚡"):
                if current_room.messages:
                    last_msg = current_room.messages[-1]["content"]
                    opt_resp = current_room.trigger_ai(last_msg, mode="optimize")
                    st.session_state.ai_display = opt_resp
                    st.rerun()