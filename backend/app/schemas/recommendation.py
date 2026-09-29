"""Draft Gemini shoe recommendation contract matching existing service inputs."""
from pydantic import BaseModel, ConfigDict, Field


class ShoeRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    weight_kg: float = Field(gt=0, allow_inf_nan=False)
    height_cm: float = Field(gt=0, allow_inf_nan=False)
    foot_size: str = Field(min_length=1)
    foot_width: str = Field(min_length=1)
    arch_type: str = Field(min_length=1)
    running_style: str = Field(min_length=1)
    budget_won: int = Field(gt=0)
    preferred_brands: list[str] | None = None


class RecommendedShoe(BaseModel):
    brand: str
    model: str
    reason: str


class ShoeRecommendationResponse(BaseModel):
    recommendations: list[RecommendedShoe]
