import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정 (탭 아이콘 및 타이틀)
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 보라색 테마 디자인 (디지털 전략가 컨셉)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stTextArea textarea { 
        background-color: #1e1e2e !important; 
        color: #ffffff !important; 
        border: 1px solid #4b0082 !important; 
    }
    .stButton button { 
        width: 100%; border-radius: 8px; font-weight: bold; 
        background-color: #4b0082; color: white; border: none; height: 3.5em;
    }
    .stButton button:hover { background-color: #6a0dad; box-shadow: 0 0 20px #6a0dad; }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    [data-testid="stImage"] { margin-bottom: -35px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더 섹션
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    else: st.write("🟣")
with col2:
    st.title("otgalnon")
    st.caption("Strategic Insight & Logic Engine")

st.divider()

# 4. 입력 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="전략적 분석이 필요한 내용을 입력하십시오.", height=200)
uploaded_file = st.file_uploader("이미지 데이터 업로드", type=["jpg", "jpeg", "png"])

# 5. API 설정 (gemini-flash-latest 고정)
with st.sidebar:
    st.title("Control Panel")
    # 사이드바 입력 우선, 없으면 Secrets 확인
    api_key_input = st.text_input("Gemini API Key", type="password", help="새로 발급받은 키를 입력하세요.")
    api_key = api_key_input if api_key_input else st.secrets.get("GEMINI_API_KEY")
    
    model_name = "gemini-flash-latest" # 사용자 지정 모델명
    st.info(f"Engine: {model_name}")
    st.caption("v5.9 | Core Synchronization")

# 6. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("API Key 미검출: 사이드바에 키를 입력하거나 Secrets를 설정하십시오.")
    elif not user_input and not uploaded_file:
        st.warning("입력 데이터가 없습니다.")
    else:
        with st.spinner("Synchronizing with Flash Engine..."):
            try:
                # v1beta 엔드포인트 유지
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                
                instr = "당신은 '오트가논' 엔진입니다. 이모티콘 없이 수학적으로 간결하게 답변하세요."
                
                # 텍스트 파트
                content_parts = [{"text": f"{instr}\n\nTask: {user_input}"}]
                
                # 이미지 파트 (바이너리 읽기 최적화)
                if uploaded_file:
                    img_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    content_parts.append({
                        "inline_data": {
                            "mime_type": uploaded_file.type,
                            "data": img_data
                        }
                    })
                
                # 페이로드 전송
                response = requests.post(
                    url, 
                    json={"contents": [{"parts": content_parts}]}, 
                    timeout=60
                )
                res_json = response.json()
                
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### Strategic Output")
                    st.write(answer)
                    st.divider()
                    # 텍스트 복사용 섹션 (보라색 강조)
                    st.markdown("<p style='color:#bf94ff; font-size:0.8rem;'>Plain Text for Copy</p>", unsafe_allow_html=True)
                    st.code(re.sub(r'[*#\-`>]', '', answer).strip(), language=None)
                else:
                    st.error(f"Engine Error: {res_json.get('error', {}).get('message', 'Unknown response')}")
                    
            except Exception as e:
                st.error(f"System Failure: {e}")

st.divider()
st.caption("© 2026 otgalnon Architecture. Optimized for Flash Engine.")