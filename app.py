import streamlit as st
import sqlite3
from datetime import datetime
import os

# 라이브러리 로드 시 예외 처리
try:
    import google.generativeai as genai
except ImportError:
    st.error("requirements.txt에 google-generativeai가 누락되었거나 설치 중입니다.")

# ==========================================
# 1. 페이지 설정 및 테마 (이모티콘 제거)
# ==========================================
page_icon_path = "logo.png" if os.path.exists("logo.png") else None
st.set_page_config(
    page_title="OTGALNON - Hyper Intelligence",
    page_icon=page_icon_path,
    layout="wide"
)

# 고급 보라색 테마 유지
st.markdown("""
    <style>
    .main { background: #0b091a; color: #d1d1d1; }
    [data-testid="stSidebar"] { background-color: #121026; border-right: 1px solid #4b3d8f; }
    .stChatMessage { background-color: rgba(75, 61, 143, 0.1) !important; border: 1px solid #4b3d8f; border-radius: 8px; }
    .stButton>button { background: linear-gradient(45deg, #6d5dfc, #b83af3); color: white; border: none; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터베이스 엔진
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
# 3. 핵심 로직 및 세션 초기화 (순서 수정)
# ==========================================
memory = MemoryEngine()

# [중요] session_id를 가장 먼저 초기화하여 AttributeError 방지
if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

# 그 다음 메시지 내역 로드
if "messages" not in st.session_state:
    st.session_state.messages = memory.recall(st.session_state.session_id)

# Gemini 설정
api_key = "YOUR_GEMINI_API_KEY" # 실제 키로 교체 필요
if api_key != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=api_key)

# ==========================================
# 4. 사이드바 및 UI
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    st.markdown("<h2 style='text-align: center;'>OTGALNON</h2>", unsafe_allow_html=True)
    st.divider()
    
    st.write(f"System Status: **ACTIVE**")
    st.write(f"Session: `{st.session_state.session_id}`")
    
    if st.button("RESET WORKSPACE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h1 style='color: #8e7cc3; font-weight: 300; letter-spacing: 2px;'>HYPER-INTELLIGENCE CENTER</h1>", unsafe_allow_html=True)

# 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 명령어 입력 및 처리
if prompt := st.chat_input("Enter command..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    memory.record(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                # Pro 모델로 고도화된 추론 수행
                model = genai.GenerativeModel('gemini-1.5-pro')
                sys_instruct = "당신은 OTGALNON의 분석 엔진입니다. 전문적이고 이모티콘 없는 고도의 지성체로 답하십시오."
                response = model.generate_content(f"{sys_instruct}\n\n질문: {prompt}")
                output = response.text
            except Exception as e:
                output = f"Operation Error: 분석 엔진 응답 실패. (사유: API 키 확인 필요)"
            
            st.markdown(output)
            st.code(output, language="markdown")
    
    st.session_state.messages.append({"role": "assistant", "content": output})
    memory.record(st.session_state.session_id, "assistant", output)