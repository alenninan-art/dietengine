from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models_recommendations

def seed_database(db: Session):
    print("Auto-seeding database with Indian & Kerala culture diet plans...")
    
    # Remove existing diet plans and meals to avoid duplicates
    db.query(models_recommendations.Meal).delete()
    db.query(models_recommendations.DietPlan).delete()
    db.flush()
    
    # Diet Plans Data
    diet_plans_data = [
        {
            "name": "Indian Heritage - Weight Gain",
            "description": "High-calorie Kerala nutrition featuring rich, traditional delicacies for weight gain.",
            "bmi_category": "underweight",
            "calories_per_day": 2800,
            "protein_g": 140,
            "carbs_g": 350,
            "fats_g": 93,
            "meals": [
                {"meal_type": "breakfast", "name": "Appam & Kerala Chicken Stew", "description": "Laced rice pancakes with rich coconut milk chicken stew", "calories": 650, "protein_g": 30, "carbs_g": 75, "fats_g": 25, "price_estimate": 100.0, "quantity": "3 Appams + 1.5 cups Stew"},
                {"meal_type": "lunch", "name": "Malabar Chicken Biriyani", "description": "Authentic fragrant kaima rice biriyani with chicken masala", "calories": 950, "protein_g": 45, "carbs_g": 110, "fats_g": 40, "price_estimate": 160.0, "quantity": "1 Full Portion (500g)"},
                {"meal_type": "snack", "name": "Pazham Pori & Chaya", "description": "Classic Kerala sweet banana fritters with tea", "calories": 400, "protein_g": 5, "carbs_g": 75, "fats_g": 12, "price_estimate": 40.0, "quantity": "2 Fritters + 1 Cup Tea"},
                {"meal_type": "dinner", "name": "Kerala Porotta & Beef Ularthiyathu", "description": "Flaky layered flatbread with spicy slow-roasted beef", "calories": 800, "protein_g": 45, "carbs_g": 80, "fats_g": 35, "price_estimate": 150.0, "quantity": "2 Porottas + 200g Beef Roast"},
            ]
        },
        {
            "name": "Indian Heritage - Balanced",
            "description": "Balanced, wholesome traditional Kerala meals.",
            "bmi_category": "normal",
            "calories_per_day": 2200,
            "protein_g": 110,
            "carbs_g": 275,
            "fats_g": 73,
            "meals": [
                {"meal_type": "breakfast", "name": "Puttu & Kadala Curry", "description": "Iconic steamed rice cake with rich black chickpea curry", "calories": 500, "protein_g": 18, "carbs_g": 85, "fats_g": 12, "price_estimate": 60.0, "quantity": "2 pieces Puttu + 1 cup Kadala Curry"},
                {"meal_type": "lunch", "name": "Kerala Sadya (Mini)", "description": "Traditional feast with Matta rice, Sambar, Avial, and Thoran", "calories": 800, "protein_g": 20, "carbs_g": 120, "fats_g": 25, "price_estimate": 120.0, "quantity": "Standard Sadya Banana Leaf Meal"},
                {"meal_type": "snack", "name": "Ela Ada", "description": "Steamed rice parcel with coconut and jaggery wrapped in banana leaf", "calories": 300, "protein_g": 4, "carbs_g": 60, "fats_g": 8, "price_estimate": 30.0, "quantity": "1 Large Ada"},
                {"meal_type": "dinner", "name": "Pathiri & Kerala Meen Curry", "description": "Soft rice flatbreads with traditional spicy fish curry", "calories": 600, "protein_g": 35, "carbs_g": 70, "fats_g": 18, "price_estimate": 110.0, "quantity": "4 Pathiris + 150g Fish Curry"},
            ]
        },
        {
            "name": "Indian Heritage - Weight Loss",
            "description": "Calorie-conscious traditional Kerala diet focusing on steamed preparations.",
            "bmi_category": "overweight",
            "calories_per_day": 1800,
            "protein_g": 120,
            "carbs_g": 180,
            "fats_g": 60,
            "meals": [
                {"meal_type": "breakfast", "name": "Idiyappam & Vegetable Stew", "description": "String hoppers with light coconut milk vegetable stew", "calories": 350, "protein_g": 8, "carbs_g": 60, "fats_g": 10, "price_estimate": 50.0, "quantity": "3 Idiyappams + 1 cup Veg Stew"},
                {"meal_type": "lunch", "name": "Matta Rice, Moru & Mathi Peera", "description": "High-fiber red rice, spiced buttermilk, and crumbled sardine with coconut", "calories": 550, "protein_g": 35, "carbs_g": 65, "fats_g": 15, "price_estimate": 80.0, "quantity": "1.5 cups Matta Rice + Moru + 1 cup Mathi Peera"},
                {"meal_type": "snack", "name": "Cherupayar Sundal (Green Gram)", "description": "Boiled and tempered green gram with fresh coconut", "calories": 200, "protein_g": 12, "carbs_g": 35, "fats_g": 4, "price_estimate": 25.0, "quantity": "1 cup (150g)"},
                {"meal_type": "dinner", "name": "Godhambu (Wheat) Dosa & Tomato Chutney", "description": "Instant whole wheat crepe with tangy local chutney", "calories": 400, "protein_g": 12, "carbs_g": 65, "fats_g": 8, "price_estimate": 40.0, "quantity": "3 Wheat Dosas + Chutney"},
            ]
        },
        {
            "name": "Indian Heritage - Intensive",
            "description": "Very low-calorie, high-protein Kerala-style diet prioritizing seafood and lean meats.",
            "bmi_category": "obese",
            "calories_per_day": 1600,
            "protein_g": 130,
            "carbs_g": 150,
            "fats_g": 53,
            "meals": [
                {"meal_type": "breakfast", "name": "Kerala Mutta Roast & 1 Appam", "description": "Spicy onion and tomato egg roast with a single rice pancake", "calories": 350, "protein_g": 18, "carbs_g": 35, "fats_g": 15, "price_estimate": 60.0, "quantity": "1 Appam + 2 Eggs in Roast"},
                {"meal_type": "lunch", "name": "Karimeen Pollichathu", "description": "Premium pearl spot fish marinated and baked in banana leaf", "calories": 400, "protein_g": 45, "carbs_g": 15, "fats_g": 18, "price_estimate": 250.0, "quantity": "1 Large Karimeen with masala"},
                {"meal_type": "snack", "name": "Sambharam (Spiced Buttermilk)", "description": "Refreshing probiotic drink with ginger, green chilli, and curry leaves", "calories": 50, "protein_g": 3, "carbs_g": 5, "fats_g": 2, "price_estimate": 15.0, "quantity": "1 Large Glass"},
                {"meal_type": "dinner", "name": "Alfaham Chicken with Salad", "description": "Arabian-influenced Kerala-style spicy grilled chicken", "calories": 450, "protein_g": 50, "carbs_g": 15, "fats_g": 20, "price_estimate": 160.0, "quantity": "Half Chicken (dry) + Cucumber/Carrot Salad"},
            ]
        }
    ]

    for plan_data in diet_plans_data:
        meals_data = plan_data.pop("meals")
        diet_plan = models_recommendations.DietPlan(**plan_data)
        db.add(diet_plan)
        db.flush()
        for meal_data in meals_data:
            meal = models_recommendations.Meal(diet_plan_id=diet_plan.id, **meal_data)
            db.add(meal)
            
    # Exercises Data
    exercises_data = [
        # Underweight (Focus on Strength & Muscle Growth)
        {"name": "Dumbbell Press", "description": "Classic chest press for upper body development", "category": "strength", "intensity": "moderate", "duration_minutes": 15, "calories_burned": 100, "bmi_category": "underweight", "equipment_needed": "Dumbbells", "location_type": "Gym"},
        {"name": "Bodyweight Squats", "description": "Foundation exercise for leg and glute strength", "category": "strength", "intensity": "moderate", "duration_minutes": 15, "calories_burned": 85, "bmi_category": "underweight", "equipment_needed": "None", "location_type": "Any"},
        {"name": "Push-ups", "description": "Essential upper body pushing movement", "category": "strength", "intensity": "moderate", "duration_minutes": 10, "calories_burned": 70, "bmi_category": "underweight", "equipment_needed": "None", "location_type": "Home"},
        {"name": "Seated Rows", "description": "Focus on back thickness and posture", "category": "strength", "intensity": "moderate", "duration_minutes": 15, "calories_burned": 90, "bmi_category": "underweight", "equipment_needed": "Cable Machine", "location_type": "Gym"},
        {"name": "Diamond Push-ups", "description": "Advanced push-up for triceps focus", "category": "strength", "intensity": "high", "duration_minutes": 10, "calories_burned": 80, "bmi_category": "underweight", "equipment_needed": "None", "location_type": "Home"},
        {"name": "Plank", "description": "Core stability for overall strength", "category": "flexibility", "intensity": "low", "duration_minutes": 5, "calories_burned": 25, "bmi_category": "underweight", "equipment_needed": "None", "location_type": "Any"},

        # Normal (Balanced - HIIT & Compound Movements)
        {"name": "Deadlift", "description": "Full body compound power movement", "category": "strength", "intensity": "high", "duration_minutes": 20, "calories_burned": 250, "bmi_category": "normal", "equipment_needed": "Barbell", "location_type": "Gym"},
        {"name": "Burpees", "description": "High-intensity full body explosive exercise", "category": "cardio", "intensity": "high", "duration_minutes": 15, "calories_burned": 180, "bmi_category": "normal", "equipment_needed": "None", "location_type": "Home"},
        {"name": "Kettlebell Swings", "description": "Hinge movement for power and endurance", "category": "strength", "intensity": "high", "duration_minutes": 15, "calories_burned": 200, "bmi_category": "normal", "equipment_needed": "Kettlebell", "location_type": "Gym"},
        {"name": "Jump Rope", "description": "Classic cardio for coordination and fat burn", "category": "cardio", "intensity": "high", "duration_minutes": 20, "calories_burned": 220, "bmi_category": "normal", "equipment_needed": "Jump Rope", "location_type": "Any"},
        {"name": "Brisk Walking", "description": "Effective steady-state cardio", "category": "cardio", "intensity": "moderate", "duration_minutes": 45, "calories_burned": 250, "bmi_category": "normal", "equipment_needed": "Walking shoes", "location_type": "Any"},
        {"name": "Cycling", "description": "Great for leg endurance and heart health", "category": "cardio", "intensity": "moderate", "duration_minutes": 40, "calories_burned": 320, "bmi_category": "normal", "equipment_needed": "Bicycle", "location_type": "Outdoors"},

        # Overweight (Burn Calories & Joint Health)
        {"name": "Elliptical Machine", "description": "Low impact, high calorie burn cardio", "category": "cardio", "intensity": "moderate", "duration_minutes": 30, "calories_burned": 350, "bmi_category": "overweight", "equipment_needed": "Elliptical", "location_type": "Gym"},
        {"name": "Walking Lunges", "description": "Builds functional leg strength and range", "category": "strength", "intensity": "moderate", "duration_minutes": 15, "calories_burned": 140, "bmi_category": "overweight", "equipment_needed": "None", "location_type": "Any"},
        {"name": "Incline Walking", "description": "Uphill walk for higher calorie burn", "category": "cardio", "intensity": "high", "duration_minutes": 30, "calories_burned": 400, "bmi_category": "overweight", "equipment_needed": "Treadmill", "location_type": "Gym"},
        {"name": "Step Aerobics", "description": "Fun rhythm-based calorie burner", "category": "cardio", "intensity": "moderate", "duration_minutes": 30, "calories_burned": 280, "bmi_category": "overweight", "equipment_needed": "Stepper", "location_type": "Home"},
        {"name": "Chair Squats", "description": "Safe, assisted movement for beginners", "category": "strength", "intensity": "low", "duration_minutes": 10, "calories_burned": 60, "bmi_category": "overweight", "equipment_needed": "Chair", "location_type": "Home"},
        {"name": "Aqua Jogging", "description": "Zero impact cardio in water", "category": "cardio", "intensity": "moderate", "duration_minutes": 30, "calories_burned": 220, "bmi_category": "overweight", "equipment_needed": "Pool", "location_type": "Any"},

        # Obese (Stability, Mobility & Low Impact)
        {"name": "Swimming", "description": "Buoyancy makes it the safest for joints", "category": "cardio", "intensity": "moderate", "duration_minutes": 30, "calories_burned": 300, "bmi_category": "obese", "equipment_needed": "Pool", "location_type": "Any"},
        {"name": "Stationary Bike", "description": "Classic safe cardio while seated", "category": "cardio", "intensity": "low", "duration_minutes": 20, "calories_burned": 150, "bmi_category": "obese", "equipment_needed": "Exercise Bike", "location_type": "Gym"},
        {"name": "Wall Push-ups", "description": "Reduced weight upper body work", "category": "strength", "intensity": "low", "duration_minutes": 10, "calories_burned": 40, "bmi_category": "obese", "equipment_needed": "Wall", "location_type": "Home"},
        {"name": "Arm Circles", "description": "Mobility and light toning", "category": "flexibility", "intensity": "low", "duration_minutes": 5, "calories_burned": 15, "bmi_category": "obese", "equipment_needed": "None", "location_type": "Any"},
        {"name": "Seated Marches", "description": "Low impact heart rate elevation", "category": "cardio", "intensity": "low", "duration_minutes": 15, "calories_burned": 80, "bmi_category": "obese", "equipment_needed": "Chair", "location_type": "Home"},
        {"name": "Slow Paced Walking", "description": "Consistent daily movement", "category": "cardio", "intensity": "low", "duration_minutes": 20, "calories_burned": 100, "bmi_category": "obese", "equipment_needed": "None", "location_type": "Any"},
    ]
    
    # Remove existing exercises to avoid duplicates
    db.query(models_recommendations.Exercise).delete()
    db.flush()

    for exercise_data in exercises_data:
        exercise = models_recommendations.Exercise(**exercise_data)
        db.add(exercise)
        
    db.commit()
    print("Database seeding completed.")
