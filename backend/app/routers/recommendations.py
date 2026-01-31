from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, models_recommendations, schemas_recommendations
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

def get_bmi_category(bmi: float) -> str:
    """Determine BMI category from BMI value"""
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"

@router.get("/diet", response_model=List[schemas_recommendations.DietPlanSchema])
def get_diet_recommendations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized diet plan recommendations based on user BMI"""
    if not current_user.height or not current_user.weight:
        raise HTTPException(status_code=400, detail="Please complete your profile first")
    
    # Calculate BMI
    height_m = current_user.height / 100
    bmi = current_user.weight / (height_m ** 2)
    bmi_category = get_bmi_category(bmi)
    
    # Get diet plans for this BMI category
    diet_plans = db.query(models_recommendations.DietPlan).filter(
        models_recommendations.DietPlan.bmi_category == bmi_category
    ).all()
    
    if not diet_plans:
        raise HTTPException(status_code=404, detail="No diet plans found for your BMI category")
    
    return diet_plans

@router.get("/exercise", response_model=List[schemas_recommendations.ExerciseSchema])
def get_exercise_recommendations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized exercise recommendations based on user BMI and activity level"""
    if not current_user.height or not current_user.weight:
        raise HTTPException(status_code=400, detail="Please complete your profile first")
    
    # Calculate BMI
    height_m = current_user.height / 100
    bmi = current_user.weight / (height_m ** 2)
    bmi_category = get_bmi_category(bmi)
    
    # Get exercises for this BMI category
    exercises = db.query(models_recommendations.Exercise).filter(
        models_recommendations.Exercise.bmi_category == bmi_category
    ).all()
    
    if not exercises:
        # Return exercises for all categories if specific not found
        exercises = db.query(models_recommendations.Exercise).all()
    
    return exercises
