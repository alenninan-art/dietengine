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


ALTERNATIVE_FOODS = {
    "Appam & Kerala Chicken Stew": [
        {"name": "Idiyappam & Egg Curry", "reason": "Similar comfort meal with steadier protein and a moderate cost.", "price_estimate": 90.0},
        {"name": "Puttu & Green Gram Curry", "reason": "More fiber-rich while keeping the meal filling.", "price_estimate": 70.0},
    ],
    "Malabar Chicken Biriyani": [
        {"name": "Matta Rice & Chicken Roast", "reason": "Balanced Kerala-style lunch with a friendlier price.", "price_estimate": 120.0},
        {"name": "Chapati & Chicken Curry", "reason": "Lower oil and easier to portion.", "price_estimate": 95.0},
    ],
    "Banana, Peanut Butter & Milk": [
        {"name": "Soya Chunks Stir Fry", "reason": "Higher protein snack for a similar moderate budget.", "price_estimate": 40.0},
        {"name": "Fruit and Curd Bowl", "reason": "Lighter option with probiotics and fruit.", "price_estimate": 35.0},
    ],
    "Kerala Porotta & Beef Ularthiyathu": [
        {"name": "Chapati & Beef Roast", "reason": "Cuts down refined flour and keeps the same flavor profile.", "price_estimate": 130.0},
        {"name": "Matta Rice & Fish Curry", "reason": "A simpler Kerala dinner with balanced macros.", "price_estimate": 110.0},
    ],
    "Puttu & Kadala Curry": [
        {"name": "Idli & Sambar", "reason": "Affordable breakfast with similar satiety.", "price_estimate": 45.0},
        {"name": "Oats Upma", "reason": "Adds more fiber for a lighter start.", "price_estimate": 35.0},
    ],
    "Kerala Sadya (Mini)": [
        {"name": "Matta Rice, Sambar & Thoran", "reason": "Keeps the Kerala plate feel while lowering cost.", "price_estimate": 90.0},
        {"name": "Curd Rice with Vegetable Stir Fry", "reason": "Gentler and easier on digestion.", "price_estimate": 70.0},
    ],
    "Fruit and Curd Bowl": [
        {"name": "Sprouts Salad", "reason": "Higher fiber and more savory.", "price_estimate": 30.0},
        {"name": "Boiled Eggs and Cucumber", "reason": "Higher protein at a similar moderate cost.", "price_estimate": 25.0},
    ],
    "Pathiri & Kerala Meen Curry": [
        {"name": "Chapati & Fish Curry", "reason": "Similar dinner with easier availability.", "price_estimate": 95.0},
        {"name": "Matta Rice & Meen Curry", "reason": "Classic balanced Kerala meal.", "price_estimate": 100.0},
    ],
    "Idiyappam & Vegetable Stew": [
        {"name": "Oats Upma", "reason": "Moderate-budget breakfast with more fiber.", "price_estimate": 35.0},
        {"name": "Puttu & Kadala Curry", "reason": "Keeps the traditional breakfast feel and more protein.", "price_estimate": 60.0},
    ],
    "Matta Rice, Moru & Mathi Peera": [
        {"name": "Brown Rice & Grilled Fish", "reason": "Comparable nutrition with simpler prep.", "price_estimate": 85.0},
        {"name": "Chapati & Dal with Salad", "reason": "Vegetarian moderate-budget switch.", "price_estimate": 55.0},
    ],
    "Cherupayar Sprouts Chaat": [
        {"name": "Roasted Chana Bowl", "reason": "Crunchy, budget-friendly, and easy to carry.", "price_estimate": 20.0},
        {"name": "Sambharam with Peanuts", "reason": "Hydrating snack with some healthy fats.", "price_estimate": 20.0},
    ],
    "Godhambu (Wheat) Dosa & Tomato Chutney": [
        {"name": "Chapati & Vegetable Curry", "reason": "Same moderate price band with simple ingredients.", "price_estimate": 45.0},
        {"name": "Ragi Dosa & Chutney", "reason": "Adds whole-grain variety.", "price_estimate": 40.0},
    ],
    "Kerala Mutta Roast & 1 Appam": [
        {"name": "Boiled Eggs and Fruit", "reason": "Cheaper high-protein breakfast.", "price_estimate": 35.0},
        {"name": "Idli & Egg Bhurji", "reason": "Balanced breakfast with moderate calories.", "price_estimate": 50.0},
    ],
    "Karimeen Pollichathu": [
        {"name": "Grilled Sardine Plate", "reason": "More moderate pricing while keeping omega-3 rich fish.", "price_estimate": 130.0},
        {"name": "Grilled Chicken and Salad", "reason": "Lean protein and easier budget control.", "price_estimate": 120.0},
    ],
    "Boiled Eggs and Cucumber": [
        {"name": "Fruit and Curd Bowl", "reason": "Lighter probiotic option.", "price_estimate": 35.0},
        {"name": "Sprouts Salad", "reason": "Fiber-rich plant-based swap.", "price_estimate": 30.0},
    ],
    "Alfaham Chicken with Salad": [
        {"name": "Grilled Chicken Wrap", "reason": "Moderate cost and easier portion sizing.", "price_estimate": 120.0},
        {"name": "Fish Curry with Salad", "reason": "Kerala-style protein with a lighter finish.", "price_estimate": 110.0},
    ],
}

