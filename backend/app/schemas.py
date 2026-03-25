from pydantic import BaseModel
from typing import Optional
from .models import Gender, ActivityLevel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[Gender] = None
    activity_level: Optional[ActivityLevel] = None
    health_goals: Optional[str] = None
    
    # Fitness Coach Fields
    workout_location: Optional[str] = None
    equipment_available: Optional[str] = None
    injuries_limitations: Optional[str] = None
    workout_days_per_week: Optional[int] = None

class User(UserBase):
    id: int
    is_active: bool = True
    
    # Profile info included in response
    full_name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[Gender] = None
    activity_level: Optional[ActivityLevel] = None
    health_goals: Optional[str] = None
    
    # Fitness Coach Fields
    workout_location: Optional[str] = None
    equipment_available: Optional[str] = None
    injuries_limitations: Optional[str] = None
    workout_days_per_week: Optional[int] = None

    class Config:
        from_attributes = True
