"""OpenWeather integration boundary. No external requests at scaffold stage."""
from app.schemas.weather import WeatherAdvice, WeatherHistory


class WeatherNotImplementedError(Exception):
    """Weather provider integration is pending."""


class WeatherService:
    async def advice(self, latitude: float, longitude: float) -> WeatherAdvice:
        # Add timeout, upstream error handling, unit conversion and advice.
        raise WeatherNotImplementedError

    async def history(self, latitude: float, longitude: float, days: int) -> WeatherHistory:
        # Confirm history source and provider plan before making requests.
        raise WeatherNotImplementedError
