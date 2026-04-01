from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AlternativeFoodSchema(BaseModel):
    name: str
    reason: str
    price_estimate: float
    price_level: str

class MealSchema(BaseModel):
    id: int
    meal_type: str
    name: str
    description: str
    calories: int
    protein_g: float
    carbs_g: float
    fats_g: float
    price_estimate: float
    price_level: str
    quantity: Optional[str] = None
    alternative_foods: List[AlternativeFoodSchema] = []
    
    class Config:
        from_attributes = True

class DietPlanSchema(BaseModel):
    id: int
    name: str
    description: str
    bmi_category: str
    calories_per_day: int
    protein_g: float
    carbs_g: float
    fats_g: float
    meals: List[MealSchema] = []
    
    class Config:
        from_attributes = True

class ExerciseSchema(BaseModel):
    id: int
    name: str
    description: str
    category: str
    intensity: str
    duration_minutes: int
    calories_burned: int
    bmi_category: str
    equipment_needed: Optional[str] = None
    
    class Config:
        from_attributes = True


class FoodItemSchema(BaseModel):
    id: int
    name: str
    cuisine: Optional[str] = None
    course: Optional[str] = None
    diet: Optional[str] = None
    servings: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    total_time_minutes: Optional[int] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    estimated_price: float
    price_level: str

    class Config:
        from_attributes = True


class FoodTrackingCreate(BaseModel):
    meal_name: str
    meal_type: Optional[str] = None
    selected_option: str
    source_plan: Optional[str] = None
    price_estimate: float = 0.0
    notes: Optional[str] = None


class FoodTrackingSchema(FoodTrackingCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FoodTrackingSummarySchema(BaseModel):
    total_tracked: int
    this_week: int
    average_price: float
    latest_selection: Optional[str] = None
