# 사용자 인증 API 계약

README의 경로와 기존 사용자 모델·스키마를 기준으로 정리한 계약입니다.
회원가입·로그인·내 정보 조회·수정 라우트와 스키마 검증이 구현되어 있습니다.
아래 성공 응답·오류 응답은 현재 구현된 계약입니다.

## 경로와 응답

| 메서드 / 경로 | 요청 | 성공 응답 | 인증 |
| --- | --- | --- | --- |
| POST /api/users/register | UserCreate JSON | 201, UserResponse | 불필요 |
| POST /api/users/login | UserLogin JSON | 200, TokenResponse | 불필요 |
| GET /api/users/me | 본문 없음 | 200, UserResponse | Bearer 토큰 |
| PUT /api/users/me | UserUpdate JSON | 200, UserResponse | Bearer 토큰 |

요청 본문의 Content-Type은 application/json입니다.

## 필수·선택 필드

- UserCreate 필수: username, email, password (문자열).
- UserLogin 필수: username, password (문자열).
- 회원가입 선택: weight_kg(float), height_cm(int), foot_size(str),
  foot_width(str), arch_type(str), running_style(str), budget_won(int),
  preferred_brands(list[str]). 생략하거나 null을 보낼 수 있습니다.
- UserUpdate: 위 선택 필드만 받습니다. username, email, password 변경은 계약에 없습니다.
- UserResponse: username, email, 위 선택 필드와 id(int), created_at,
  updated_at(ISO 8601 날짜 문자열)을 반환합니다.
- TokenResponse: access_token(비어 있지 않은 문자열), token_type("bearer"),
  expires_in(양의 정수, 초)을 반환합니다.

UserResponse에는 password와 hashed_password 필드가 없습니다.
회원가입은 response_model=UserResponse로 응답을 제한합니다.
preferred_brands는 DB에 JSON 문자열로 저장하고 응답에서 문자열 배열로 변환합니다.

## 요청·응답 예시

회원가입: POST /api/users/register

```json
{"username": "runner01", "email": "runner@example.com", "password": "example-password", "weight_kg": 65.0}
```

201 성공 응답 (GET /api/users/me도 같은 형태):

```json
{
  "id": 1,
  "username": "runner01",
  "email": "runner@example.com",
  "weight_kg": 65.0,
  "height_cm": null,
  "foot_size": null,
  "foot_width": null,
  "arch_type": null,
  "running_style": null,
  "budget_won": null,
  "preferred_brands": null,
  "created_at": "2026-09-28T10:00:00",
  "updated_at": "2026-09-28T10:00:00"
}
```

로그인: POST /api/users/login

```json
{"username": "runner01", "password": "example-password"}
```

200 성공 응답 (1800초는 현재 30분 설정에 해당하는 예시):

```json
{"access_token": "<jwt>", "token_type": "bearer", "expires_in": 1800}
```

로그인 토큰은 app/config.py의 SECRET_KEY, ALGORITHM,
ACCESS_TOKEN_EXPIRE_MINUTES를 사용합니다. sub는 문자열 사용자 ID이고,
iat 및 exp는 UTC 기준 Unix timestamp(초)입니다.
exp - iat와 응답 expires_in은 동일한 설정값에서 계산됩니다.

GET /api/users/me, PUT /api/users/me 요청 헤더:

```http
Authorization: Bearer <jwt>
```

프로필 수정: PUT /api/users/me

```json
{"weight_kg": 66.0, "preferred_brands": ["Nike", "Adidas"]}
```

200 응답은 수정된 UserResponse입니다. 생략한 필드는 유지하고,
명시적인 null은 해당 선택 필드를 비웁니다.
model_dump(exclude_unset=True)로 둘을 구분합니다.
빈 객체는 프로필을 유지합니다. UserUpdate에 없는 필드(id, user_id,
username, email, password 등)는 422로 거부합니다.

## 주요 오류 상태 코드

| 상태 | 적용 상황 | 응답 |
| --- | --- | --- |
| 422 | 필수 필드 누락, null, 잘못된 타입, 빈 필수 문자열 | FastAPI 기본 detail 배열 |
| 409 | 회원가입 username 또는 email 중복 | {"detail": "Username or email already exists"} |
| 401 | 존재하지 않는 사용자 또는 잘못된 비밀번호 | {"detail": "Invalid username or password"} |
| 401 | 보호된 API의 토큰 누락·만료·변조 또는 사용자 없음 | {"detail": "Could not validate credentials"} |

보호된 API의 401에는 WWW-Authenticate: Bearer 헤더를 반환합니다.
비밀번호 검증 오류의 상세 이유나 비밀번호·해시는 응답에 포함하지 않습니다.
Pydantic 검증 오류의 input에는 입력값이 포함될 수 있으므로,
요청 검증 오류 응답에서는 input과 ctx를 제거하고 위치·유형·메시지만 반환합니다.

## README에 없었던 새 결정 사항

- 로그인 식별자는 기존 UserLogin과 동일하게 username을 사용합니다.
- 필수 문자열은 빈 문자열 및 공백만 있는 문자열을 거부합니다.
  검증은 원래 문자열을 그대로 반환하며 비밀번호를 trim하거나 변경하지 않습니다.
- 이번 단계에서는 이메일 형식 검증, 비밀번호 길이·복잡도 정책을 추가하지 않습니다.
- 비밀번호 저장은 기존 passlib의 PBKDF2-SHA256(600,000회, 랜덤 salt)을 사용합니다.
  비밀번호 전체를 해싱하며 JWT SECRET_KEY와 독립적으로 동작합니다.
- 회원가입 201, 중복 409, 인증 실패 401 및 위 오류 메시지를 계약으로 정합니다.
- 토큰 타입은 bearer로 고정하고 수명은 초 단위 양의 정수로 반환합니다.
- /me 수정은 생략한 값 유지, 명시적 null은 삭제하는 방식입니다.
- 보호된 API는 설정의 ALGORITHM만 허용하며 서명, 필수 exp와 sub를 검증합니다.
  exp는 미래의 정수 Unix timestamp, sub는 양의 PostgreSQL INTEGER 범위 사용자 ID 문자열이어야 합니다.
  토큰이 유효해도 DB에 사용자가 없으면 401입니다.
- refresh token, 로그아웃·비밀번호 재설정 API는 이 계약의 범위에 없습니다.

## Swagger에서 호출

1. /docs에서 회원가입 후 로그인 API를 실행합니다.
2. 로그인 응답의 access_token을 복사합니다.
3. Authorize 버튼의 HTTPBearer 입력란에 토큰 문자열만 붙여 넣습니다.
   Bearer 접두사는 Swagger가 추가합니다.
4. GET /api/users/me 또는 PUT /api/users/me를 실행합니다.

다른 API에 적용하는 방법은 [인증 의존성 사용 가이드](AUTH_DEPENDENCIES.md)를 참고하세요.
