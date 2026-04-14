import streamlit as st
import sqlite3
from datetime import datetime
import os

# 1. 라이브러리 로드
try:
    import google.generativeai as genai
except ImportError:
    st.error("SYSTEM ERROR: 'google-generativeai' 라이브러리가 필요합니다.")

# ==========================================
# 2. 페이지 및 테마 설정
# ==========================================
page_icon_path = "logo.png" if os.path.exists("logo.png") else None
st.set_page_config(
    page_title="OTGALNON - Hyper Intelligence",
    page_icon=page_icon_path,
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0b091a; color: #d1d1d1; }
    [data-testid="stSidebar"] { background-color: #0e0c1f; border-right: 1px solid #4b3d8f; }
    .stChatMessage { background-color: rgba(75, 61, 143, 0.1) !important; border: 1px solid rgba(75, 61, 143, 0.3); border-radius: 10px !important; }
    .stButton>button { background: linear-gradient(45deg, #4b3d8f, #6d5dfc); color: white; border: none; font-weight: 600; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 데이터베이스 엔진
# ==========================================
class MemoryEngine:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
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

db = MemoryEngine()
if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_pro_engine"
if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. 고성능 AI 추론 엔진 (Gemini 1.5 Pro)
# ==========================================
def run_hyper_inference(user_input):
    # Streamlit Secrets에서 API Key 로드
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "CRITICAL ERROR: 유효한 API Key가 감지되지 않았습니다. Secrets 설정을 확인하십시오."

    try:
        genai.configure(api_key=api_key)
        
        # 404 에러 방지를 위한 표준 모델명 설정
        # 지능 고도화를 위해 반드시 'gemini-1.5-pro' 사용
        model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            system_instruction=(
                "당신은 OTGALNON의 핵심 지능 아키텍트입니다. "
                "사용자의 요청에 대해 단순 대답을 지양하고, 다각적인 심층 분석을 수행하십시오. "
                "텍스트에서 모든 이모티콘을 배제하고, 한국어 경어체를 사용하되 논리적인 엄격함을 유지하십시오. "
                "답변은 보고서 형식(개요-분석-결론)으로 구조화하십시오."
            )
        )
        
        # 추론 실행
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"SYSTEM ERROR: 분석 엔진 가동 중 오류가 발생했습니다. ({str(e)})"

# ==========================================
# 5. 메인 컨트롤 센터 UI
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png")
    st.markdown("<h2 style='text-align: center;'>OTGALNON</h2>", unsafe_allow_html=True)
    st.divider()
    if st.button("RESET ENGINE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300; letter-spacing: 1px;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

# 히스토리 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력 처리 루프
if prompt := st.chat_input("Enter command or research query..."):
    # 1. 사용자 메시지 처리
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    # 2. AI 하이퍼 추론 실행
    with st.chat_message("assistant"):
        with st.spinner("PERFORMING NEURAL ANALYSIS..."):
            answer = run_hyper_inference(prompt)
            st.markdown(answer)
            # 전문가용 복사 코드 블록 제공
            st.code(answer, language="markdown")

    # 3. 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": answer})
    db.save(st.session_state.session_id, "assistant", answer)
