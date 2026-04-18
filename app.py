import streamlit as st
import sqlite3
from datetime import datetime
import os

# 1. 라이브러리 로드
try:
    import google.generativeai as genai
except ImportError:
    st.error("SYSTEM ERROR: 'google-generativeai' 설치가 필요합니다.")

# ==========================================
# 2. 페이지 및 테마 설정 (이모티콘 배제)
# ==========================================
page_icon_path = "logo.png" if os.path.exists("logo.png") else None
st.set_page_config(
    page_title="OTGALNON - Next Gen Intelligence",
    page_icon=page_icon_path,
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0b091a; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #0e0c1f; border-right: 1px solid #4b3d8f; }
    .stChatMessage { background-color: rgba(75, 61, 143, 0.1) !important; border: 1px solid rgba(75, 61, 143, 0.3); border-radius: 12px !important; }
    .stButton>button { background: linear-gradient(45deg, #4b3d8f, #6d5dfc); color: white; border: none; font-weight: 600; width: 100%; transition: 0.3s; }
    .stButton>button:hover { box-shadow: 0 0 15px #6d5dfc; transform: translateY(-1px); }
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
    st.session_state.session_id = "otgalnon_gen2_core"
if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. 하이퍼 추론 엔진 (Gemini 2.5
 적용)
# ==========================================
def run_ai_inference(user_input):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "CRITICAL ERROR: API Key가 감지되지 않았습니다."

    try:
        genai.configure(api_key=api_key)
        
        # [수정 포인트] 1.5 Pro 대신 Gemini 2.5 Flash 사용
        # 지원 여부에 따라 'gemini-2.5-flash' 또는 'gemini-2.5-flash-exp' 사용
        model_name = 'gemini-2.5-flash' 
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=(
                "당신은 OTGALNON의 하이퍼 분석 엔진입니다. "
                "이모티콘을 절대 사용하지 않으며, 모든 답변은 데이터와 논리에 기반해야 합니다. "
                "전문적인 용어를 사용하되 구조는 명확하게(서론-본론-결론) 작성하십시오. "
                "사용자의 지적 수준에 맞춘 고도화된 추론 결과만을 출력하십시오."
            )
        )
        
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        # 404 에러 등이 날 경우 모델명을 -exp 버전으로 자동 전환 시도 (fallback)
        if "404" in str(e):
            return "ANALYSIS FAILED: 지정된 모델(2.5 Flash)을 현재 리전에서 사용할 수 없습니다. API 설정을 확인하십시오."
        return f"SYSTEM ERROR: 엔진 구동 실패. (사유: {str(e)})"

# ==========================================
# 5. 메인 컨트롤 센터 UI
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png")
    st.markdown("<h3 style='text-align: center;'>OTGALNON v3.0</h3>", unsafe_allow_html=True)
    st.divider()
    if st.button("RESET WORKSPACE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300; letter-spacing: 1px;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter complex inquiry..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("EXECUTING NEURAL REASONING..."):
            answer = run_ai_inference(prompt)
            st.markdown(answer)
            st.code(answer, language="markdown")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    db.save(st.session_state.session_id, "assistant", answer)