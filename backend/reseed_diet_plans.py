from app.database import SessionLocal
from app.models_recommendations import DietPlan, Meal, Exercise
from app.seeder import seed_database

# Clear existing data
db = SessionLocal()
try:
    # Delete in correct order (meals first due to foreign key)
    db.query(Meal).delete()
    db.query(DietPlan).delete()
    db.query(Exercise).delete()
    db.commit()
    print("Cleared all existing diet plans, meals, and exercises")
    
    # Reseed with updated data
    seed_database(db)
    print("Database reseeded with updated rice portions")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
