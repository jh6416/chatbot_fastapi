import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

# OpenAI 클라이언트 초기화
client = AsyncOpenAI(api_key=api_key)

async def generate_response(message: str) -> str:
    """
    GPT를 사용하여 사용자 메시지에 대한 응답을 생성합니다.
    
    Args:
        message: 사용자 입력 메시지
        
    Returns:
        GPT가 생성한 응답
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 친절하고 도움이 되는 한국어 챗봇입니다."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        raise e 