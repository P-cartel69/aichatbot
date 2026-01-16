import streamlit as st
import requests
import uuid
from datetime import datetime

# ================== PAGE CONFIG ==================

st.set_page_config(
    page_title="Falana AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = "http://localhost:8000"

# ================== GLOBAL STYLES ==================

st.markdown("""
<style>

/* ===== Base ===== */
html, body, [class*="css"] {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Inter', sans-serif;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}

/* ===== Headings ===== */
h1, h2, h3 {
    color: #020617;
}

/* ===== Buttons ===== */
.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.55rem 1rem;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #1e40af;
}

/* ===== Chat Bubbles ===== */
[data-testid="stChatMessage"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.7rem;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06);
}

/* ===== User Message ===== */
[data-testid="stChatMessage"]:has(svg[aria-label="user"]) {
    background: #eff6ff;
}

/* ===== Assistant Message ===== */
[data-testid="stChatMessage"]:has(svg[aria-label="assistant"]) {
    background: #ffffff;
}

/* ===== Input Box ===== */
textarea {
    border-radius: 14px !important;
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    color: #020617 !important;
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #cbd5f5;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ================== HELPERS ==================

def new_thread_id():
    return f"thread-{uuid.uuid4().hex[:8]}"

def now():
    return datetime.now().strftime("%H:%M")

def get_threads():
    try:
        r = requests.get(f"{BASE_URL}/chat/threads", timeout=5)
        r.raise_for_status()
        return r.json()
    except:
        return []

def get_history(thread_id):
    try:
        r = requests.get(f"{BASE_URL}/chat/history/{thread_id}", timeout=5)
        r.raise_for_status()
        return r.json()["message"]
    except:
        return []

def send_message(thread_id, message):
    r = requests.post(
        f"{BASE_URL}/chat/{thread_id}",
        params={"message": message},
        timeout=20
    )
    r.raise_for_status()
    return r.json()["message"]

# ================== SESSION STATE ==================

if "current_thread" not in st.session_state:
    st.session_state.current_thread = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "busy" not in st.session_state:
    st.session_state.busy = False

# ================== SIDEBAR ==================

with st.sidebar:
    st.markdown("## 🤖 Falana AI")
    st.caption("Clean • Intelligent • Secure")

    st.markdown("### 🧵 Conversations")

    threads = get_threads()

    if not threads:
        st.info("No conversations yet")

    for t in threads:
        active = t == st.session_state.current_thread
        label = f"▶ {t}" if active else t

        if st.button(label, key=t, use_container_width=True):
            st.session_state.current_thread = t
            st.session_state.messages = get_history(t)
            st.rerun()

    st.divider()

    if st.button("➕ New Conversation", use_container_width=True):
        tid = new_thread_id()
        st.session_state.current_thread = tid
        st.session_state.messages = []
        st.rerun()

# ================== MAIN ==================

st.markdown("# Falana AI")
st.caption("Ask. Reason. Build.")

if not st.session_state.current_thread:
    st.info("Select or create a conversation to begin.")
    st.stop()

st.markdown(f"**Thread ID:** `{st.session_state.current_thread}`")

# ================== CHAT ==================

if not st.session_state.messages:
    st.markdown("""
    <div style="opacity:0.6; padding:2rem;">
        Start typing to begin a meaningful conversation.
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg.get("type")
    content = msg.get("content")

    if role == "human":
        with st.chat_message("user"):
            st.markdown(content)
            st.caption(now())

    elif role == "ai":
        with st.chat_message("assistant"):
            st.markdown(content)
            st.caption(now())

# ================== INPUT ==================

prompt = st.chat_input("Message Falana AI...")

if prompt and not st.session_state.busy:
    st.session_state.busy = True

    st.session_state.messages.append({
        "type": "human",
        "content": prompt
    })

    with st.spinner("Falana AI is thinking..."):
        try:
            st.session_state.messages = send_message(
                st.session_state.current_thread,
                prompt
            )
        except:
            st.error("Backend not responding")

    st.session_state.busy = False
    st.rerun()
