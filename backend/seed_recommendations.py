"""Seed database with sample diet plans and exercises"""
import sys
sys.path.append('.')
from app.database import SessionLocal, engine, Base
from app import models_recommendations

# Create tables (drop first to update schema)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def seed_diet_plans():
    db = SessionLocal()
    
    # Diet Plans for each BMI category
    diet_plans_data = [
        {
            "name": "Indian Heritage - Weight Gain",
            "description": "High-calorie, budget-friendly Indian nutrition for healthy weight gain.",
            "bmi_category": "underweight",
            "calories_per_day": 2800,
            "protein_g": 140,
            "carbs_g": 350,
            "fats_g": 93,
            "meals": [
                {"meal_type": "breakfast", "name": "Puttu & Kadala Curry", "description": "Steamed rice cake with spicy black chickpeas", "calories": 650, "protein_g": 18, "carbs_g": 95, "fats_g": 22, "price_estimate": 35.0, "quantity": "2 pieces (150g) + 1 cup (200g) curry"},
                {"meal_type": "snack", "name": "Banana Fritters & Milk", "description": "Kerala Ethakka Appam with whole milk", "calories": 350, "protein_g": 8, "carbs_g": 50, "fats_g": 12, "price_estimate": 25.0, "quantity": "2 pieces (120g) + 1 glass (250ml) milk"},
                {"meal_type": "lunch", "name": "Neychoru & Chicken Curry", "description": "Budget ghee rice with Kerala chicken masala", "calories": 850, "protein_g": 40, "carbs_g": 90, "fats_g": 35, "price_estimate": 120.0, "quantity": "2 cups (400g) rice + 200g chicken"},
                {"meal_type": "snack", "name": "Soya Chunks Stir Fry", "description": "Economic high-protein snack", "calories": 300, "protein_g": 25, "carbs_g": 10, "fats_g": 15, "price_estimate": 20.0, "quantity": "1 cup (150g)"},
                {"meal_type": "dinner", "name": "Aloo Paratha & Curd", "description": "Wholesome stuffed parathas with homemade yogurt", "calories": 650, "protein_g": 15, "carbs_g": 85, "fats_g": 25, "price_estimate": 50.0, "quantity": "2 pieces (200g) + 1 cup (200g) curd"},
            ]
        },
        {
            "name": "Indian Heritage - Balanced",
            "description": "Economical balanced Indian nutrition with cultural staples.",
            "bmi_category": "normal",
            "calories_per_day": 2200,
            "protein_g": 110,
            "carbs_g": 275,
            "fats_g": 73,
            "meals": [
                {"meal_type": "breakfast", "name": "Masala Dosa & Sambar", "description": "Fermented rice pancake with potato filling", "calories": 450, "protein_g": 10, "carbs_g": 70, "fats_g": 15, "price_estimate": 40.0, "quantity": "1 large dosa (150g) + 1 cup (240ml) sambar"},
                {"meal_type": "snack", "name": "Boiled Eggs", "description": "High-quality affordable protein", "calories": 155, "protein_g": 13, "carbs_g": 1, "fats_g": 11, "price_estimate": 12.0, "quantity": "2 large eggs (100g)"},
                {"meal_type": "lunch", "name": "Red Rice & Avial", "description": "Kerala red rice with mixed vegetable coconut stew", "calories": 650, "protein_g": 20, "carbs_g": 85, "fats_g": 25, "price_estimate": 60.0, "quantity": "1.5 cups (300g) rice + 1 cup (200g) avial"},
                {"meal_type": "snack", "name": "Roasted Peanuts", "description": "Budget-friendly healthy fats", "calories": 200, "protein_g": 8, "carbs_g": 6, "fats_g": 16, "price_estimate": 10.0, "quantity": "1/4 cup (30g)"},
                {"meal_type": "dinner", "name": "Chappathi & Dal Tadka", "description": "Whole wheat rotis with high-fiber yellow lentils", "calories": 745, "protein_g": 30, "carbs_g": 100, "fats_g": 20, "price_estimate": 45.0, "quantity": "3 pieces (150g) + 1 cup (200g) dal"},
            ]
        },
        {
            "name": "Indian Heritage - Weight Loss",
            "description": "Calorie-conscious Indian diet focusing on steamed preparations.",
            "bmi_category": "overweight",
            "calories_per_day": 1800,
            "protein_g": 120,
            "carbs_g": 180, "fats_g": 60,
            "meals": [
                {"meal_type": "breakfast", "name": "Oats Upma", "description": "Savory oats with carrots and beans", "calories": 350, "protein_g": 12, "carbs_g": 50, "fats_g": 10, "price_estimate": 30.0, "quantity": "1.5 cups (250g)"},
                {"meal_type": "snack", "name": "Green Gram Salad", "description": "Steamed and seasoned sprouted mung beans", "calories": 200, "protein_g": 14, "carbs_g": 30, "fats_g": 2, "price_estimate": 15.0, "quantity": "1 cup (150g)"},
                {"meal_type": "lunch", "name": "Idiyappam & Veg Curry", "description": "Steamed rice noodles with coconut-free vegetable curry", "calories": 450, "protein_g": 15, "carbs_g": 75, "fats_g": 10, "price_estimate": 45.0, "quantity": "3 small pieces (120g) + 1 cup (200ml) curry"},
                {"meal_type": "snack", "name": "Sambharam", "description": "Traditional spiced buttermilk", "calories": 80, "protein_g": 3, "carbs_g": 6, "fats_g": 3, "price_estimate": 8.0, "quantity": "1 big glass (300ml)"},
                {"meal_type": "dinner", "name": "Grilled Fish & Cabbage Thoran", "description": "Spicy grilled lean fish with stir-fried cabbage", "calories": 720, "protein_g": 50, "carbs_g": 25, "fats_g": 20, "price_estimate": 100.0, "quantity": "150g fish + 1.5 cups (200g) thoran"},
            ]
        },
        {
            "name": "Indian Heritage - Intensive",
            "description": "Very low-calorie, high-protein Indian management diet.",
            "bmi_category": "obese",
            "calories_per_day": 1600,
            "protein_g": 130,
            "carbs_g": 150, "fats_g": 53,
            "meals": [
                {"meal_type": "breakfast", "name": "Besan Chilla", "description": "Gram flour pancakes with lots of spinach", "calories": 300, "protein_g": 15, "carbs_g": 35, "fats_g": 10, "price_estimate": 25.0, "quantity": "2 medium pieces (140g)"},
                {"meal_type": "snack", "name": "Roasted Chana", "description": "Fiber-rich roasted chickpeas", "calories": 150, "protein_g": 8, "carbs_g": 20, "fats_g": 4, "price_estimate": 8.0, "quantity": "1/2 cup (50g)"},
                {"meal_type": "lunch", "name": "Kanji & Whole Payar", "description": "Minimal rice gruel with protein-rich green gram", "calories": 450, "protein_g": 22, "carbs_g": 65, "fats_g": 10, "price_estimate": 25.0, "quantity": "1 bowl (300ml) kanji + 1/2 cup (100g) payar"},
                {"meal_type": "snack", "name": "Cucumber Salad", "description": "Sliced cucumbers with black salt", "calories": 50, "protein_g": 1, "carbs_g": 8, "fats_g": 0, "price_estimate": 10.0, "quantity": "200g slices"},
                {"meal_type": "dinner", "name": "Soya Chunk Curry & Roti", "description": "High-protein meat substitute with single whole wheat roti", "calories": 650, "protein_g": 45, "carbs_g": 70, "fats_g": 15, "price_estimate": 35.0, "quantity": "1.5 cups (300g) curry + 1 roti (50g)"},
            ]
        }
    ]

    for plan_data in diet_plans_data:
        meals_data = plan_data.pop("meals")
        diet_plan = models_recommendations.DietPlan(**plan_data)
        db.add(diet_plan)
        db.flush()  # Get the ID
        
        for meal_data in meals_data:
            meal = models_recommendations.Meal(diet_plan_id=diet_plan.id, **meal_data)
            db.add(meal)
    
    db.commit()
    print(f"Seeded {len(diet_plans_data)} diet plans")

