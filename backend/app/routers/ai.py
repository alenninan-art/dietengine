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

# Mock food database for AI results (Per 100g or 250ml serving)
FOOD_DATABASE = {
    # Traditional Indian/Kerala Dishes
    "puttu_and_kadala": {"calories": 350, "protein": 12, "carbs": 60, "fats": 8},
    "appam_and_egg_curry": {"calories": 320, "protein": 15, "carbs": 45, "fats": 10},
    "chicken_biryani": {"calories": 550, "protein": 30, "carbs": 70, "fats": 18},
    "masala_dosa": {"calories": 380, "protein": 8, "carbs": 65, "fats": 10},
    "idli_with_sambar": {"calories": 250, "protein": 10, "carbs": 45, "fats": 4},
    "kerala_sadya_meal": {"calories": 850, "protein": 20, "carbs": 140, "fats": 25},
    "fish_curry_meals": {"calories": 600, "protein": 35, "carbs": 95, "fats": 12},
    "nadan_chicken_fry": {"calories": 400, "protein": 28, "carbs": 5, "fats": 30},
    
    # Snacks
    "samosa": {"calories": 260, "protein": 4, "carbs": 25, "fats": 18},
    "banana_chips": {"calories": 520, "protein": 2, "carbs": 60, "fats": 32},
    "masala_vada": {"calories": 150, "protein": 6, "carbs": 15, "fats": 8},
    "parippu_vada": {"calories": 180, "protein": 8, "carbs": 20, "fats": 10},
    
    # Drinks
    "sambharam_buttermilk": {"calories": 45, "protein": 3, "carbs": 5, "fats": 1},
    "kerala_chai_tea": {"calories": 90, "protein": 3, "carbs": 12, "fats": 4},
    "tender_coconut_water": {"calories": 45, "protein": 1, "carbs": 10, "fats": 0.1},
    "filter_coffee": {"calories": 80, "protein": 2, "carbs": 10, "fats": 4},
    
    # Standard Items
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
