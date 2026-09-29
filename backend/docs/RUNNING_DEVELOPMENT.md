# 러닝 기록 API 개발 기반

현재는 기능 구현 전 골격이다. README의 시작/종료, 목록/상세,
전체/주간/월간 통계 7개 경로를 유지하고 수정/삭제 2개 경로를 보완한다. 로그인하지 않으면 401,
로그인한 사용자의 유효한 요청에는 미구현을 뜻하는 501을 반환한다.
기록 저장이나 통계 계산이 완료됐다는 의미가 아니다.

## 구조

- app/api/routes/running.py: 공통 인증, 요청 검증, 기존 응답 스키마 연결.
- app/services/running.py: 기록 처리와 통계를 구현할 서비스 경계.
- app/schemas/running_record.py: PM의 기존 스키마 재사용.
- app/models/running_record.py: PM의 기존 모델 유지.
- tests/test_running_scaffold.py: 인증과 미구현 응답 확인.

동기 SQLAlchemy 세션에 맞춰 라우트는 def로 작성한다.
get_current_user로 인증한 사용자 ID를 서비스에 전달한다.
조회/수정/삭제에는 반드시 사용자 조건을 추가하고 신발 소유권도 검사해야 한다.
인증 연결만으로 소유권 검사까지 구현된 것은 아니다.

## 구현 전에 맞출 계약

1. README의 start/end 방식과 ROLES.md의 완료 기록 POST 방식 중 최종 계약.
2. 시작 세션 저장 방법과 종료 요청 본문. 현재 모델은 종료 시각도 필수다.
3. 분 단위 정수 유지 여부, 초 단위 지원, 일시정지 시간 처리.
4. 주/월 경계의 시간대, 집계 키, 기록이 없는 기간의 응답.
5. 수정 허용 필드 및 재전송 중복 방지 식별자.

목록은 skip >= 0, 1 <= limit <= 100이며 상세 ID는 양수다.
조회와 통계 응답은 기존 Python 스키마 및 Android 초안 형태를 따른다.
start 응답과 end 요청의 새 필드는 아직 확정하지 않았다.
PUT/DELETE /api/running/{record_id}는 초안과 ROLES.md의 수정/삭제 요구를 보완한다.
PUT은 기존 RunningRecordUpdate 필드만 받으며 생략은 유지, null은 비우는 계약이다.
알 수 없는 필드와 0 이하 shoe_id는 거부한다. 아직 실제 변경은 수행하지 않는다.

## 후속 구현

저장/조회 → 수정/삭제와 신발 누적 거리·횟수 → 통계 순서로 구현한다.
기록과 신발 통계는 한 트랜잭션에서 변경하며 동시 요청과 중복 요청을 고려한다.
날씨와 AI 추천의 전체 골격은 BACKEND2_STRUCTURE.md에 정리한다.

## 로컬 검증

backend 폴더에서 실행:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

테스트는 팀원의 격리된 SQLite fixture와 테스트 JWT를 사용한다.
PostgreSQL, 실제 서버, Android 연동 검증은 별도로 필요하다.
