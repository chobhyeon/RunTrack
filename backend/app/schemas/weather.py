"""Draft weather response contracts; no fabricated observations or advice."""
from datetime import date

from pydantic import BaseModel, Field


class WeatherLocation(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class WeatherAdvice(WeatherLocation):
    temperature_c: float
    perceived_temperature_c: float
    humidity_percent: int = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0)
    uv_index: float | None = Field(default=None, ge=0)
    running_score: int | None = Field(default=None, ge=0, le=100)
    condition: str
    tips: list[str]


class WeatherData(BaseModel):
    date: date
    temperature_c: float
    condition: str
    humidity_percent: int = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0)


class WeatherHistory(BaseModel):
    location: WeatherLocation
    days: int = Field(ge=1, le=30)
    history: list[WeatherData]
