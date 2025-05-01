import whisper
import torch
import numpy as np
import os
from typing import Optional

# Whisper 모델 로드
model = None

async def load_model(model_name: str = "base"):
    """Whisper 모델을 로드합니다."""
    global model
    if model is None:
        model = whisper.load_model(model_name)
    return model

async def transcribe_audio(audio_path: str, language: Optional[str] = "ko") -> str:
    """
    오디오 파일을 텍스트로 변환합니다.
    
    Args:
        audio_path: 오디오 파일 경로
        language: 언어 코드 (기본값: 한국어)
        
    Returns:
        변환된 텍스트
    """
    # 모델 로드
    model = await load_model()
    
    # 오디오 파일 변환
    try:
        result = model.transcribe(
            audio_path,
            language=language,
            fp16=torch.cuda.is_available()
        )
        return result["text"]
    except Exception as e:
        print(f"음성 변환 오류: {str(e)}")
        raise e 