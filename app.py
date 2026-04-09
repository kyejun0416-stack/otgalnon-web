import streamlit as st
import sqlite3
from datetime import datetime
import os

# ==========================================
# 1. 데이터베이스 관리 클래스 (저장소 엔진)
# ==========================================
class ChatManager:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """데이터베이스 파일과 테이블을 생성합니다."""
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
        """대화 내역을 DB 파일에 물리적으로 저장합니다."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now())
            )
            conn.commit()

    def load(self, session_id):
        """특정 세션의 대화 내역을 모두 가져옵니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

# ==========================================
# 2. 앱 초기 설정 및 데이터베이스 연결
# ==========================================
st.set_page_config(page_title="otgalnon 프로젝트", page_icon="⚙️")

# 데이터베이스 관리자 객체 생성
db = ChatManager()

# 세션 ID 설정
if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

# DB에서 과거 대화 내역 불러오기
if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 3. 프로젝트 핵심 로직 (시계방향 회전 등)
# ==========================================
def process_otgalnon_command(command):
    """기존 otgalnon 엔진 기능을 처리하는 함수"""
    if "시계방향" in command or "회전" in command:
        return "🔄 엔진을 시계방향으로 회전 시켰습니다. (otgalnon command executed)"
    else:
        return f"입력하신 '{command}'에 대한 분석을 완료했습니다."

# ==========================================
# 4. UI 레이아웃 및 채팅 로직
# ==========================================
st.title("🚀 otgalnon 개발 엔진 v2.0")
st.info("모든 대화 기록은 'otgalnon_history.db' 파일에 자동으로 기록됩니다.")

# 사이드바 설정
with st.sidebar:
    st.header("Project Status")
    st.write(f"현재 세션: `{st.session_state.session_id}`")
    if st.button("대화 화면 비우기"):
        st.session_state.messages = []
        st.rerun()

# 1) 저장된 대화 내용을 화면에 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 2) 사용자 입력 처리 (여기가 93라인 근처입니다)
if prompt := st.chat_input("명령어나 대화를 입력하세요..."):
    # 사용자 메시지 화면 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 세션 상태 및 DB에 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    # AI 응답 생성 및 처리
    with st.chat_message("assistant"):
        with st.spinner("엔진 연산 중..."):
            response = process_otgalnon_command(prompt)
            st.markdown(response)
    
    # 세션 상태 및 DB에 AI 메시지 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
    db.save(st.session_state.session_id, "assistant", response)