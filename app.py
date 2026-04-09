import streamlit as st
import sqlite3
from datetime import datetime
import os

# ==========================================
# 1. 페이지 설정 (이전 버전의 스타일 복구)
# ==========================================
st.set_page_config(
    page_title="otgalnon 개발 엔진",
    page_icon="🚀",
    layout="wide",  # 넓은 화면 구성
    initial_sidebar_state="expanded"
)

# 이전 버전의 깔끔한 디자인을 위한 커스텀 CSS
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 저장소 엔진 (SQLite 기반)
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
# 3. 데이터 및 세션 초기화
# ==========================================
db = ChatManager()

if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

# 앱 시작 시 DB에서 기존 내역 로드
if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. 사이드바 (기존 설정 버튼 및 상태창)
# ==========================================
with st.sidebar:
    st.title("⚙️ Engine Control")
    st.success("System Status: Online")
    st.divider()
    
    # 이전 버전에서 사용하던 세션 관리 버튼들
    st.info(f"현재 세션: {st.session_state.session_id}")
    
    if st.button("🔄 화면 새로고침"):
        st.rerun()
        
    if st.button("🗑️ 대화 비우기"):
        st.session_state.messages = []
        # 화면만 비우고 DB는 유지하거나, 필요시 새 세션ID 부여 가능
        st.rerun()
    
    st.divider()
    st.caption("v2.7 - Storage Integrated")

# ==========================================
# 5. 핵심 엔진 로직 (회전 명령어 등)
# ==========================================
def process_command(text):
    """사용자가 이전에 구현했던 핵심 기능들"""
    if "시계방향" in text or "회전" in text:
        return "🔄 **[명령 수행]** otgalnon 엔진이 시계방향으로 회전되었습니다."
    elif "라면" in text:
        return "🍜 **[가이드]** 라면 끓이는 법: 물 550ml -> 스프 -> 면 4분!"
    else:
        return f"✅ **[연산 완료]** '{text}' 명령에 대한 처리가 끝났습니다."

# ==========================================
# 6. 메인 화면 및 채팅 (복사 버튼 기능 포함)
# ==========================================
st.title("🚀 otgalnon 개발 환경")

# 대화 내용 렌더링
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # 이전 버전의 편의 기능: 응답 내용 복사 버튼 대용 (st.code 활용)
        if msg["role"] == "assistant":
             # 복사 버튼이 기본 포함된 코드 블록 형태로 출력
             st.code(msg["content"], language="text")

# 채팅 입력 및 처리
if prompt := st.chat_input("여기에 명령어를 입력하세요..."):
    # 1. 사용자 메시지
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    # 2. AI 응답 (이전의 풍부한 답변 방식 적용)
    with st.chat_message("assistant"):
        with st.spinner("엔진 연산 중..."):
            response = process_command(prompt)
            st.markdown(response)
            st.code(response, language="text") # 복사하기 편하도록 추가
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    db.save(st.session_state.session_id, "assistant", response)