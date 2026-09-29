"""Authenticated endpoint for the existing Gemini service boundary."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.ai.recommendations import (
    RecommendationNotImplementedError,
    ShoeRecommendationService,
    shoe_recommendation_service,
)
from app.schemas.recommendation import ShoeRecommendationRequest, ShoeRecommendationResponse


router = APIRouter(
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Authentication required"},
               501: {"description": "Gemini integration not implemented yet"}},
)


def get_recommendation_service() -> ShoeRecommendationService:
    return shoe_recommendation_service


@router.post("/shoes", response_model=ShoeRecommendationResponse)
async def recommend_shoes(
    request: ShoeRecommendationRequest,
    service: ShoeRecommendationService = Depends(get_recommendation_service),
):
    """Draft: profile fields are supplied explicitly; Gemini calls are pending."""
    try:
        return await service.get_shoe_recommendations(**request.model_dump())
    except RecommendationNotImplementedError:
        raise HTTPException(501, "Shoe recommendation is not implemented yet") from None
