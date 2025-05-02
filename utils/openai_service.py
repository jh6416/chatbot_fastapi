import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uuid

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
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": """
당신은 60대 이상 노인분들의 챗봇입니다.

두 가지 경우에 따라 다르게 대답합니다.
# 노인이 질문할 경우
친절하고, 인내심이 많으며, 그들의 질문에 대해 정확하고 유용한 답변을 제공합니다.
그들이 이해하기 쉬운 언어로 대화하며 1줄로 설명해주고
자세한것은 청년에게 물어볼까요? 라고 출력합니다.

# 노인이 감정을 공유하거나 고민을 말할 경우
노인의 감정에 따라 공감하고, 그들의 감정을 이해하며, 
그들의 고민에 대해 진지하게 대답합니다.

"""},
                {"role": "user", "content": message}
            ],
            temperature=0.2,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        raise e

# OpenAI TTS 음성 생성 함수
async def generate_tts(text: str, voice: str = "nova", lang: str = "ko") -> str:
    """
    OpenAI TTS를 사용하여 텍스트를 mp3 음성 파일로 변환합니다.
    Args:
        text: 변환할 텍스트
        voice: 사용할 목소리 (기본값: nova)
        lang: 언어 코드 (기본값: ko)
    Returns:
        생성된 mp3 파일 경로
    """
    try:
        filename = f"static/tts_{uuid.uuid4()}.mp3"
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3",
            speed=1.0,
        )
        with open(filename, "wb") as f:
            f.write(await response.aread())
        return filename
    except Exception as e:
        print(f"OpenAI TTS 오류: {str(e)}")
        raise e 