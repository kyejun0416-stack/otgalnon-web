import streamlit as st
import requests
import base64
import re

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon: Direct Engine", page_icon="⚡", layout="centered")

# 스타일 커스텀 (다크 모드 감성)
st.markdown("""
    <style>
    .stTextArea textarea { background-color: #1e1e1e; color: #ffffff; border-radius: 10px; }
    .stButton button { width: 100%; border-radius: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 사이드바 (설정)
with st.sidebar:
    st.title("⚙️ otgalnon Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    model_choice = st.selectbox("Engine", ["gemini-2.0-flash", "gemini-1.5-pro"])
    st.divider()
    st.caption("Project: otgalnon v3.5")
    st.caption("Mode: Direct Strategy")

# 3. 메인 인터페이스
st.title("🧠 오트가논 (otgalnon)")
st.info("내부적으로 분해와 검증을 거친 '최종 전략'만 즉시 출력합니다.")

user_input = st.text_area("분석할 과제를 입력하세요", placeholder="내용 입력 또는 이미지 업로드...", height=150)
uploaded_file = st.file_uploader("이미지 업로드 (선택)", type=["jpg", "jpeg", "png"])

# 4. 분석 및 출력 로직
if st.button("⚡ 오트가논 가동"):
    if not api_key:
        st.error("❗ 사이드바에 API 키를 입력해주세요.")
    elif not user_input and not uploaded_file:
        st.warning("❗ 입력 내용이 없습니다.")
    else:
        with st.spinner("🧠 오트가논이 전략을 추출 중입니다..."):
            url = f"https://generativelanguage.googleapis.com/v1/models/{model_choice}:generateContent?key={api_key}"
            
            # 다이렉트 출력 전용 시스템 규칙
            system_instruction = """
            당신은 '오트가논(otgalnon)' 논리 엔진입니다. 
            내부적으로 [분해], [검증]을 거쳐 최적의 해답을 도출하되, 답변 시에는 오직 최종 결론과 실행 지침만 핵심 위주로 제시하세요.
            불필요한 인사말, 기호, 마크다운 서식을 최소화하여 전달하세요.
            """
            
            parts = [{"text": f"{system_instruction}\n\n사용자 요청: {user_input}"}]
            
            if uploaded_file:
                image_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": image_b64}})
            
            payload = {"contents": [{"parts": parts}]}
            
            try:
                response = requests.post(url, json=payload)
                answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                
                # 결과 박스
                st.subheader("🎯 최종 전략")
                st.write(answer)
                
                # 순수 텍스트 복사 기능 (기호 제거)
                clean_text = re.sub(r'[*#\-`>]', '', answer).strip()
                
                # Streamlit의 코드박스는 클릭 시 자동 복사 기능을 지원함
                st.divider()
                st.caption("📋 아래 박스를 클릭하면 기호 없는 '순수 내용'이 복사됩니다.")
                st.code(clean_text, language=None)
                
            except Exception as e:
                st.error(f"❌ 엔진 가동 실패: {e}")

st.divider()
st.caption("© 2026 Project otgalnon - Direct Strategy Mode")