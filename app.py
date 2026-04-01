import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 보라색 테마 기반 CSS (강력 적용)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    /* 입력창이 무조건 보이도록 배경색과 테두리 강조 */
    .stTextArea textarea { 
        background-color: #1e1e2e !important; 
        color: #ffffff !important; 
        border: 2px solid #4b0082 !important; 
        border-radius: 8px; 
    }
    .stButton button { 
        width: 100%; border-radius: 8px; font-weight: bold; 
        background-color: #4b0082; color: white; border: none; height: 3em;
    }
    .stButton button:hover { background-color: #6a0dad; box-shadow: 0 0 15px #6a0dad; }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    [data-testid="stImage"] { margin-bottom: -35px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더 섹션 (로고 & 타이틀)
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.write("🟣") # 로고 없을 시 임시 아이콘

with col2:
    st.title("otgalnon")
    st.markdown("<p style='color:#8a8ab5; margin-top:-15px;'>Strategic Insight & Logic Engine</p>", unsafe_allow_html=True)

st.divider()

# 4. [수정] 입력 인터페이스를 최우선으로 노출 (조건문 밖으로 추출)
user_input = st.text_area("분석 과제 입력", placeholder="분석할 내용을 입력하십시오.", height=200)
uploaded_file = st.file_uploader("데이터 업로드 (이미지 선택)", type=["jpg", "jpeg", "png"])

# 5. API 키 및 모델 설정 (사이드바)
with st.sidebar:
    st.title("Settings")
    # Secrets 확인 후 없으면 입력창
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key Loaded from Secrets")
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="API 키를 입력해야 엔진이 작동합니다.")
    
    st.divider()
    model_choice = st.selectbox("Engine Selection", ["gemini-flash-latest", "gemini-pro-latest"])
    st.caption("v5.2 | Strategic Purple")

# 6. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("오류: 사이드바(왼쪽 화살표 > 클릭)에 API Key를 입력하십시오.")
    elif not user_input and not uploaded_file:
        st.warning("내용을 입력하십시오.")
    else:
        with st.spinner("Decoding Logic..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
            system_instruction = "당신은 '오트가논' 전략 엔진입니다. 이모티콘 없이 수학적이고 간결한 문체로 핵심만 답변하세요."
            
            parts = [{"text": f"{system_instruction}\n\nTask: {user_input}"}]
            if uploaded_file:
                image_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": image_b64}})
            
            try:
                response = requests.post(url, json={"contents": [{"parts": parts}]}, timeout=30)
                res_json = response.json()
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### Strategic Output")
                    st.write(answer)
                    st.divider()
                    st.code(re.sub(r'[*#\-`>]', '', answer).strip(), language=None)
                else:
                    st.error(f"Engine Error: {res_json.get('error', {}).get('message', 'API Error')}")
            except Exception as e:
                st.error(f"System Failure: {e}")

st.divider()
st.caption("© 2026 otgalnon Architecture.")