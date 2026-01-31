from pydantic import BaseModel
from typing import List, Optional

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
    quantity: Optional[str] = None
    
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
