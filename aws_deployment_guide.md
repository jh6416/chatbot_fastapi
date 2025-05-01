# AWS EC2 배포 가이드

이 가이드는 FastAPI 음성 챗봇을 AWS EC2 인스턴스에 배포하는 방법을 설명합니다.

## 1. EC2 인스턴스 준비

### 1.1 EC2 인스턴스 생성
1. AWS 콘솔에 로그인하고 EC2 서비스로 이동합니다.
2. "인스턴스 시작" 버튼을 클릭합니다.
3. 인스턴스 유형은 최소 `t2.medium` 이상을 권장합니다 (Whisper 모델 실행 시 메모리가 필요함).
4. 보안 그룹 설정에서 다음 포트를 열어줍니다:
   - SSH (22): 관리용
   - HTTP (80): 웹 트래픽
   - HTTPS (443): 보안 웹 트래픽
   - TCP (8000): FastAPI 서버 (또는 선택한 포트)
5. 인스턴스를 시작하고 SSH 키 페어를 다운로드합니다.

### 1.2 기본 설정

인스턴스에 SSH로 연결:
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

시스템 업데이트:
```bash
sudo apt update && sudo apt upgrade -y
```

필수 패키지 설치:
```bash
sudo apt install -y python3-pip python3-venv git ffmpeg
```

## 2. 애플리케이션 배포

### 2.1 코드 가져오기
```bash
git clone https://your-repository-url.git
cd FastAPI_whisper
```

### 2.2 가상 환경 설정
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 환경 설정
```bash
cp env.example .env
nano .env
```

.env 파일에 다음 정보를 입력합니다:
```
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=chatbot_db
MONGODB_COLLECTION=conversations
```

### 2.4 MongoDB 설치 (로컬에서 실행하는 경우)

```bash
# MongoDB 공개 키 추가
sudo apt-get install gnupg curl
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor

# MongoDB 레포지토리 추가
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# 패키지 업데이트 및 MongoDB 설치
sudo apt-get update
sudo apt-get install -y mongodb-org

# MongoDB 서비스 시작
sudo systemctl start mongod
sudo systemctl enable mongod
```

## 3. 애플리케이션 실행

### 3.1 테스트 실행
```bash
python app.py
```

애플리케이션이 제대로 실행되는지 확인합니다. `Ctrl+C`로 중지합니다.

### 3.2 백그라운드에서 실행
```bash
nohup python app.py > app.log 2>&1 &
```

실행 중인 프로세스 ID는 다음 명령어로 확인할 수 있습니다:
```bash
ps aux | grep python
```

### 3.3 서비스로 실행 (권장)

systemd 서비스 파일 생성:
```bash
sudo nano /etc/systemd/system/fastapi-whisper.service
```

다음 내용을 입력:
```
[Unit]
Description=FastAPI Whisper Chatbot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/FastAPI_whisper
ExecStart=/home/ubuntu/FastAPI_whisper/venv/bin/python app.py
Restart=always
Environment="PATH=/home/ubuntu/FastAPI_whisper/venv/bin"

[Install]
WantedBy=multi-user.target
```

서비스 활성화 및 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl start fastapi-whisper
sudo systemctl enable fastapi-whisper
```

## 4. HTTPS 설정 (선택 사항)

보안 연결을 위해 Nginx와 Let's Encrypt를 사용하여 HTTPS를 설정할 수 있습니다:

```bash
# Nginx 설치
sudo apt install -y nginx

# Nginx 설정
sudo nano /etc/nginx/sites-available/fastapi-whisper
```

설정 파일 내용:
```
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

심볼릭 링크 생성 및 Nginx 재시작:
```bash
sudo ln -s /etc/nginx/sites-available/fastapi-whisper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Let's Encrypt로 SSL 인증서 발급:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 문제 해결

### 로그 확인
```bash
tail -f app.log
```

### 서비스 상태 확인
```bash
sudo systemctl status fastapi-whisper
```

### Firewall 확인
```bash
sudo ufw status
```

### 메모리 사용량 확인
```bash
free -h
```

Whisper 모델이 메모리를 많이 사용하는 경우 스왑 공간을 추가할 수 있습니다:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
``` 