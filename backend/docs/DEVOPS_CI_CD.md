# 🚀 DevOps & CI/CD 파이프라인 가이드

**DevOps&QA 팀을 위한 완전한 CI/CD 설정 가이드**

---

## 📋 목차

1. [개요](#개요)
2. [GitHub Actions 설정](#github-actions-설정)
3. [워크플로우 상세 설명](#워크플로우-상세-설명)
4. [실행 방법](#실행-방법)
5. [모니터링 및 트러블슈팅](#모니터링-및-트러블슈팅)

---

## 개요

### CI/CD란?

```
📝 개발자가 코드 작성
    ↓
🔄 GitHub에 Push/PR 생성
    ↓
🤖 GitHub Actions 자동 실행 (CI - Continuous Integration)
    ├─ 코드 스타일 검사 (lint)
    ├─ 자동 테스트 실행 (test)
    └─ 코드 커버리지 확인
    ↓
✅ 모든 검사 통과?
    ↓
📦 Docker 이미지 빌드 (CD - Continuous Deployment)
    ↓
🚀 자동 배포 (Production)
```

### 필요한 파일 구조

```
RunTrack/
├─ .github/
│  └─ workflows/
│     ├─ lint.yml ...................... ✅ 코드 스타일 검사
│     ├─ test.yml ...................... ✅ 테스트 실행
│     └─ deploy.yml .................... ✅ 배포 자동화
├─ backend/
│  ├─ Dockerfile ...................... ✅ Docker 이미지 정의
│  ├─ requirements.txt ................ ✅ Python 의존성
│  └─ app/
│     └─ main.py ...................... ✅ FastAPI 앱
├─ docker-compose.yml ................. ✅ 로컬 개발 환경
└─ README.md
```

---

## GitHub Actions 설정

### 1️⃣ `.github/workflows/lint.yml` - 코드 스타일 검사

**목적:** 모든 코드가 팀의 코딩 스타일을 따르는지 확인

**실행 시점:**
- `git push` 할 때마다
- Pull Request 생성 시

**검사 항목:**
- 라인 길이 (최대 100자)
- 들여쓰기 (4칸)
- 공백 규칙
- import 정렬

### 2️⃣ `.github/workflows/test.yml` - 자동 테스트

**목적:** 모든 기능이 정상 작동하는지 자동으로 테스트

**실행 시점:**
- `git push` 할 때마다
- Pull Request 생성 시

**검사 항목:**
- pytest로 모든 테스트 실행
- 테스트 커버리지 측정 (목표: 80%+)
- 데이터베이스 마이그레이션 테스트

**테스트 환경:**
- PostgreSQL 15 (테스트 DB)
- Redis (캐시 테스트)
- Python 3.11

### 3️⃣ `.github/workflows/deploy.yml` - 자동 배포

**목적:** main 브랜치에 머지되면 자동으로 production 배포

**실행 시점:**
- `main` 브랜치에만 머지될 때
- 수동 트리거 가능 (필요시)

**배포 단계:**
1. Docker 이미지 빌드
2. Docker Hub/Registry에 푸시
3. Production 서버에 배포
4. 헬스체크 (서비스가 정상인지 확인)

---

## 워크플로우 상세 설명

### `lint.yml` 상세 분석

```yaml
name: Lint Check              # 워크플로우 이름
on: [push, pull_request]      # 언제 실행할 것인가

jobs:
  lint:
    runs-on: ubuntu-latest    # 실행 환경 (Linux)
    steps:                     # 실행할 단계들
      - uses: actions/checkout@v3          # 코드 가져오기
      - name: Run flake8                   # 이름
        run: |                             # 실행 명령어
          pip install flake8
          flake8 backend/app --max-line-length=100
```

**Flake8이 검사하는 것:**
```
E999: Syntax errors
E901: Indentation contains mixed spaces and tabs
E225: Missing whitespace around operator
W291: Trailing whitespace
W292: No newline at end of file
```

### `test.yml` 상세 분석

```yaml
name: Run Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:                # 백그라운드에서 실행할 서비스
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
      redis:
        image: redis:latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run pytest
        run: cd backend && pytest --cov=app tests/
```

**pytest가 하는 것:**
```
✅ backend/tests/ 폴더의 모든 테스트 파일 실행
✅ 각 테스트 함수 실행 (test_*.py, *_test.py)
✅ 성공/실패 결과 리포트
✅ 코드 커버리지 계산 (--cov=app)
```

### `deploy.yml` 상세 분석

```yaml
name: Deploy
on:
  push:
    branches: [main]          # main 브랜치에만 실행

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t runtrack-backend:latest ./backend
      - name: Push to registry
        run: docker push runtrack-backend:latest
      - name: Deploy to production
        run: |
          # 원격 서버에 SSH로 접속해서 배포
          # 또는 Kubernetes, AWS, GCP 등으로 배포
```

---

## 실행 방법

### 1️⃣ 로컬에서 검사하기 (선택사항)

배포 전에 로컬에서 먼저 확인:

```bash
# Flake8 검사
cd backend
pip install flake8
flake8 app --max-line-length=100

# 테스트 실행
pip install pytest pytest-asyncio pytest-cov
pytest --cov=app tests/
```

### 2️⃣ GitHub에서 자동 실행

**상황 1: 코드 푸시**
```bash
git add .
git commit -m "feat: Add new feature"
git push origin feature/my-feature
# → GitHub Actions 자동 시작
# → lint.yml + test.yml 실행
```

**상황 2: Pull Request 생성**
```bash
# GitHub에서 PR 생성
# → lint.yml + test.yml 자동 실행
# → 성공하면 "All checks passed" ✓
# → 실패하면 빨간색 X 표시
```

**상황 3: main에 머지**
```bash
# PR을 main에 머지
# → lint.yml + test.yml + deploy.yml 모두 실행
# → 배포 완료!
```

### 3️⃣ 워크플로우 상태 확인

```
GitHub 저장소 → Actions 탭 → 실행 중인 워크플로우 확인
```

**상태:**
- 🟡 In progress: 실행 중
- ✅ Success: 성공
- ❌ Failed: 실패

---

## 모니터링 및 트러블슈팅

### 🔍 문제 진단

**Q1: lint 실패**
```
Error: Line too long (115 > 100 characters)

해결: 코드의 너무 긴 라인을 100자 이하로 줄이기
```

**Q2: test 실패**
```
FAILED backend/tests/test_users.py::test_register - AssertionError

해결:
1. 로컬에서 `pytest` 실행해서 테스트 실패 원인 파악
2. 코드 수정
3. 다시 `git push`
```

**Q3: deploy 실패**
```
Error: Docker push denied

해결:
1. Docker Registry 인증 정보 확인 (GitHub Secrets)
2. 토큰 만료되었는지 확인
3. 권한 확인
```

### 📊 성공 기준

| 검사 | 성공 기준 |
|------|----------|
| Lint | 모든 flake8 규칙 통과 |
| Test | pytest 모든 테스트 통과 |
| Coverage | 80% 이상 (선택사항) |
| Deploy | Docker 이미지 성공적으로 빌드 및 배포 |

### 🔧 GitHub Secrets 설정

Production 배포 시 필요한 민감한 정보:

```
Settings → Secrets and variables → Actions
→ New repository secret

필요한 Secrets:
- DOCKER_REGISTRY_URL (Docker Hub URL)
- DOCKER_USERNAME (Docker 계정)
- DOCKER_PASSWORD (Docker 토큰)
- SSH_PRIVATE_KEY (배포 서버 접근용)
- DATABASE_URL (Production DB)
```

---

## 📝 주간 체크리스트 (DevOps&QA 팀)

### Week 1 (기초 설정)
```
[ ] Dockerfile 작성
[ ] docker-compose.yml 작성
[ ] .github/workflows/ 폴더 생성
[ ] lint.yml 작성 및 테스트
[ ] test.yml 작성 및 테스트
```

### Week 2 (고급 설정)
```
[ ] deploy.yml 작성
[ ] GitHub Secrets 설정
[ ] Production 배포 테스트
[ ] 모니터링 대시보드 설정
```

### Week 3+ (유지보수)
```
[ ] CI/CD 성공률 모니터링
[ ] 실패 원인 분석 및 해결
[ ] 성능 최적화
[ ] 보안 취약점 스캔
```

---

## 📞 참고 자료

- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Flake8 규칙](https://www.flake8rules.com/)
- [pytest 가이드](https://docs.pytest.org/)
- [Docker 공식 문서](https://docs.docker.com/)

---

**다음 단계:** [DOCKER_SETUP.md](DOCKER_SETUP.md)에서 Docker 설정 방법을 알아보세요! 🐳
