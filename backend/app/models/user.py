"""
사용자 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # 신체 정보
    weight_kg = Column(Float)
    height_cm = Column(Integer)
    foot_size = Column(String)  # "280mm", "US 10" 등
    foot_width = Column(String)  # "narrow", "regular", "wide"
    arch_type = Column(String)  # "low", "", "high"
    
    # 선호도
    running_style = Column(String)  # "cushioning", "speed", "trail", "all-purpose"
    budget_won = Column(Integer)
    preferred_brands = Column(String)  # JSON 형식
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    shoes = relationship("Shoe", back_populates="user")
    running_records = relationship("RunningRecord", back_populates="user")
