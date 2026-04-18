import streamlit as st
import sqlite3
from datetime import datetime
import os
import time

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
    st.session_state.session_id = "otgalnon_stable_v4"
if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. 하이퍼 추론 엔진 (에러 복구 로직 포함)
# ==========================================
def run_intelligent_inference(user_input):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "CRITICAL ERROR: API Key가 존재하지 않습니다."

    genai.configure(api_key=api_key)
    
    # 가용 모델 리스트 (사용 가능한 것을 순차적으로 시도)
    model_candidates = ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']
    
    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction="이모티콘을 배제하고 논리적이고 전문적인 분석 결과를 제공하십시오."
            )
            response = model.generate_content(user_input)
            return f"**[ENGINE: {model_name}]**\n\n{response.text}"
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg: # 할당량 초과 시
                st.warning(f"{model_name} 할당량 초과. 다음 엔진으로 전환합니다...")
                time.sleep(2) # 짧은 대기 후 전환
                continue
            return f"SYSTEM ERROR: {err_msg}"
    
    return "제한 사항: 현재 모든 엔진의 할당량이 소진되었습니다. 약 1분 후 다시 시도해 주십시오."

# ==========================================
# 5. UI 구성 및 실행
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png")
    st.markdown("<h2 style='text-align: center;'>OTGALNON</h2>", unsafe_allow_html=True)
    st.divider()
    if st.button("RESET"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300;'>CONTROL CENTER</h2>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter command..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("ANALYZING..."):
            answer = run_intelligent_inference(prompt)
            st.markdown(answer)
            st.code(answer, language="markdown")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    db.save(st.session_state.session_id, "assistant", answer)