# 🐳 Docker 설정 가이드

**DevOps&QA 팀을 위한 Docker 이미지 및 Compose 설정**

---

## 📋 목차

1. [개요](#개요)
2. [Dockerfile 작성](#dockerfile-작성)
3. [docker-compose.yml 작성](#docker-composeyml-작성)
4. [실행 방법](#실행-방법)
5. [명령어 레퍼런스](#명령어-레퍼런스)

---

## 개요

### Docker란?

```
Docker = "코드가 실행되는 컨테이너"

개발자 PC (Windows)
    ↓
Docker 컨테이너 (Linux 환경)
    ├─ Python 3.11
    ├─ FastAPI
    ├─ PostgreSQL
    └─ Redis
    ↓
Production 서버 (Linux)
    ↓
"내 PC에서 되는데 서버에서 안 됨" 문제 해결! ✅
```

### 왜 필요한가?

| 문제 | Docker 해결책 |
|------|--------------|
| "내 PC에서는 되는데..." | 모든 개발자/서버에 동일한 환경 제공 |
| 의존성 충돌 | 각 프로젝트마다 독립적인 환경 |
| 배포 복잡성 | 컨테이너 한두 개만 배포하면 됨 |
| 확장성 | 같은 이미지 여러 개 동시 실행 가능 |

---

## Dockerfile 작성

### 위치

```
backend/Dockerfile
```

### 전체 코드

```dockerfile
# Step 1: Base Image (기반이 되는 이미지)
FROM python:3.11-slim

# Step 2: 작업 디렉토리 설정
WORKDIR /app

# Step 3: 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: 소스코드 복사
COPY . .

# Step 5: 환경변수 설정 (선택)
ENV PYTHONUNBUFFERED=1

# Step 6: 포트 노출
EXPOSE 8000

# Step 7: 실행 명령어
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 상세 설명

#### 1️⃣ Base Image
```dockerfile
FROM python:3.11-slim
```
- `python:3.11` = Python 3.11이 설치된 이미지
- `slim` = 불필요한 패키지 제거한 가벼운 버전
- 대안: `python:3.11-alpine` (더 가벼움, 약 40MB)

#### 2️⃣ 작업 디렉토리
```dockerfile
WORKDIR /app
```
- 컨테이너 내부의 작업 폴더를 `/app`으로 설정
- 이후 모든 명령어는 `/app`에서 실행됨

#### 3️⃣ 의존성 설치
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
- `COPY requirements.txt .` = PC의 `requirements.txt`를 컨테이너로 복사
- `RUN pip install` = 컨테이너에서 패키지 설치
- `--no-cache-dir` = 설치 후 캐시 삭제해서 이미지 크기 감소

#### 4️⃣ 소스코드 복사
```dockerfile
COPY . .
```
- 전체 `backend/` 폴더를 컨테이너 `/app`으로 복사

#### 5️⃣ 환경변수
```dockerfile
ENV PYTHONUNBUFFERED=1
```
- Python이 버퍼링 없이 로그를 즉시 출력
- Docker 로그를 실시간으로 볼 수 있음

#### 6️⃣ 포트 노출
```dockerfile
EXPOSE 8000
```
- 외부에서 포트 8000으로 접근할 수 있게 설정
- 실제 포트 매핑은 실행 시 `-p` 옵션으로 함

#### 7️⃣ 실행 명령어
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- 컨테이너 시작 시 자동으로 실행되는 명령어
- `--host 0.0.0.0` = 외부의 모든 IP에서 접근 가능

### 빌드 방법

```bash
cd backend
docker build -t runtrack-backend:1.0 .
```

**설명:**
- `docker build` = Dockerfile로부터 이미지 빌드
- `-t runtrack-backend:1.0` = 이미지 이름:태그
- `.` = 현재 디렉토리의 Dockerfile 사용

### 실행 방법 (단독)

```bash
docker run -p 8000:8000 runtrack-backend:1.0
```

**설명:**
- `-p 8000:8000` = 호스트의 포트 8000을 컨테이너의 포트 8000으로 매핑
- 브라우저에서 `http://localhost:8000`으로 접근 가능

---

## docker-compose.yml 작성

### 위치

```
RunTrack/docker-compose.yml  (root 폴더)
```

### 전체 코드

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: runtrack-backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/runtrack
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    container_name: runtrack-db
    environment:
      POSTGRES_DB: runtrack
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    container_name: runtrack-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 상세 설명

#### 📦 `backend` 서비스
```yaml
backend:
  build: ./backend                           # Dockerfile 위치
  container_name: runtrack-backend           # 컨테이너 이름
  ports:
    - "8000:8000"                            # 포트 매핑
  environment:                               # 환경변수
    DATABASE_URL: postgresql://...
    REDIS_URL: redis://redis:6379
  depends_on:                                # 선행 서비스
    - db
    - redis
  volumes:                                   # 파일 공유
    - ./backend:/app                         # 로컬 수정 → 컨테이너 반영
  command: uvicorn ... --reload              # 재시작 자동감지
```

**주요 설정:**
- `--reload` = 파일 수정하면 서버 자동 재시작 (개발용)
- `environment`의 `redis://redis:6379`에서 `redis`는 다른 컨테이너의 이름

#### 🗄️ `db` (PostgreSQL) 서비스
```yaml
db:
  image: postgres:15                         # 기존 이미지 사용
  environment:
    POSTGRES_DB: runtrack                    # DB 이름
    POSTGRES_USER: user                      # 사용자명
    POSTGRES_PASSWORD: password              # 비밀번호
  volumes:
    - postgres_data:/var/lib/postgresql/data # 데이터 영구 저장
  healthcheck:                               # 서비스 정상 여부 확인
    test: ["CMD-SHELL", "pg_isready -U user"]
```

**주의:**
- `POSTGRES_PASSWORD: password`는 개발용입니다!
- Production에서는 안전한 비밀번호 사용 필수

#### 🔴 `redis` 서비스
```yaml
redis:
  image: redis:7                             # Redis 7 버전
  ports:
    - "6379:6379"                            # Redis 기본 포트
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]       # Redis 정상 작동 확인
```

#### 💾 Volume (데이터 영구 저장)
```yaml
volumes:
  postgres_data:                             # 생성할 volume 이름
```

**역할:**
- 컨테이너를 삭제해도 데이터 유지
- 모든 컨테이너가 공유 가능
- 호스트 디스크의 특정 위치에 저장

---

## 실행 방법

### 1️⃣ 첫 실행 (모든 서비스 시작)

```bash
cd RunTrack
docker-compose up
```

**출력:**
```
runtrack-db       | database system is ready to accept connections
runtrack-redis    | Ready to accept connections
runtrack-backend  | Uvicorn running on http://0.0.0.0:8000
```

**테스트:**
```bash
# 다른 터미널에서
curl http://localhost:8000/docs
```

### 2️⃣ 백그라운드에서 실행

```bash
docker-compose up -d
```

- `-d` = Detached mode (터미널 다시 사용 가능)

### 3️⃣ 상태 확인

```bash
docker-compose ps
```

**출력:**
```
NAME              COMMAND                  STATUS
runtrack-backend  uvicorn app.main:app     Up 2 minutes
runtrack-db       postgres                 Up 2 minutes (healthy)
runtrack-redis    redis-server             Up 2 minutes (healthy)
```

### 4️⃣ 로그 확인

```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f db
```

### 5️⃣ 실행 중지

```bash
# 컨테이너만 중지 (데이터 유지)
docker-compose stop

# 컨테이너 제거 (데이터는 유지)
docker-compose down

# 컨테이너 + 데이터 모두 삭제 (주의!)
docker-compose down -v
```

### 6️⃣ 재시작

```bash
docker-compose restart
```

---

## 명령어 레퍼런스

### 빌드 관련

```bash
# 이미지 빌드
docker build -t 이미지이름:태그 .

# 이미지 목록 보기
docker images

# 이미지 삭제
docker rmi 이미지이름:태그

# 이미지 강제 삭제
docker rmi -f 이미지이름:태그
```

### 컨테이너 실행

```bash
# 포트 매핑하며 실행
docker run -p 8000:8000 이미지이름

# 환경변수 설정하며 실행
docker run -e DATABASE_URL=... 이미지이름

# 볼륨 마운트하며 실행
docker run -v 로컬경로:/app 이미지이름

# 백그라운드 실행
docker run -d 이미지이름
```

### 컨테이너 관리

```bash
# 실행 중인 컨테이너 목록
docker ps

# 모든 컨테이너 목록 (종료된 것 포함)
docker ps -a

# 컨테이너 로그 보기
docker logs -f 컨테이너이름

# 컨테이너 내부에서 명령어 실행
docker exec -it 컨테이너이름 bash

# 컨테이너 중지
docker stop 컨테이너이름

# 컨테이너 삭제
docker rm 컨테이너이름
```

### Compose 명령어

```bash
# 모든 서비스 시작
docker-compose up

# 백그라운드 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 보기
docker-compose logs -f [서비스명]

# 서비스 재시작
docker-compose restart [서비스명]

# 모든 서비스 중지
docker-compose stop

# 모든 서비스 제거
docker-compose down

# 서비스 및 볼륨 제거
docker-compose down -v

# 이미지 재빌드하며 실행
docker-compose up --build
```

---

## 📝 주간 체크리스트

### Week 1 (Setup)
```
[ ] Dockerfile 작성 (backend/Dockerfile)
[ ] docker-compose.yml 작성 (root 폴더)
[ ] docker-compose up -d 실행
[ ] http://localhost:8000/docs 접근 확인
[ ] docker-compose logs -f 로그 확인
```

### Week 2 (Testing)
```
[ ] Backend 수정 → 자동 재시작 확인 (--reload)
[ ] Database 데이터 생성 및 조회 테스트
[ ] Redis 캐시 작동 확인
[ ] 컨테이너 재시작 후 데이터 유지 확인
```

### Week 3+ (Production)
```
[ ] Multi-stage build 적용 (이미지 크기 최적화)
[ ] Health check 모니터링
[ ] 로그 수집 및 분석
[ ] 성능 최적화 (메모리 제한 등)
```

---

## 🔧 트러블슈팅

### Q1: "Port 8000 is already allocated"
```bash
# 해결 1: 다른 포트 사용
docker run -p 8001:8000 이미지이름

# 해결 2: 기존 컨테이너 중지
docker stop 컨테이너이름

# 해결 3: 강제 종료
docker rm -f 컨테이너이름
```

### Q2: "Connection refused" (DB 연결 불가)
```bash
# 확인: DB 서비스 실행 중?
docker-compose ps

# 확인: 컨테이너 로그
docker-compose logs db

# 해결: depends_on으로 순서 지정
depends_on:
  - db      # backend 시작 전에 db 시작
```

### Q3: "database is being accessed by other users"
```bash
# 기존 연결 종료 후 재시작
docker-compose restart db
```

### Q4: 데이터가 사라짐 (컨테이너 삭제)
```bash
# 주의!
docker-compose down -v       # ❌ 데이터 삭제됨

# 대신 사용
docker-compose stop          # ✅ 데이터 유지
docker-compose down          # ✅ 데이터 유지 (볼륨 유지)
```

---

## 📞 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 가이드](https://docs.docker.com/compose/)
- [Best Practices for Python Docker Images](https://docs.docker.com/language/python/build-images/)

---

**다음 단계:** CI/CD 파이프라인 설정은 [DEVOPS_CI_CD.md](DEVOPS_CI_CD.md)를 참고하세요! 🚀
