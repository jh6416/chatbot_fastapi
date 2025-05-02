import whisper
import torch
import numpy as np
import os
from typing import Optional
import re

# Whisper 모델 로드
model = None

async def load_model(model_name: str = "small"):
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
            fp16=torch.cuda.is_available(),
            temperature=0.2,
            initial_prompt="이것은 노인분들의 한국어 음성입니다. 발음이 불명확할 수 있으니 문맥을 고려하여 정확한 한국어로 변환해주세요."
        )
        text = result["text"].strip()
        # 한글 자음만 반복되는 경우 안내 메시지 반환
        if re.fullmatch(r"[ㄱ-ㅎ\s]+", text):
            return "정확히 인식하지 못했습니다. 다시 말씀해 주세요."
        return text
    except Exception as e:
        print(f"음성 변환 오류: {str(e)}")
        raise e 