def seed_exercises():
    db = SessionLocal()
    
    exercises_data = [
        # Underweight - Focus on strength building
        {"name": "Push-ups", "description": "Standard push-ups for upper body strength", "category": "strength", "intensity": "moderate", "duration_minutes": 15, "calories_burned": 80, "bmi_category": "underweight", "equipment_needed": "None"},
        {"name": "Squats", "description": "Bodyweight squats for leg strength", "category": "strength", "intensity": "moderate", "duration_minutes": 15, "calories_burned": 85, "bmi_category": "underweight", "equipment_needed": "None"},
        {"name": "Light Jogging", "description": "Gentle jogging for cardio", "category": "cardio", "intensity": "low", "duration_minutes": 20, "calories_burned": 120, "bmi_category": "underweight", "equipment_needed": "None"},
        
        # Normal - Balanced fitness
        {"name": "Running", "description": "Moderate pace running", "category": "cardio", "intensity": "moderate", "duration_minutes": 30, "calories_burned": 300, "bmi_category": "normal", "equipment_needed": "Running shoes"},
        {"name": "Cycling", "description": "Outdoor or stationary cycling", "category": "cardio", "intensity": "moderate", "duration_minutes": 40, "calories_burned": 350, "bmi_category": "normal", "equipment_needed": "Bicycle"},
        {"name": "Yoga", "description": "Vinyasa or power yoga", "category": "flexibility", "intensity": "moderate", "duration_minutes": 45, "calories_burned": 200, "bmi_category": "normal", "equipment_needed": "Yoga mat"},
        {"name": "Weight Training", "description": "Full body weight training routine", "category": "strength", "intensity": "moderate", "duration_minutes": 45, "calories_burned": 250, "bmi_category": "normal", "equipment_needed": "Dumbbells"},
        
        # Overweight - Focus on calorie burning
        {"name": "Brisk Walking", "description": "Fast-paced walking", "category": "cardio", "intensity": "moderate", "duration_minutes": 45, "calories_burned": 250, "bmi_category": "overweight", "equipment_needed": "Walking shoes"},
        {"name": "Swimming", "description": "Lap swimming or water aerobics", "category": "cardio", "intensity": "moderate", "duration_minutes": 40, "calories_burned": 400, "bmi_category": "overweight", "equipment_needed": "Swimming pool"},
        {"name": "Elliptical Training", "description": "Low-impact cardio workout", "category": "cardio", "intensity": "moderate", "duration_minutes": 35, "calories_burned": 300, "bmi_category": "overweight", "equipment_needed": "Elliptical machine"},
        {"name": "Resistance Band Exercises", "description": "Full body resistance training", "category": "strength", "intensity": "low", "duration_minutes": 30, "calories_burned": 150, "bmi_category": "overweight", "equipment_needed": "Resistance bands"},
        
        # Obese - Low-impact, joint-friendly
        {"name": "Water Walking", "description": "Walking in shallow pool water", "category": "cardio", "intensity": "low", "duration_minutes": 30, "calories_burned": 180, "bmi_category": "obese", "equipment_needed": "Swimming pool"},
        {"name": "Chair Exercises", "description": "Seated exercises for mobility", "category": "strength", "intensity": "low", "duration_minutes": 25, "calories_burned": 100, "bmi_category": "obese", "equipment_needed": "Chair"},
        {"name": "Gentle Yoga", "description": "Beginner-friendly yoga poses", "category": "flexibility", "intensity": "low", "duration_minutes": 30, "calories_burned": 120, "bmi_category": "obese", "equipment_needed": "Yoga mat"},
        {"name": "Recumbent Bike", "description": "Low-impact cycling with back support", "category": "cardio", "intensity": "low", "duration_minutes": 30, "calories_burned": 200, "bmi_category": "obese", "equipment_needed": "Recumbent bike"},
    ]
    
    for exercise_data in exercises_data:
        exercise = models_recommendations.Exercise(**exercise_data)
        db.add(exercise)
    
    db.commit()
    print(f"Seeded {len(exercises_data)} exercises")

if __name__ == "__main__":
    print("Seeding database...")
    seed_diet_plans()
    seed_exercises()
    print("Database seeded successfully!")
