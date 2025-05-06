import whisper
import torch
import numpy as np
import os
from typing import Optional
import re
from fastapi import HTTPException

# 전역 변수로 Whisper 모델 선언
whisper_model = None

def set_whisper_model(model):
    """서버 시작 시 로드된 모델을 설정하는 함수"""
    global whisper_model
    whisper_model = model

async def transcribe_audio(audio_file_path: str) -> str:
    """
    오디오 파일을 텍스트로 변환하는 함수
    
    Args:
        audio_file_path (str): 오디오 파일 경로
        
    Returns:
        str: 변환된 텍스트
        
    Raises:
        HTTPException: 모델이 로드되지 않았거나 변환 중 오류 발생 시
    """
    if whisper_model is None:
        raise HTTPException(
            status_code=500,
            detail="Whisper 모델이 로드되지 않았습니다."
        )
    
    try:
        # 로드된 모델로 음성 변환
        result = whisper_model.transcribe(
            audio_file_path,
            language="ko",
            fp16=torch.cuda.is_available(),
            temperature=0.2,
            initial_prompt="이것은 노인분들의 한국어 음성입니다. 발음이 불명확할 수 있으니 문맥을 고려하여 정확한 한국어로 변환해주세요."
        )
        
        text = result["text"].strip()
        
        # 한글 자음만 반복되는 경우 처리
        if re.fullmatch(r"[ㄱ-ㅎ\s]+", text):
            return "정확히 인식하지 못했습니다. 다시 말씀해 주세요."
            
        return text
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"음성 변환 중 오류 발생: {str(e)}"
        ) 