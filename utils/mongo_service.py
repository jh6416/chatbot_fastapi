import os
from datetime import datetime
from typing import List, Dict, Any
import motor.motor_asyncio
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# MongoDB 연결 정보
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "chatbot_db")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "conversations")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI가 설정되지 않았습니다. .env 파일을 확인하세요.")

# MongoDB 클라이언트 초기화
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

async def save_conversation(
    conversation_id: str, 
    user_message: str, 
    bot_response: str, 
    timestamp: datetime
) -> str:
    """
    대화를 MongoDB에 저장합니다.
    
    Args:
        conversation_id: 대화 ID
        user_message: 사용자 메시지
        bot_response: 챗봇 응답
        timestamp: 타임스탬프
        
    Returns:
        저장된 대화의 ID
    """
    try:
        document = {
            "conversation_id": conversation_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": timestamp
        }
        
        result = await collection.insert_one(document)
        print(f"MongoDB 저장 성공: {result.inserted_id}")  # 디버깅용 로그
        return str(result.inserted_id)
    except Exception as e:
        print(f"MongoDB 저장 오류: {str(e)}")  # 디버깅용 로그
        raise e

async def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
    """
    특정 대화 ID에 대한 대화 기록을 조회합니다.
    
    Args:
        conversation_id: 대화 ID
        
    Returns:
        대화 기록 목록
    """
    cursor = collection.find(
        {"conversation_id": conversation_id},
        {"_id": 0}  # _id 필드는 제외
    ).sort("timestamp", 1)  # 시간순 정렬
    
    result = []
    async for document in cursor:
        # 타임스탬프를 문자열로 변환
        document["timestamp"] = document["timestamp"].isoformat()
        result.append(document)
    
    return result 