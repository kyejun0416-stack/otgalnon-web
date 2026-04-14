import streamlit as st
import sqlite3
from datetime import datetime
import os

# 1. 라이브러리 로드 및 예외 처리
try:
    import google.generativeai as genai
except ImportError:
    st.error("SYSTEM ERROR: 'google-generativeai' 라이브러리를 찾을 수 없습니다. requirements.txt를 확인하십시오.")

# ==========================================
# 2. 페이지 및 테마 설정 (이모티콘 배제)
# ==========================================
# 로고 파일을 페이지 아이콘으로 설정
page_icon_path = "logo.png" if os.path.exists("logo.png") else None

st.set_page_config(
    page_title="OTGALNON - Hyper Intelligence",
    page_icon=page_icon_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 고급 보라색 테마 및 UI 스타일링
st.markdown("""
    <style>
    .main {
        background-color: #0b091a;
        background: linear-gradient(to bottom, #0b091a, #1a1635, #121026);
        color: #d1d1d1;
    }
    [data-testid="stSidebar"] {
        background-color: #0e0c1f;
        border-right: 1px solid #4b3d8f;
    }
    .stChatMessage {
        background-color: rgba(75, 61, 143, 0.1) !important;
        border: 1px solid rgba(75, 61, 143, 0.3);
        border-radius: 10px !important;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background: linear-gradient(45deg, #4b3d8f, #6d5dfc);
        color: white;
        border: none;
        font-weight: 600;
        letter-spacing: 0.5px;
        width: 100%;
    }
    .stTextInput>div>div>input {
        background-color: #121026;
        color: #ffffff;
        border-color: #4b3d8f !important;
    }
    /* 로고 중앙 정렬 */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 데이터베이스 및 세션 관리
# ==========================================
class MemoryManager:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS chat_log 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp DATETIME)''')

    def save(self, session_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                         (session_id, role, content, datetime.now()))

    def load(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

db = MemoryManager()

# [중요] 세션 초기화 순서 강제 (AttributeError 방지)
if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_core_v3"

if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. AI 브레인 설정 (Gemini 1.5 Pro)
# ==========================================
# API 키 설정 (Streamlit Secrets 권장)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # 지능 극대화를 위한 시스템 명령어
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction=(
            "당신은 OTGALNON의 고도화된 분석 엔진입니다. "
            "이모티콘 사용을 엄격히 금지하며, 지적이고 분석적인 태도를 유지하십시오. "
            "사용자의 질문에 대해 제1원리 사고에 입각하여 구조적인 해답을 제시하십시오. "
            "답변은 마크다운 형식을 활용하되, 가독성보다 논리적 완성도에 집중하십시오."
        )
    )
else:
    model = None

# ==========================================
# 5. UI 구성
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png")
    else:
        st.markdown("<h1 style='text-align: center; color: #6d5dfc;'>OTGALNON</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #888;'>HYPER INTELLIGENCE ENGINE</p>", unsafe_allow_html=True)
    st.divider()
    
    st.write(f"SYSTEM: **ONLINE**")
    st.write(f"SESSION: `{st.session_state.session_id}`")
    
    if st.button("CLEAR WORKSPACE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300; letter-spacing: 1px;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

# 대화 로그 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력 처리
if prompt := st.chat_input("Enter research command..."):
    # 1. 사용자 입력 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    # 2. AI 분석 수행
    with st.chat_message("assistant"):
        if model:
            with st.spinner("ANALYZING DATA..."):
                try:
                    response = model.generate_content(prompt)
                    answer = response.text
                except Exception as e:
                    answer = f"ANALYSIS FAILED: {str(e)}"
        else:
            answer = "CRITICAL ERROR: API Key가 설정되지 않았습니다. 관리자 설정을 확인하십시오."
        
        st.markdown(answer)
        st.code(answer, language="markdown") # 복사용 코드 블록

    # 3. 결과 저장
    st.session_state.messages.append({"role": "assistant", "content": answer})
    db.save(st.session_state.session_id, "assistant", answer)


