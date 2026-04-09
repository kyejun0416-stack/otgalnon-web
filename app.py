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

db = ChatManager()

if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 3. 답변 생성 로직 (이 부분이 핵심입니다!)
# ==========================================
def generate_response(user_input):
    """
    사용자의 입력에 따라 풍부한 답변을 생성하는 로직
    (추후 여기에 실제 LLM API를 연결하면 완벽해집니다)
    """
    input_text = user_input.strip()
    
    # 1. 시계방향 회전 명령어 처리
    if "시계방향" in input_text or "회전" in input_text:
        return (
            "🔄 **otgalnon 엔진 회전 제어 시스템 가동**\n\n"
            "사용자의 요청에 따라 엔진을 시계방향으로 회전 시켰습니다.\n"
            "- 회전 각도: 기본값(90도)\n"
            "- 상태: 정상 작동 중"
        )
    
    # 2. 라면 끓이는 법 (테스트용 응답 보강)
    elif "라면" in input_text:
        return (
            "🍜 **otgalnon 엔진이 알려주는 맛있는 라면 레시피**\n\n"
            "1. 물 550ml를 엔진 가열 장치로 끓입니다.\n"
            "2. 물이 끓으면 건더기 스프와 분말 스프를 먼저 넣습니다.\n"
            "3. 면을 넣고 4분간 더 끓입니다. (면을 들었다 놨다 하면 더 쫄깃해요!)\n"
            "4. 마지막에 계란이나 파를 곁들이면 완성입니다."
        )
    
    # 3. 기본 응답
    else:
        return (
            f"📢 **엔진 알림**\n\n"
            f"입력하신 내용: '{input_text}'\n"
            f"현재 이 명령은 처리 대기 중이거나 학습되지 않은 명령어입니다. "
            f"개발자님, 이 질문에 대한 새로운 로직을 추가해보는 건 어떨까요?"
        )

# ==========================================
# 4. UI 및 채팅 처리
# ==========================================
st.title("🚀 otgalnon 개발 엔진 v2.5")
st.info("데이터베이스에 실시간 저장 중입니다.")

# 대화 내용 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력창
if prompt := st.chat_input("질문을 입력해보세요 (예: 라면 끓이는 법)"):
    
    # [사용자] 화면 표시 및 DB 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    # [AI] 답변 생성, 화면 표시 및 DB 저장
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            # 이제 이 함수가 풍부한 답변을 내뱉습니다!
            full_response = generate_response(prompt) 
            st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    db.save(st.session_state.session_id, "assistant", full_response)