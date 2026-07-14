import streamlit as st
import google.generativeai as genai

def initialize_otgalnon():
    """Gemini API를 연결하고 모델을 반환합니다."""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None, "API Key Missing"
    
    genai.configure(api_key=api_key)
    try:
        model_list = [m.name for m in genai.list_models()]
        target = next((m for m in model_list if "gemini-3-flash" in m), "models/gemini-1.5-flash")
        
        model = genai.GenerativeModel(
            model_name=target,
            system_instruction=(
                "당신은 OTGALNON의 최고 분석관입니다. "
                "이모티콘 사용을 엄격히 금지하며, 제1원리 추론에 기반해 논리적으로 답변하십시오. "
                "사용자가 발표 자료나 PPT 형태의 출력을 요구하면, 각 슬라이드의 제목은 '###' 또는 '##'으로 구분하고, "
                "내용은 글머리 기호(* 또는 -)를 사용하여 요약식으로 가독성 있게 작성하십시오."
            )
        )
        return model, target
    except Exception as e:
        return None, str(e)