FOOD_PRICE_BY_COURSE = {
    "breakfast": 45.0,
    "snack": 30.0,
    "main course": 95.0,
    "main course / breakfast": 60.0,
    "main course / festival": 110.0,
    "dessert": 40.0,
    "salad": 35.0,
    "side dish": 30.0,
}


def get_price_level(price: float) -> str:
    if price <= 35:
        return "budget"
    if price <= 110:
        return "moderate"
    return "premium"


def get_food_estimated_price(course: str | None) -> float:
    if not course:
        return 55.0
    normalized = course.strip().lower()
    return FOOD_PRICE_BY_COURSE.get(normalized, 55.0)


def serialize_meal(meal: models_recommendations.Meal) -> dict:
    alternatives = ALTERNATIVE_FOODS.get(meal.name, [])
    return {
        "id": meal.id,
        "meal_type": meal.meal_type,
        "name": meal.name,
        "description": meal.description,
        "calories": meal.calories,
        "protein_g": meal.protein_g,
        "carbs_g": meal.carbs_g,
        "fats_g": meal.fats_g,
        "price_estimate": meal.price_estimate,
        "price_level": get_price_level(meal.price_estimate),
        "quantity": meal.quantity,
        "alternative_foods": [
            {
                **item,
                "price_level": get_price_level(item["price_estimate"]),
            }
            for item in alternatives
        ],
    }


def serialize_plan(plan: models_recommendations.DietPlan) -> dict:
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "bmi_category": plan.bmi_category,
        "calories_per_day": plan.calories_per_day,
        "protein_g": plan.protein_g,
        "carbs_g": plan.carbs_g,
        "fats_g": plan.fats_g,
        "meals": [serialize_meal(meal) for meal in plan.meals],
    }


def serialize_food_item(item: models_recommendations.FoodItem) -> dict:
    estimated_price = get_food_estimated_price(item.course)
    return {
        "id": item.id,
        "name": item.name,
        "cuisine": item.cuisine,
        "course": item.course,
        "diet": item.diet,
        "servings": item.servings,
        "prep_time_minutes": item.prep_time_minutes,
        "cook_time_minutes": item.cook_time_minutes,
        "total_time_minutes": item.total_time_minutes,
        "ingredients": item.ingredients,
        "instructions": item.instructions,
        "estimated_price": estimated_price,
        "price_level": get_price_level(estimated_price),
    }

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
    
    return [serialize_plan(plan) for plan in diet_plans]

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
    query = db.query(models_recommendations.Exercise).filter(
        models_recommendations.Exercise.bmi_category == bmi_category
    )
    
    # Filter by location if set
    if current_user.workout_location:
        query = query.filter(
            (models_recommendations.Exercise.location_type == current_user.workout_location) | 
            (models_recommendations.Exercise.location_type == "Any")
        )
    
    exercises = query.all()
    
    if not exercises:
        # Return exercises for all categories if specific not found
        exercises = db.query(models_recommendations.Exercise).all()
    
    return exercises


@router.get("/foods", response_model=List[schemas_recommendations.FoodItemSchema])
def get_food_catalog(
    q: str | None = None,
    course: str | None = None,
    diet: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Browse the Kerala food catalog imported from the dataset."""
    query = db.query(models_recommendations.FoodItem)

    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (models_recommendations.FoodItem.name.ilike(like)) |
            (models_recommendations.FoodItem.ingredients.ilike(like)) |
            (models_recommendations.FoodItem.course.ilike(like))
        )

    if course:
        query = query.filter(models_recommendations.FoodItem.course.ilike(f"%{course.strip()}%"))

    if diet:
        query = query.filter(models_recommendations.FoodItem.diet.ilike(f"%{diet.strip()}%"))

    limit = max(1, min(limit, 50))
    items = query.order_by(models_recommendations.FoodItem.name.asc()).limit(limit).all()
    return [serialize_food_item(item) for item in items]
