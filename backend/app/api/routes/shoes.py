"""신발 관리 API 라우트
- 신발 등록, 조회, 수정, 삭제
- 신발별 누적 킬로 추적
"""
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import Shoe, User
from app.schemas.shoe import ShoeCreate, ShoeResponse, ShoeStats, ShoeUpdate

router = APIRouter(responses={
    401: {"description": "Authentication required"},
})


def _get_owned_shoe(shoe_id: int, user_id: int, db: Session) -> Shoe:
    shoe = db.scalar(
        select(Shoe).where(Shoe.id == shoe_id, Shoe.user_id == user_id)
    )
    if shoe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shoe not found",
        )
    return shoe


# 신발 등록
@router.post("", response_model=ShoeResponse, status_code=status.HTTP_201_CREATED)
def create_shoe(
    request: ShoeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shoe = Shoe(**request.model_dump(), user_id=current_user.id)
    db.add(shoe)
    db.commit()
    db.refresh(shoe)
    return shoe


# 신발 목록 조회
@router.get("", response_model=list[ShoeResponse])
def get_shoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list(db.scalars(
        select(Shoe).where(Shoe.user_id == current_user.id).order_by(Shoe.id)
    ).all())


# 신발 상세 조회
@router.get("/{shoe_id}", response_model=ShoeResponse)
def get_shoe(
    shoe_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_shoe(shoe_id, current_user.id, db)


# 신발 수정
@router.put("/{shoe_id}", response_model=ShoeResponse)
def update_shoe(
    request: ShoeUpdate,
    shoe_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shoe = _get_owned_shoe(shoe_id, current_user.id, db)
    # Ignore omitted fields and null values so partial updates preserve existing data.
    for field, value in request.model_dump(
        exclude_unset=True,
        exclude_none=True,
    ).items():
        setattr(shoe, field, value)
    db.commit()
    db.refresh(shoe)
    return shoe


# 신발 삭제
@router.delete("/{shoe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shoe(
    shoe_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shoe = _get_owned_shoe(shoe_id, current_user.id, db)
    db.delete(shoe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# 신발 통계
@router.get("/{shoe_id}/stats", response_model=ShoeStats)
def get_shoe_stats(
    shoe_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shoe = _get_owned_shoe(shoe_id, current_user.id, db)
    return ShoeStats(
        cumulative_km=shoe.cumulative_km or 0.0,
        run_count=shoe.run_count or 0,
        condition=shoe.condition or "good",
    )
