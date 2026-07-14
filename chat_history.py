import json
import os

HISTORY_FILE = "chat_history.json"

def load_history():
    """파일에서 대화 기록을 불러옵니다."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(messages):
    """대화 기록을 파일에 즉시 저장합니다."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def clear_history():
    """저장된 대화 기록 파일을 삭제합니다."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)