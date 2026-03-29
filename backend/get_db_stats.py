from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, models_recommendations

def get_stats():
    db = SessionLocal()
    try:
        users = db.query(models.User).count()
        diet_plans = db.query(models_recommendations.DietPlan).count()
        meals = db.query(models_recommendations.Meal).count()
        exercises = db.query(models_recommendations.Exercise).count()
        
        print(f"Users: {users}")
        print(f"Diet Plans: {diet_plans}")
        print(f"Meals: {meals}")
        print(f"Exercises: {exercises}")
    finally:
        db.close()

if __name__ == "__main__":
    get_stats()
