# Backend 2 전체 개발 골격

후속 작성된 README를 경로 기준으로 사용하고, 초기 업무 목록 및 ROLES.md의
수정/삭제 요구를 보완한다. 모든 기능은 아직 서비스 골격이며 실제 DB 저장,
통계 계산, OpenWeather/Gemini 호출은 구현하지 않았다.

## 경로

| 메서드 | 실제 경로 | 목적 |
| --- | --- | --- |
| POST | /api/running/start | 세션 시작 |
| POST | /api/running/{session_id}/end | 종료 및 기록 저장 |
| GET | /api/running | 기록 목록 |
| GET | /api/running/{record_id} | 기록 상세 |
| PUT | /api/running/{record_id} | 기록 수정 |
| DELETE | /api/running/{record_id} | 기록 삭제 |
| GET | /api/running/statistics/summary | 전체 통계 |
| GET | /api/running/statistics/weekly | 주간 통계 |
| GET | /api/running/statistics/monthly | 월간 통계 |
| GET | /api/weather/advice | 날씨와 러닝 조언 |
| GET | /api/weather/history | 기상 이력 |
| POST | /api/recommendations/shoes | Gemini 신발 추천 |

초기 create/list/update/delete/stats/info 경로는 중복으로 만들지 않았다.
모든 경로에 팀원의 get_current_user 인증을 적용했다. 날씨 인증도 이번 초안의
선택이다. 유효한 요청은 현재 501, 인증 실패는 401, 입력 오류는 422다.
삭제 성공 시 204는 향후 계약이며 현재는 삭제하지 않고 501을 반환한다.

## 파일과 역할

```text
app/
  api/routes/running.py           요청 검증·인증·러닝 서비스 연결
  api/routes/weather.py           날씨 요청 및 서비스 연결
  api/routes/recommendations.py   추천 요청 및 Gemini 서비스 연결
  api/ai/recommendations.py       기존 Gemini 서비스 위치 유지
  services/running.py             DB 변경·소유권·누적 거리·통계 구현 자리
  services/weather.py             OpenWeather 호출·단위 변환·조언 구현 자리
  schemas/running_record.py       기존 PM 스키마 재사용
  schemas/weather.py              날씨 응답 초안
  schemas/recommendation.py       추천 요청·응답 초안
```

외부 API 서비스는 의존성 주입으로 테스트 대역과 교체 가능하다.
API 키가 없어도 import 및 테스트할 수 있으며 실제 외부 통신은 하지 않는다.
테스트에서 반환하는 날씨와 신발은 테스트용 데이터로 운영 코드에 포함하지 않는다.

## 요청·응답 초안

- 러닝: 시작 응답 및 종료 요청 본문은 세션 저장 방식을 정한 뒤 추가한다.
  기존 DB 모델에 맞춰 분 단위 필드를 유지하며 초 단위로 임의 변경하지 않았다.
- 수정: title, description, shoe_id, feeling, notes만 허용한다.
  기록·신발 소유권 검사는 서비스 실제 구현 단계에서 추가해야 한다.
- 날씨: latitude [-90,90], longitude [-180,180]. 이력 days 기본 7,
  범위 1~30은 로컬 요청 제한일 뿐 외부 공급자의 지원 범위를 보장하지 않는다.
  응답은 섭씨, 습도 %, 풍속 km/h로 단위를 명시한다. UV/추천 점수는 선택값이다.
  Python 응답은 snake_case 초안이며 기존 Android camelCase 모델과 매핑 합의가 필요하다.
- 추천: 기존 서비스 인수에 맞춰 weight_kg, height_cm, foot_size, foot_width,
  arch_type, running_style, budget_won을 요청에서 받는다. preferred_brands는 선택이다.
  현재는 저장된 프로필에서 자동으로 가져오지 않는다. 요청에 사용자 ID를 받지 않는다.
  응답은 recommendations 배열의 brand, model, reason으로 정의했다.
  가격·재고를 AI가 확인한 사실처럼 반환하지 않는다.

## 실제 구현 시 남은 일

1. PM과 세션 상태/종료 필수 필드 및 마이그레이션 설계.
2. 러닝 저장·조회와 사용자/신발 소유권 검사.
3. 수정·삭제와 신발 누적 거리/횟수를 한 트랜잭션으로 처리.
   동시 수정, 중복 저장 및 실패 rollback 검증.
4. 주/월 경계 시간대, 빈 통계, 총 시간/총 거리 기준 페이스 계산.
5. OpenWeather 응답 변환, 시간 제한, 외부 오류 처리, 이력 제공 출처 확정.
6. Gemini 클라이언트, 프롬프트와 응답 검증, 시간 제한, 실패 처리.
   추천 이유와 실제 제품 정보의 근거를 구분하고 실패 시 결과를 지어내지 않는다.

## 검증 범위

backend에서 `.\.venv\Scripts\python.exe -m pytest -q`로 실행한다.
기존 인증 테스트, 러닝 골격 테스트, Backend 2 추가 경로와 입력 검증,
외부 서비스 대역 연결, OpenAPI 인증 표기를 검사한다.
이는 실제 저장·추천 정확도나 PostgreSQL/Android/외부 API 연동 검증이 아니다.
