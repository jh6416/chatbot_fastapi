from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
import uvicorn
from typing import Optional
import uuid
from datetime import datetime
from utils.whisper_service import transcribe_audio
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

templates = Jinja2Templates(directory="templates")

# 정적 파일 제공
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def transcribe_audio_route(audio_file: UploadFile = File(...)):
    # 임시 파일로 저장
    temp_file_path = f"uploads/{uuid.uuid4()}.wav"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await audio_file.read())
    
    try:
        # Whisper를 사용하여 음성을 텍스트로 변환
        transcription = await transcribe_audio(temp_file_path)
        
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        return {"transcription": transcription}
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"음성 변환 오류: {str(e)}")

@app.post("/chat")
async def chat_endpoint(
    message: str = Form(...),
    conversation_id: Optional[str] = Form(None)
):
    try:
        # GPT를 사용하여 응답 생성
        response = await generate_response(message)
        
        # 새 대화 ID 생성 또는 기존 ID 사용
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # MongoDB에 대화 저장
        timestamp = datetime.utcnow()
        await save_conversation(conversation_id, message, response, timestamp)
        
        return {
            "response": response,
            "conversation_id": conversation_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 응답 오류: {str(e)}")

@app.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    try:
        history = await get_conversation_history(conversation_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대화 기록 조회 오류: {str(e)}")

@app.post("/tts")
async def tts_endpoint(text: str = Form(...)):
    try:
        tts_path = await generate_tts(text)
        return {"tts_url": f"/{tts_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS 변환 오류: {str(e)}")

@app.post("/delete-tts")
async def delete_tts(request: Request):
    data = await request.json()
    tts_path = data.get("tts_path")
    if tts_path and tts_path.startswith("static/") and os.path.exists(tts_path):
        os.remove(tts_path)
        return {"result": "deleted"}
    return {"result": "not_found"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 