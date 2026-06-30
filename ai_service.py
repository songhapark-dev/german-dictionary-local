import json
from config import GEMINI_API_KEY
from google import genai


def search_word_via_ai(user_input):
    """Nutzt die Gemini-API, um Tippfehler zu korrigieren und die Bedeutung zu extrahieren."""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return user_input, "Bitte geben Sie zuerst Ihren API-Key ein!"

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
    너는 독일어 전문가이자 유능한 번역가야. 입력된 독일어 데이터의 오타를 교정하고 정확한 한국어 뜻을 추출해줘.
    
    [처리 규칙]
    1. 오타 교정: 유저가 입력한 독일어(단어, 숙어, 관용구, 슬랭 등)에 오타나 대소문자 오류가 있다면 올바르게 교정해줘.
    2. 뜻풀이 (meaning):
       - 단어뿐만 아니라 숙어(Redewendung)나 슬랭(Umgangssprache)인 경우에도 핵심 한국어 의미를 정확히 짚어줘.
       - 🚨 [중요 - 글자 수 제한]: 한국어 설명은 반드시 공백을 포함하여 **최대 60자 이내**로 명확하고 간결하게 요약해줘. 화면에 예쁘게 나오도록 불필요하게 길게 늘어놓지 마.
    [출력 규칙]
    - 반드시 아래 제공하는 JSON 형식으로만 답변해줘.
    - 마크다운 기호(```json)나 앞뒤 불필요한 설명은 절대 붙이지 말고 순수한 JSON 문자열만 반환해줘.
    
    유저 입력값: {user_input}
    
    응답 형식:
    {{"word": "교정된 올바른 독일어 단어 또는 숙어", "meaning": "핵심 한국어 뜻 및 상황/뉘앙스 설명"}}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = json.loads(response.text.strip())
        return result["word"], result["meaning"]
    except Exception as e:
        print(f"Fehler beim API-Aufruf: {e}")
        return None, None