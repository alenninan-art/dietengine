from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
import time
import random
from ..routers.auth import get_current_user
from .. import models

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

# Mock food database for AI results
FOOD_DATABASE = {
    "pizza": {"calories": 266, "protein": 11, "carbs": 33, "fats": 10},
    "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fats": 0.2},
    "chicken_rice": {"calories": 450, "protein": 35, "carbs": 50, "fats": 12},
    "salad": {"calories": 150, "protein": 5, "carbs": 10, "fats": 8},
    "burger": {"calories": 500, "protein": 25, "carbs": 40, "fats": 25},
}

@router.post("/estimate")
async def estimate_calories(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """
    Mock AI endpoint that 'analyzes' an image and returns calorie estimation.
    In a real app, this would use YOLOv8 or a CNN model.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Simulate AI processing time
    time.sleep(1.5)
    
    # Mock detection - randomly pick a food from our small database
    food_names = list(FOOD_DATABASE.keys())
    detected_food = random.choice(food_names)
    nutrition = FOOD_DATABASE[detected_food]
    
    return {
        "food_name": detected_food.replace("_", " ").title(),
        "confidence": round(random.uniform(0.85, 0.99), 2),
        "nutrition": nutrition,
        "message": f"AI detected {detected_food.replace('_', ' ')} with high confidence."
    }
