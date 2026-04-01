import streamlit as st
import requests
import base64
import re

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon: Direct Engine", page_icon="⚡", layout="centered")

# 2. 사이드바 (설정)
with st.sidebar:
    st.title("⚙️ otgalnon Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    # 모델 이름을 가장 안정적인 버전으로 고정하거나 선택
    model_choice = st.selectbox("Engine", ["gemini-1.5-flash", "gemini-1.5-pro"])
    st.divider()
    st.caption("Project: otgalnon v3.6")

# 3. 메인 인터페이스
st.title(" 오트가논 (otgalnon)")

user_input = st.text_area("분석할 과제를 입력하세요", placeholder="내용 입력...", height=150)
uploaded_file = st.file_uploader("이미지 업로드 (선택)", type=["jpg", "jpeg", "png"])

if st.button("⚡ 오트가논 가동"):
    if not api_key:
        st.error("❗ 사이드바에 API 키를 입력해주세요.")
    else:
        with st.spinner(" 전략 추출 중..."):
            # API URL 구성 (v1beta 사용 권장)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
            
            system_instruction = "당신은 '오트가논' 엔진입니다. 내부적으로 분해/검증 후 [출력] 내용만 핵심 위주로 제시하세요."
            parts = [{"text": f"{system_instruction}\n\n사용자 요청: {user_input}"}]
            
            if uploaded_file:
                image_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": image_b64}})
            
            payload = {"contents": [{"parts": parts}]}
            
            try:
                response = requests.post(url, json=payload)
                res_json = response.json()
                
                # [디버깅] candidates가 없을 경우 에러 내용 상세 출력
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.subheader("🎯 최종 전략")
                    st.write(answer)
                    
                    # 복사용 텍스트 정제
                    clean_text = re.sub(r'[*#\-`>]', '', answer).strip()
                    st.divider()
                    st.caption("📋 클릭 시 순수 내용 복사")
                    st.code(clean_text, language=None)
                else:
                    # 구글이 보낸 에러 메시지를 직접 표시
                    error_msg = res_json.get('error', {}).get('message', '알 수 없는 API 오류')
                    st.error(f"❌ API 응답 오류: {error_msg}")
                    with st.expander("상세 로그 보기"):
                        st.write(res_json)
                        
            except Exception as e:
                st.error(f"❌ 시스템 오류: {e}")
