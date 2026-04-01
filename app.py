import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정 및 브라우저 탭 아이콘(Favicon) 적용
st.set_page_config(
    page_title="otgalnon",
    page_icon="logo.png",
    layout="centered"
)

# CSS 스타일: 미니멀리즘 및 전문적인 다크 톤 유지
st.markdown("""
    <style>
    /* 메인 배경 및 텍스트 영역 스타일 */
    .stTextArea textarea { background-color: #1e1e1e; color: #ffffff; border-radius: 5px; border: 1px solid #333; }
    
    /* 버튼 스타일: 수학적 간결함 강조 */
    .stButton button { 
        width: 100%; 
        border-radius: 5px; 
        font-weight: bold; 
        background-color: #262626; 
        color: #efefef; 
        border: 1px solid #444;
        transition: all 0.3s;
    }
    .stButton button:hover { border-color: #ffffff; color: #ffffff; background-color: #333; }
    
    /* 로고 및 타이틀 간격 조절 */
    [data-testid="stImage"] { margin-bottom: -30px; }
    
    /* 코드 박스(복사 영역) 스타일 */
    code { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 로고 및 헤더 섹션
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.caption("No Logo")

with col2:
    st.title("otgalnon")
    st.caption("Strategic Insight & Logic Engine")

st.divider()

# 3. API 키 보안 로드 (Secrets 우선, 없을 시 사이드바)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.title("System Settings")
        api_key = st.text_input("Gemini API Key", type="password")
        st.info("💡 Permanent access: Add GEMINI_API_KEY to Streamlit Secrets.")

# 사이드바 설정 영역
with st.sidebar:
    st.divider()
    model_choice = st.selectbox("Engine Selection", ["gemini-flash-latest", "gemini-pro-latest"])
    st.caption("Project: otgalnon v4.5")
    st.caption("Architecture: Minimal Vector Logic")

# 4. 메인 입력 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="분석할 내용을 입력하거나 이미지를 업로드하십시오.", height=180)
uploaded_file = st.file_uploader("데이터 업로드 (이미지)", type=["jpg", "jpeg", "png"])

# 5. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("시스템 가동 실패: API Key가 유효하지 않습니다.")
    elif not user_input and not uploaded_file:
        st.warning("분석 데이터 미검출: 내용을 입력하십시오.")
    else:
        with st.spinner("Processing Logic..."):
            # 정밀 타격 엔드포인트 구성
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
            
            # 수학적 간결함을 유지하기 위한 시스템 프롬프트
            system_instruction = (
                "당신은 '오트가논(otgalnon)' 전략 엔진입니다. "
                "모든 답변에서 이모티콘 사용을 엄격히 금지합니다. "
                "수학적 증명처럼 간결하고 논리적인 문체를 유지하며, "
                "불필요한 수식어를 배제하고 핵심 실행 지침과 전략적 결론만 출력하십시오."
            )
            
            parts = [{"text": f"{system_instruction}\n\nTask: {user_input}"}]
            
            if uploaded_file:
                image_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": image_b64}})
            
            payload = {
                "contents": [
                    {
                        "parts": parts
                    }
                ]
            }
            headers = {'Content-Type': 'application/json'}
            
           try:
                # 1. API 호출
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                res_json = response.json()
                
                # 2. 응답 성공 여부 확인
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    st.markdown("### Strategic Output")
                    st.write(answer)
                    
                    # [에러 지점] 텍스트 정제 및 복사 영역
                    clean_text = re.sub(r'[*#\-`>]', '', answer).strip()
                    st.divider()
                    st.caption("Plain Text for Copy")
                    st.code(clean_text, language=None)
                else:
                    # API는 응답했으나 에러 내용이 있는 경우
                    error_msg = res_json.get('error', {}).get('message', 'Unknown API Error')
                    st.error(f"Engine Error: {error_msg}")
                    
            except Exception as e:
                # 네트워크 오류 등 시스템 예외 처리 (SyntaxError 해결의 핵심)
                st.error(f"System Failure: {e}")

# 최하단 푸터
st.divider()
st.caption("© 2026 otgalnon Architecture. All rights reserved.")