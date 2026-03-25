from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from .auth import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

@router.put("/", response_model=schemas.User)
def update_profile(
    profile: schemas.UserProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update user profile fields
    if profile.full_name is not None:
        current_user.full_name = profile.full_name
    if profile.age is not None:
        current_user.age = profile.age
    if profile.height is not None:
        current_user.height = profile.height
    if profile.weight is not None:
        current_user.weight = profile.weight
    if profile.gender is not None:
        current_user.gender = profile.gender
    if profile.activity_level is not None:
        current_user.activity_level = profile.activity_level
    if profile.health_goals is not None:
        current_user.health_goals = profile.health_goals
    if profile.workout_location is not None:
        current_user.workout_location = profile.workout_location
    if profile.equipment_available is not None:
        current_user.equipment_available = profile.equipment_available
    if profile.injuries_limitations is not None:
        current_user.injuries_limitations = profile.injuries_limitations
    if profile.workout_days_per_week is not None:
        current_user.workout_days_per_week = profile.workout_days_per_week
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/bmi")
def calculate_bmi(current_user: models.User = Depends(get_current_user)):
    if not current_user.height or not current_user.weight:
        raise HTTPException(status_code=400, detail="Height and weight required to calculate BMI")
    
    # BMI = weight(kg) / (height(m))^2
    height_m = current_user.height / 100  # convert cm to m
    bmi = current_user.weight / (height_m ** 2)
    
    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 2),
        "category": category,
        "height": current_user.height,
        "weight": current_user.weight
    }
