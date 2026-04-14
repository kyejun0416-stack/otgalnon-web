import streamlit as st
import sqlite3
from datetime import datetime
import os
import google.generativeai as genai

# ==========================================
# 0. ENGINE CONFIGURATION (PRO MODEL)
# ==========================================
os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_brain_engine():
    # 고성능 추론 모델인 1.5 Pro를 호출합니다.
    return genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction=(
            "당신은 OTGALNON 프로젝트의 핵심 지능인 'Hyper-Analyst'입니다. "
            "단순한 정보 나열을 거부하고, 다각적인 분석과 논리적 추론을 통해 답변하십시오. "
            "이모티콘 사용을 금하며, 전문 용어를 정확하게 구사하는 고도의 지적인 톤을 유지하십시오. "
            "답변 전 반드시 내부적으로 문제의 구조를 먼저 분석하십시오."
        )
    )

# ==========================================
# 1. ADVANCED UI & THEME (NO EMOJIS)
# ==========================================
st.set_page_config(page_title="OTGALNON - Hyper Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background: #0b091a; color: #d1d1d1; font-family: 'Pretendard', sans-serif; }
    [data-testid="stSidebar"] { background-color: #121026; border-right: 1px solid #4b3d8f; }
    .stChatMessage { background-color: rgba(75, 61, 143, 0.1) !important; border: 1px solid #4b3d8f; border-radius: 8px; }
    .stCodeBlock { border: 1px solid #4b3d8f !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIC & STORAGE (STABLE VERSION)
# ==========================================
class MemoryEngine:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS chat_log 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp DATETIME)''')

    def record(self, session_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                         (session_id, role, content, datetime.now()))

    def recall(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

# ==========================================
# 3. CORE EXECUTION
# ==========================================
memory = MemoryEngine()
if "session_id" not in st.session_state:
    st.session_state.session_id = f"ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M')}"
if "messages" not in st.session_state:
    st.session_state.messages = memory.recall(st.session_state.session_id)

with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_column_width=True)
    st.markdown("<h2 style='text-align: center;'>OTGALNON</h2>", unsafe_allow_html=True)
    st.divider()
    st.write(f"SESSION ID: `{st.session_state.session_id}`")
    if st.button("RESET WORKSPACE"):
        st.session_state.session_id = f"ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M')}"
        st.session_state.messages = []
        st.rerun()

st.markdown("<h1 style='color: #8e7cc3; font-weight: 300;'>HYPER-INTELLIGENCE CENTER</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter complex inquiry..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    memory.record(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("EXECUTING NEURAL REASONING..."):
            brain = get_brain_engine()
            # 과거 대화 맥락을 포함하여 지능적인 추론 유도
            chat = brain.start_chat(history=[]) 
            response = chat.send_message(prompt)
            
            output = response.text
            st.markdown(output)
            st.code(output, language="markdown")
    
    st.session_state.messages.append({"role": "assistant", "content": output})
    memory.record(st.session_state.session_id, "assistant", output)