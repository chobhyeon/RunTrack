"""
Google Gemini API를 활용한 AI 신발 추천 서비스
"""
from app.schemas.recommendation import ShoeRecommendationResponse


class RecommendationNotImplementedError(Exception):
    """Gemini integration is pending."""

class ShoeRecommendationService:
    """AI 신발 추천 서비스"""
    
    def __init__(self):
        """Gemini API 초기화"""
        pass
    
    async def get_shoe_recommendations(
        self,
        weight_kg: float,
        height_cm: float,
        foot_size: str,
        foot_width: str,
        arch_type: str,
        running_style: str,
        budget_won: int,
        preferred_brands: list = None
    ) -> ShoeRecommendationResponse:
        """사용자의 신체 정보와 선호도를 바탕으로 AI가 신발을 추천"""
        # Add Gemini client timeout, structured response validation and failure handling.
        # Never fabricate recommendations when the provider fails.
        raise RecommendationNotImplementedError

# 서비스 인스턴스
shoe_recommendation_service = ShoeRecommendationService()
