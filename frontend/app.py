"""
=============================================================================
FILE: frontend/app.py
PURPOSE: ChatGPT-Style Projects & Sessions UI Dashboard for RAG Study Assistant.
WHAT IT DOES:
  1. Auto-Embeds PDFs upon file selection in 1 single go.
  2. Projects Navigation (Placement, Programming Languages, STQA-Acad).
  3. Project Dashboard Tabs: 'Chats' vs 'Sources'.
  4. Instant Chat Session creation & page-level citation views.
  5. Pins Chat Input box to the bottom of the screen (ChatGPT/Gemini style).
=============================================================================
"""

import streamlit as st
import requests

# Backend API Base URL
API_URL = "http://127.0.0.1:8000/api/v1"

# Page Configuration
st.set_page_config(page_title="ChatGPT Projects - Study RAG", page_icon="📁", layout="wide")

# Custom CSS for ChatGPT-Style Dark Theme & Bottom-Pinned Input Box
st.markdown("""
<style>
    .stApp { background-color: #0d0d0d; color: #ececec; }
    .stSidebar { background-color: #171717; }
    .project-header { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = None
if "active_project_name" not in st.session_state:
    st.session_state.active_project_name = None
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None
if "active_session_name" not in st.session_state:
    st.session_state.active_session_name = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# Helper function to clear chat history when switching sessions
def set_active_session(session_id, session_name):
    st.session_state.active_session_id = session_id
    st.session_state.active_session_name = session_name
    st.session_state.messages = []

# =============================================================================
# SIDEBAR: Projects List & Project Creator
# =============================================================================
with st.sidebar:
    st.title("📁 Projects")
    
    # --- 1. CREATE NEW PROJECT ---
    with st.expander("➕ New Project"):
        new_proj = st.text_input("Project Name", placeholder="e.g. Placement, Physics-101")
        if st.button("Create Project"):
            if new_proj.strip():
                res = requests.post(f"{API_URL}/projects/", json={"name": new_proj})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.active_project_id = data["id"]
                    st.session_state.active_project_name = data["name"]
                    st.session_state.active_session_id = None
                    st.rerun()

    # --- 2. LIST PROJECTS ---
    projects_res = requests.get(f"{API_URL}/projects/")
    projects = projects_res.json() if projects_res.status_code == 200 else []

    if projects:
        st.subheader("Your Projects")
        for proj in projects:
            is_active = (proj["id"] == st.session_state.active_project_id)
            label = f"📁  {proj['name']}" if not is_active else f"📂  {proj['name']} (Active)"
            
            if st.button(label, key=f"proj_{proj['id']}", use_container_width=True):
                st.session_state.active_project_id = proj["id"]
                st.session_state.active_project_name = proj["name"]
                st.session_state.active_session_id = None
                st.session_state.messages = []
                st.rerun()
    else:
        st.info("No projects created yet. Create one above!")

# =============================================================================
# MAIN DASHBOARD: Inside Selected Project
# =============================================================================
if not st.session_state.active_project_id:
    st.markdown("<h1 class='project-header'>📁 Projects</h1>", unsafe_allow_html=True)
    st.info("👈 Please create or select a Project from the left sidebar to start!")
else:
    proj_name = st.session_state.active_project_name
    proj_id = st.session_state.active_project_id
    st.markdown(f"<h1 class='project-header'>📁 {proj_name}</h1>", unsafe_allow_html=True)

    tab_chats, tab_sources = st.tabs(["💬 Chats", "📄 Sources"])

    # -------------------------------------------------------------------------
    # TAB 1: CHATS (Sessions & Message History)
    # -------------------------------------------------------------------------
    with tab_chats:
        col_new_chat, col_sess_select = st.columns([1, 2])
        
        with col_new_chat:
            with st.popover(f"➕ New Chat in {proj_name}"):
                sess_name_input = st.text_input("Chat Title", placeholder="e.g. Marsh AI Prep, s1")
                if st.button("Start Chat"):
                    if sess_name_input.strip():
                        res = requests.post(
                            f"{API_URL}/projects/{proj_id}/sessions",
                            json={"name": sess_name_input}
                        )
                        if res.status_code == 200:
                            s_data = res.json()
                            set_active_session(s_data["id"], s_data["name"])
                            st.rerun()

        sess_res = requests.get(f"{API_URL}/projects/{proj_id}/sessions")
        sessions = sess_res.json() if sess_res.status_code == 200 else []

        with col_sess_select:
            if sessions:
                sess_dict = {s["name"]: s["id"] for s in sessions}
                selected_s_name = st.selectbox(
                    "Active Chat Session",
                    options=list(sess_dict.keys()),
                    label_visibility="collapsed"
                )
                if selected_s_name and (st.session_state.active_session_name != selected_s_name):
                    set_active_session(sess_dict[selected_s_name], selected_s_name)

        st.divider()

        if not st.session_state.active_session_id:
            st.info(f"Click **'➕ New Chat in {proj_name}'** above to start a conversation thread!")
        else:
            st.caption(f"Active Session: **{st.session_state.active_session_name}**")
            
            # Display Chat History Container
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        if "sources" in msg and msg["sources"]:
                            with st.expander("📌 View Page Citations"):
                                for src in msg["sources"]:
                                    st.write(f"📄 **{src['filename']}** (Page {src['page']})")
                                    st.caption(f"Snippet: \"{src['text_snippet']}...\"")

    # -------------------------------------------------------------------------
    # TAB 2: SOURCES (PDF Uploader & Auto-Embedding)
    # -------------------------------------------------------------------------
    with tab_sources:
        st.subheader(f"📄 Project Sources ({proj_name})")
        uploaded_file = st.file_uploader("➕ Add sources (Upload PDF)", type=["pdf"], key="pdf_auto_uploader")
        
        if uploaded_file is not None:
            file_key = f"{proj_id}_{uploaded_file.name}_{uploaded_file.size}"
            if file_key not in st.session_state.processed_files:
                with st.spinner(f"Auto-chunking & embedding '{uploaded_file.name}' into Pinecone..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    upload_res = requests.post(f"{API_URL}/projects/{proj_id}/documents", files=files)
                    
                    if upload_res.status_code == 200:
                        doc_data = upload_res.json()
                        st.session_state.processed_files.add(file_key)
                        st.success(f"✅ Successfully embedded '{doc_data['filename']}' ({doc_data['total_chunks']} chunks in Pinecone)!")
                        st.rerun()
                    else:
                        st.error("Failed to process and embed PDF.")

    # -------------------------------------------------------------------------
    # ROOT CHAT INPUT: DOCKED TO BOTTOM (ChatGPT / Gemini Style)
    # -------------------------------------------------------------------------
    if st.session_state.active_session_id:
        if user_query := st.chat_input(f"Message in {proj_name}..."):
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            # Trigger immediate UI refresh to show user question and fetch response
            chat_res = requests.post(
                f"{API_URL}/sessions/{st.session_state.active_session_id}/chat",
                json={"question": user_query}
            )
            
            if chat_res.status_code == 200:
                data = chat_res.json()
                ans = data["answer"]
                srcs = data["sources"]
                st.session_state.messages.append({"role": "assistant", "content": ans, "sources": srcs})
                st.rerun()
            else:
                st.error("Error generating answer from backend API.")
