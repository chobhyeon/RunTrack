# 신발·러닝 API의 인증 의존성 사용

공통 의존성은 app/api/dependencies.py의 get_current_user입니다.
Authorization: Bearer 헤더를 읽고 설정의 허용 알고리즘·서명·만료·사용자 ID를
검증한 뒤 DB의 User를 반환합니다. 누락·잘못된 토큰 또는 삭제된 사용자는
401과 WWW-Authenticate: Bearer 헤더를 반환합니다.

라우트에서는 토큰을 직접 해석하지 않고 다음처럼 주입합니다.
기존 DB 세션과 함께 사용하면 FastAPI가 동일 요청의 get_db 결과를 재사용합니다.
현재 SQLAlchemy 세션은 동기 방식이므로 아래 예시는 동기 라우트입니다.

```python
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import Shoe, User


@router.get("/{shoe_id}")
def get_shoe(
    shoe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shoe = db.scalar(select(Shoe).where(
        Shoe.id == shoe_id,
        Shoe.user_id == current_user.id,
    ))
    if shoe is None:
        raise HTTPException(status_code=404, detail="Shoe not found")
    # 실제 라우트에서는 response_model= ShoeResponse 등으로 반환 필드를 제한합니다.
    return shoe
```

위 코드는 적용 예시이며 현재 신발·러닝 라우트를 변경하지는 않았습니다.
인증 성공은 다른 사용자의 데이터 접근 권한을 의미하지 않습니다.

- 목록 조회: user_id == current_user.id 조건으로 필터링합니다.
- 단건 조회·수정·삭제: 자원 ID와 user_id 조건을 함께 사용합니다.
- 신규 생성: user_id는 요청값 대신 current_user.id로 지정합니다.
- 러닝 기록에 shoe_id를 지정할 때에도 신발의 소유자를 확인합니다.
- User ORM을 그대로 응답하면 hashed_password가 노출될 수 있으므로,
  사용자 응답은 UserResponse 등 명시적인 response_model로 제한합니다.
- 비밀번호·토큰·Authorization 헤더를 로그에 출력하지 않습니다.

HTTPBearer가 OpenAPI 보안 스키마를 생성하므로 의존성을 적용한 API는
/docs의 Authorize 버튼에서 토큰을 입력해 호출할 수 있습니다.

## 내 정보 수정 동작

PUT /api/users/me는 URL 또는 요청 본문에서 사용자 ID를 받지 않습니다.
get_current_user로 확인한 사용자만 수정합니다. UserUpdate의 필드 외에는
422로 거부하고, 생략한 선택 필드는 유지하며 null은 비웁니다.
preferred_brands는 DB의 JSON 문자열과 API의 배열 사이에서 변환됩니다.
DB 저장 실패 시 rollback하고, 성공 시 갱신된 UserResponse를 반환합니다.

## 검증

backend에서 다음 명령으로 격리된 SQLite 기반 테스트를 실행합니다.

```bash
python -m pytest
```

조회·수정, 계정 간 수정 차단, 삭제된 사용자, 누락·만료·변조·잘못된 알고리즘의
토큰, 잘못된 sub/exp, 저장 실패 rollback 및 Swagger 보안 스키마를 검증합니다.
실제 PostgreSQL의 데이터를 변경하지 않습니다.
