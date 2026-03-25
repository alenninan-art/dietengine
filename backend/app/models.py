from sqlalchemy import Column, Integer, String, Float, Enum
from .database import Base
import enum

class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class ActivityLevel(str, enum.Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extra_active = "extra_active"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    
    # Profile Data
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True) # in cm
    weight = Column(Float, nullable=True) # in kg
    gender = Column(Enum(Gender), nullable=True)
    activity_level = Column(Enum(ActivityLevel), nullable=True)
    health_goals = Column(String, nullable=True) # e.g. "lose weight", "gain muscle"

