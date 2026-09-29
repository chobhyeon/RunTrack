"""
사용자 관련 API 라우트
- 회원가입, 로그인, 프로필 관리
"""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate, TokenResponse

router = APIRouter()

# 회원가입
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Username or email already exists"}},
)
def register(request: UserCreate, db: Session = Depends(get_db)):
    conflict = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Username or email already exists",
    )
    existing = db.scalar(select(User.id).where(or_(
        User.username == request.username, User.email == request.email,
    )))
    if existing is not None:
        raise conflict

    values = request.model_dump(exclude={"password"})
    brands = values["preferred_brands"]
    values["preferred_brands"] = json.dumps(brands, ensure_ascii=False) if brands is not None else None
    user = User(**values, hashed_password=hash_password(request.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # PostgreSQL unique_violation, or SQLite's unique constraint in tests.
        original = exc.orig
        is_unique = (
            getattr(original, "pgcode", None) == "23505"
            or getattr(original, "sqlite_errorname", None) == "SQLITE_CONSTRAINT_UNIQUE"
        )
        if is_unique:
            raise conflict from None
        raise
    db.refresh(user)
    return user

# 로그인
@router.post(
    "/login", response_model=TokenResponse,
    responses={401: {"description": "Invalid username or password"}},
)
def login(request: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == request.username))
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer", expires_in=expires_in)

# 프로필 조회
@router.get(
    "/me", response_model=UserResponse,
    responses={401: {"description": "Could not validate credentials"}},
)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# 프로필 수정
@router.put(
    "/me", response_model=UserResponse,
    responses={401: {"description": "Could not validate credentials"}},
)
def update_profile(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    values = request.model_dump(exclude_unset=True)
    if "preferred_brands" in values and values["preferred_brands"] is not None:
        values["preferred_brands"] = json.dumps(values["preferred_brands"], ensure_ascii=False)
    for name, value in values.items():
        setattr(current_user, name, value)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(current_user)
    return current_user
