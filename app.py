from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
import uvicorn
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
from utils.whisper_service import set_whisper_model, transcribe_audio
from utils.openai_service import generate_response, generate_tts
from utils.mongo_service import save_conversation, get_conversation_history

app = FastAPI(title="음성 챗봇 API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버 시작 시 Whisper 모델 로딩
@app.on_event("startup")
async def startup_event():
    print("Whisper 모델 로딩 중...")
    import whisper
    model = whisper.load_model("base")
    set_whisper_model(model)
    print("Whisper 모델 로딩 완료!")

templates = Jinja2Templates(directory="templates")

# 정적 파일 제공
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def transcribe_audio_route(audio_file: UploadFile = File(...)):
    if not audio_file.filename.endswith('.wav'):
        raise HTTPException(
            status_code=400,
            detail="WAV 파일만 지원됩니다."
        )
        
    temp_file_path = f"uploads/{uuid.uuid4()}.wav"
    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await audio_file.read())
        
        transcription = await transcribe_audio(temp_file_path)
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/chat")
async def chat_endpoint(
    request_data: Dict[str, Any] = Body(...)
):
    try:
        message = request_data.get("message")
        conversation_id = request_data.get("conversation_id")
        
        if not message:
            raise HTTPException(status_code=400, detail="메시지가 없습니다.")
        
        # GPT를 사용하여 응답 생성
        response = await generate_response(message)
        
        # TTS 변환
        tts_path = await generate_tts(response)
        
        # 새 대화 ID 생성 또는 기존 ID 사용
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # MongoDB에 대화 저장
        timestamp = datetime.utcnow()
        await save_conversation(conversation_id, message, response, timestamp)
        
        return {
            "response": response,
            "tts_url": f"/{tts_path}",
            "conversation_id": conversation_id
        }
    except Exception as e:
        print(f"챗봇 응답 오류: {str(e)}")  # 디버깅용 로그
        raise HTTPException(status_code=500, detail=f"챗봇 응답 오류: {str(e)}")

@app.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    try:
        history = await get_conversation_history(conversation_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대화 기록 조회 오류: {str(e)}")

@app.post("/delete-tts")
async def delete_tts(request: Request):
    try:
        data = await request.json()
        tts_path = data.get("tts_path")
        
        if not tts_path:
            return {"result": "no_path_provided"}
            
        # 경로에서 파일명만 추출
        filename = os.path.basename(tts_path)
        full_path = os.path.join("uploads", filename)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"TTS 파일 삭제 성공: {full_path}")  # 디버깅용 로그
            return {"result": "deleted"}
        else:
            print(f"TTS 파일을 찾을 수 없음: {full_path}")  # 디버깅용 로그
            return {"result": "not_found"}
    except Exception as e:
        print(f"TTS 파일 삭제 오류: {str(e)}")  # 디버깅용 로그
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/favicon.ico')
async def favicon():
    return {"status": "no favicon"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)