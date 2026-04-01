from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, models_recommendations, schemas_recommendations
from ..database import get_db
from .auth import get_current_user

router = APIRouter(
    prefix="/tracking",
    tags=["tracking"]
)


@router.post("/foods", response_model=schemas_recommendations.FoodTrackingSchema)
def track_food_selection(
    payload: schemas_recommendations.FoodTrackingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = models_recommendations.UserFoodTracking(
        user_id=current_user.id,
        meal_name=payload.meal_name,
        meal_type=payload.meal_type,
        selected_option=payload.selected_option,
        source_plan=payload.source_plan,
        price_estimate=payload.price_estimate,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/foods", response_model=list[schemas_recommendations.FoodTrackingSchema])
def get_tracked_foods(
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 100))
    return (
        db.query(models_recommendations.UserFoodTracking)
        .filter(models_recommendations.UserFoodTracking.user_id == current_user.id)
        .order_by(models_recommendations.UserFoodTracking.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/foods/summary", response_model=schemas_recommendations.FoodTrackingSummarySchema)
def get_food_tracking_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(models_recommendations.UserFoodTracking)
        .filter(models_recommendations.UserFoodTracking.user_id == current_user.id)
        .order_by(models_recommendations.UserFoodTracking.created_at.desc())
        .all()
    )
    week_ago = datetime.utcnow() - timedelta(days=7)
    this_week = sum(1 for entry in entries if entry.created_at >= week_ago)
    average_price = round(sum(entry.price_estimate for entry in entries) / len(entries), 2) if entries else 0.0

    return {
        "total_tracked": len(entries),
        "this_week": this_week,
        "average_price": average_price,
        "latest_selection": entries[0].selected_option if entries else None,
    }
