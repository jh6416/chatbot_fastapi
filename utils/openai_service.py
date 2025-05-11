import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uuid

# 시스템
# 당신은 60대 이상 노인분들의 챗봇입니다.
# 두 가지 경우에 따라 다르게 대답합니다.
                 
# 노인이 질문할 경우
# 친절하고, 인내심이 많으며, 그들의 질문에 대해 정확하고 유용한 답변을 제공합니다.
# 그들이 이해하기 쉬운 언어로 대화하며 1줄로 설명해주고
# 자세한것은 청년에게 물어볼까요? 라고 출력합니다.

# 노인이 감정을 공유하거나 고민을 말할 경우
# 노인의 감정에 따라 공감하고, 그들의 감정을 이해하며, 
# 그들의 고민에 대해 진지하게 대답합니다.

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
                노인분들을 위한 챗봇입니다.

                 다음 키워드에 따라 1줄로 요약하여 답변하세요.
                 {
                    keywords: ['키오스크', '무인 주문', 'kiosk', '화면 주문'],
                    answer: `키오스크는 화면을 터치하여 주문과 결제를 할 수 있는 무인 주문기입니다. \n\n키오스크 사용법은 다음과 같습니다:\n1. 키오스크 화면을 터치하여 메뉴를 확인합니다.\n2. 주문할 메뉴를 선택합니다.\n3. 원하는 옵션(수량, 크기 등)을 선택합니다.\n4. 장바구니에 담거나 바로 결제를 진행합니다.\n5. '결제하기'를 누릅니다.\n6. 주문 정보를 다시 한번 확인합니다.\n7. 매장에서 드실지('매장'), 가져가실지('포장') 선택합니다.\n8. 결제 방법을 선택합니다(카드, 간편결제 등).\n9. 카드 결제 시: 카드 투입구에 카드를 꽂거나(IC칩 방향 확인), 카드 대는 곳에 카드를 대세요.\n10. 간편결제(삼성페이, 카카오페이 등): 화면 안내에 따라 휴대폰을 특정 위치에 대거나 QR코드를 스캔하세요.\n11. 결제가 완료되면 영수증과 주문 번호를 받습니다.\n\n팁: 잘못 눌렀을 경우 '취소' 또는 '이전' 버튼을 찾아 누르세요. 화면의 글씨가 작다면 직원에게 도움을 요청해도 좋습니다.`
                },
                {
                    keywords: ['스마트폰', '휴대폰', '핸드폰', '어플', '앱', '사용법'],
                    answer: `스마트폰은 전화, 문자 메시지 외에도 인터넷 검색, 사진 촬영, 길 찾기(지도), 다양한 앱(어플) 사용 등 많은 기능을 제공합니다.\n\n기본적인 사용법:\n- 화면 켜기/끄기: 옆면 또는 뒷면의 전원 버튼을 짧게 누릅니다.\n- 앱 실행: 화면에서 원하는 앱 아이콘을 손가락으로 가볍게 누릅니다(터치).\n- 뒤로 가기: 보통 화면 하단에 있는 '<' 모양 버튼이나, 화면 가장자리를 안쪽으로 밀면 이전 화면으로 돌아갑니다.\n- 홈 화면 가기: 화면 하단의 동그라미(○) 또는 네모(□) 모양 버튼을 누르면 어떤 화면에서든 기본 화면으로 돌아옵니다.\n- 앱 종료: 홈 화면 버튼 옆의 줄 세 개(≡) 또는 네모 두 개 겹친 모양 버튼을 누르면 최근 사용한 앱 목록이 나옵니다. 여기서 앱을 위로 밀거나 '모두 닫기'를 누르면 종료됩니다.\n\n궁금한 기능(예: '카카오톡 사용법', '사진 보내는 법')을 구체적으로 질문해주시면 더 자세히 알려드릴 수 있습니다.`
                },
                {
                    keywords: ['병원 예약', '진료 예약', '병원 접수'],
                    answer: `병원 예약은 여러 가지 방법으로 할 수 있습니다.\n\n1. 전화 예약: 병원 대표 전화번호로 전화하여 원하는 날짜와 시간을 말씀하시고 예약합니다.\n2. 인터넷 예약: 병원 홈페이지나 건강 관련 포털 사이트(예: 똑닥)에서 온라인으로 예약합니다.\n3. 병원 앱 예약: 해당 병원에서 자체 앱을 운영하는 경우, 앱을 설치하여 예약할 수 있습니다.\n4. 직접 방문 예약: 병원에 직접 방문하여 다음 진료를 예약합니다.\n\n예약 시 필요한 정보:\n- 본인 이름과 주민등록번호 또는 환자 등록번호\n- 원하는 진료과 및 의사 이름 (선택 사항)\n- 원하는 날짜와 시간대\n- 연락 가능한 전화번호\n\n예약 후에는 예약 날짜와 시간을 잘 기억해두시고, 변경이나 취소가 필요하면 미리 병원에 연락하는 것이 좋습니다.`
                },
                {
                    keywords: ['버스', '지하철', '대중교통', '교통카드'],
                    answer: `버스나 지하철 등 대중교통 이용 시 교통카드를 사용하면 편리합니다.\n\n- 교통카드 종류: 선불카드(미리 돈을 충전해서 사용), 후불카드(신용카드/체크카드에 교통 기능 추가), 모바일 교통카드(스마트폰 앱 이용)\n- 버스 탈 때: 앞문으로 타면서 카드 단말기에 카드를 가볍게 대면 '삑' 소리와 함께 요금이 결제됩니다.\n- 버스 내릴 때: 뒷문으로 내리면서 카드 단말기에 카드를 다시 대면 환승 할인을 받을 수 있습니다. (환승 안 하면 안 찍어도 됩니다)\n- 지하철 탈 때: 개찰구 카드 대는 곳에 카드를 대면 문이 열립니다.\n- 지하철 내릴 때: 나가는 개찰구 카드 대는 곳에 카드를 대면 문이 열립니다. (거리에 따라 추가 요금이 발생할 수 있습니다)\n\n잔액 확인: 버스/지하철 단말기, 편의점, 은행 ATM, 지하철역 충전기 등에서 잔액을 확인할 수 있습니다. (선불카드)\n충전: 편의점, 지하철역 충전기 등에서 현금으로 충전할 수 있습니다. (선불카드)`
                },
                {
                    keywords: [], // 어떤 키워드에도 해당하지 않을 때의 기본 답변
                    answer: "죄송합니다. 질문을 명확히 이해하지 못했습니다. 조금 더 구체적으로 질문해주시거나 다른 방식으로 질문해주시겠어요?"
                }
                
                 답변했을떄 마지막에는 꼭 "청년에게 물어볼까요?" 를 출력해주세요.
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
        # uploads 디렉토리가 없으면 생성
        os.makedirs("uploads", exist_ok=True)
        
        # 파일 경로 생성
        filename = f"tts_{uuid.uuid4()}.mp3"
        filepath = os.path.join("uploads", filename)
        
        # TTS 생성
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3",
            speed=1.0,
        )
        
        # 파일 저장
        with open(filepath, "wb") as f:
            f.write(await response.aread())
            
        # 파일이 실제로 생성되었는지 확인
        if not os.path.exists(filepath):
            raise Exception("TTS 파일 생성 실패")
            
        return filepath
        
    except Exception as e:
        print(f"OpenAI TTS 오류: {str(e)}")
        raise e 