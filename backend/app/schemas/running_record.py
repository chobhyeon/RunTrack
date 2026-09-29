"""
러닝 기록 Pydantic 스키마
"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class RunningRecordBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    distance_km: float
    duration_minutes: int
    start_time: datetime
    end_time: datetime

class RunningRecordCreate(RunningRecordBase):
    shoe_id: Optional[int] = None
    avg_pace_min_per_km: Optional[float] = None
    max_speed_kmh: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    elevation_gain_m: Optional[float] = None
    temperature_c: Optional[float] = None
    feeling: Optional[str] = None
    notes: Optional[str] = None

class RunningRecordUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    shoe_id: Optional[int] = Field(default=None, gt=0)
    feeling: Optional[str] = None
    notes: Optional[str] = None

class RunningRecordResponse(RunningRecordBase):
    id: int
    user_id: int
    shoe_id: Optional[int]
    avg_pace_min_per_km: Optional[float]
    max_speed_kmh: Optional[float]
    avg_speed_kmh: Optional[float]
    avg_heart_rate: Optional[int]
    calories_burned: Optional[float]
    elevation_gain_m: Optional[float]
    temperature_c: Optional[float]
    feeling: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RunningStatistics(BaseModel):
    total_distance_km: float
    total_runs: int
    avg_distance_km: float
    avg_pace_min_per_km: float
    total_duration_minutes: int
    avg_duration_minutes: int
    total_calories: float
    avg_heart_rate: Optional[float]
    avg_elevation_gain_m: Optional[float]
