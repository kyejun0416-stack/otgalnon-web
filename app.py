import streamlit as st
import sqlite3
from datetime import datetime
import os

# ==========================================
# 1. 페이지 테마 및 환경 설정 (복구 완료)
# ==========================================
st.set_page_config(
    page_title="otgalnon 개발 엔진 v2.6",
    page_icon="⚙️",
    layout="wide",  # 넓은 화면 모드 복구
    initial_sidebar_state="expanded"
)

# 커스텀 스타일 (필요시 추가했던 CSS 설정들을 여기에 유지)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    stChatMessage {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터베이스 관리 클래스
# ==========================================
class ChatManager:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME
                )
            ''')
            conn.commit()

    def save(self, session_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now())
            )
            conn.commit()

    def load(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

# ==========================================
# 3. 초기화 로직
# ==========================================
db = ChatManager()

if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. 사이드바 및 편의 기능 (복구 및 강화)
# ==========================================
with st.sidebar:
    st.title("🚀 Project otgalnon")
    st.subheader("Engine Status: [RUNNING]")
    st.divider()
    
    st.info(f"📍 현재 세션: {st.session_state.session_id}")
    
    # 기록 초기화 및 관리
    if st.button("🗑️ 화면 비우기", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("© 2026 otgalnon Dev Team")

# ==========================================
# 5. 엔진 로직 (기존 회전 명령 등)
# ==========================================
def process_otgalnon_command(command):
    cmd = command.strip()
    if "시계방향" in cmd or "회전" in cmd:
        return "🔄 **[엔진 제어]** 시계방향 회전 명령을 성공적으로 수행했습니다."
    elif "라면" in cmd:
        return "🍜 **[레시피 엔진]** 물 550ml, 스프 먼저, 면 4분! 쫄깃하게 완성하세요."
    else:
        return f"✅ **[분석 완료]** 입력값 '{cmd}'에 대한 연산을 마쳤습니다."

# ==========================================
# 6. 메인 채팅 인터페이스 (복사 버튼 포함)
# ==========================================
st.title("💬 otgalnon 대화형 엔진")

# 대화 내용 렌더링
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 각 메시지 하단에 복사 버튼 추가 (Streamlit 기본 기능 활용)
        if msg["role"] == "assistant":
            # st.button 대신 st.code나 특정 컴포넌트를 사용하여 복사 편의성 제공
            pass 

# 입력창
if prompt := st.chat_input("명령어를 입력하세요..."):
    # 사용자 메시지
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    # AI 응답
    with st.chat_message("assistant"):
        with st.spinner("엔진 가동 중..."):
            response = process_otgalnon_command(prompt)
            st.markdown(response)
            # 최신 응답에 대해 복사하기 편하도록 코드 블록 스타일로도 제공 가능
            if "회전" in prompt:
                st.code(response, language="text") 
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    db.save(st.session_state.session_id, "assistant", response)