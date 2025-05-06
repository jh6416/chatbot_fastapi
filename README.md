# FastAPI 음성 챗봇 0506

MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=chatbot_db
MONGODB_COLLECTION=conversations 
Whisper, OpenAI GPT 및 MongoDB를 활용한 음성 인식 챗봇 애플리케이션입니다.

## 기능

- Whisper를 사용한 음성-텍스트 변환
- OpenAI GPT를 사용한 자연어 응답 생성
- MongoDB를 사용한 대화 내역 저장
- 사용자 친화적인 웹 인터페이스

## 설치 및 실행 방법

### 필수 조건

- Python 3.9 이상
- MongoDB 설치 및 실행
- OpenAI API 키

### 설치

1. 저장소를 클론합니다:
```bash
git clone [저장소 URL]
cd [프로젝트 폴더]
```

2. 가상 환경을 생성하고 활성화합니다:
```bash
python -m venv venv
source venv/bin/activate  # 리눅스/맥
# 또는
venv\Scripts\activate  # 윈도우
```

3. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
```bash
cp env.example .env
```
`.env` 파일을 열고 필요한 정보를 입력합니다.

### 실행

애플리케이션을 시작합니다:
```bash
python app.py
```

또는 Uvicorn을 직접 사용:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## AWS EC2 배포

1. EC2 인스턴스 준비
   - Python 3.9 이상 설치
   - 필요한 방화벽 포트 열기 (기본: 8000)

2. 프로젝트 코드 배포:
```bash
git clone [저장소 URL]
cd [프로젝트 폴더]
pip install -r requirements.txt
```

3. 환경 변수 설정:
```bash
cp env.example .env
nano .env  # 필요한 정보 입력
```

4. 애플리케이션 실행:
```bash
nohup python app.py > app.log 2>&1 &
```

## 프로젝트 구조

```
├── app.py                  # FastAPI 메인 애플리케이션
├── utils/
│   ├── __init__.py
│   ├── whisper_service.py  # Whisper 음성 변환 서비스
│   ├── openai_service.py   # OpenAI GPT 서비스
│   └── mongo_service.py    # MongoDB 연결 및 데이터 관리
├── templates/
│   └── index.html          # 웹 인터페이스 템플릿
├── static/                 # 정적 파일 (CSS, JS 등)
├── uploads/                # 업로드된 오디오 파일 임시 저장
├── requirements.txt        # 필요한 패키지 목록
└── .env                    # 환경 변수 파일
```

## 라이선스

MIT 
