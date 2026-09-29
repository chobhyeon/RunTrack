"""
기상 데이터 & 조언 API 라우트
- 현재 기상 조건 기반 체감온도 계산
- 러닝 추천 점수 (0-100)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_current_user
from app.schemas.weather import WeatherAdvice, WeatherHistory
from app.services.weather import WeatherNotImplementedError, WeatherService

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Authentication required"},
               501: {"description": "Weather integration not implemented yet"}},
)


async def get_weather_service():
    try:
        yield WeatherService()
    except WeatherNotImplementedError:
        raise HTTPException(501, "Weather feature is not implemented yet") from None

# 러닝 조언
@router.get("/advice", response_model=WeatherAdvice)
async def get_running_advice(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    service: WeatherService = Depends(get_weather_service),
):
    return await service.advice(latitude, longitude)

# 기상 이력
@router.get("/history", response_model=WeatherHistory)
async def get_weather_history(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=30),
    service: WeatherService = Depends(get_weather_service),
):
    return await service.history(latitude, longitude, days)
