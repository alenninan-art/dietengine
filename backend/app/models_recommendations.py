from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class DietPlan(Base):
    __tablename__ = "diet_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    bmi_category = Column(String)  # underweight, normal, overweight, obese
    calories_per_day = Column(Integer)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fats_g = Column(Float)
    meals = relationship("Meal", back_populates="diet_plan")

class Meal(Base):
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    diet_plan_id = Column(Integer, ForeignKey("diet_plans.id"))
    meal_type = Column(String)  # breakfast, lunch, dinner, snack
    name = Column(String)
    description = Column(Text)
    calories = Column(Integer)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fats_g = Column(Float)
    price_estimate = Column(Float, default=0.0)
    quantity = Column(String, nullable=True) # e.g. "1 cup", "2 pieces"
    
    diet_plan = relationship("DietPlan", back_populates="meals")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    category = Column(String)  # cardio, strength, flexibility, sports
    intensity = Column(String)  # low, moderate, high
    duration_minutes = Column(Integer)
    calories_burned = Column(Integer)  # approximate per session
    bmi_category = Column(String)  # recommended for which BMI category
    equipment_needed = Column(String, nullable=True)
    location_type = Column(String, default="Any") # e.g., "Gym", "Home", "Any"
