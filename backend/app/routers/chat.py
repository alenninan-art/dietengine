import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
import random
from ..routers.auth import get_current_user
from .. import models, models_recommendations
from ..database import get_db
import traceback

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# Initialize OpenAI Client
client = None
if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here":
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage(BaseModel):
    message: str

def get_bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"

# Fallback responses for common questions
CHAT_RESPONSES = [
    "To lose weight, it's important to maintain a calorie deficit while eating nutrient-dense foods.",
    "Protein is crucial for muscle repair. Try including chicken, tofu, or lentils in your meals.",
    "Brisk walking for 30 minutes a day is a great way to start your fitness journey.",
    "Hydration is key! Aim for 2-3 liters of water daily.",
    "I recommend tracking your macros. Aim for a balance of protein, carbs, and healthy fats.",
    "Consistency is more important than intensity when you're starting out.",
    "Don't forget to get 7-9 hours of sleep; it's when your body recovers and burns fat efficiently.",
]

@router.post("")
async def chat_with_ai(
    chat_input: ChatMessage,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI Chatbot endpoint using OpenAI with personalized logic.
    """
    user_msg = chat_input.message.lower().strip()
    
    if not user_msg:
        return {"reply": "I'm here to help! Ask me anything about your diet, exercises, or health goals."}

    try:
        # Personalization data
        name_parts = current_user.full_name.split() if current_user.full_name else []
        nickname = name_parts[0] if name_parts else "friend"
        goal = current_user.health_goals.lower() if current_user.health_goals else "improve your health"
        age = current_user.age
        gender = current_user.gender
        activity = str(current_user.activity_level).replace('_', ' ') if current_user.activity_level else "moderate"
        
        # Fitness Coaching Data
        workout_loc = current_user.workout_location or "Unknown"
        equipment = current_user.equipment_available or "Not specified"
        injuries = current_user.injuries_limitations or "No reported injuries"
        days_per_week = current_user.workout_days_per_week or 3
        
        # BMI calculation for response
        user_bmi = None
        bmi_cat = None
        if current_user.height and current_user.weight:
            height_m = current_user.height / 100
            user_bmi = current_user.weight / (height_m ** 2)
            bmi_cat = get_bmi_category(user_bmi)

        # Fetch context from database
        diet_context = ""
        exercise_context = ""
        if bmi_cat:
            plan = db.query(models_recommendations.DietPlan).filter(
                models_recommendations.DietPlan.bmi_category == bmi_cat
            ).first()
            if plan:
                meals = [f"{m.meal_type}: {m.name} ({m.quantity})" for m in plan.meals]
                diet_context = f"The user's recommended diet plan is '{plan.name}'. Meals: {', '.join(meals)}."
            
            exs = db.query(models_recommendations.Exercise).filter(
                models_recommendations.Exercise.bmi_category == bmi_cat
            ).limit(3).all()
            if exs:
                exercises = [f"{e.name} ({e.duration_minutes} min)" for e in exs]
                exercise_context = f"Recommended exercises: {', '.join(exercises)}."

        # Try OpenAI first if available
        if client:
            try:
                # Construct a rich system prompt
                system_prompt = (
                    f"You are the 'Diet Engine Expert AI & Fitness Coach', a professional health, nutrition, and fitness consultant. \n"
                    f"Current User Profile:\n"
                    f"- Name: {nickname}\n"
                    f"- Goal: {goal}\n"
                    f"- Age: {age if age else 'Unknown'}\n"
                    f"- Gender: {gender if gender else 'Unknown'}\n"
                    f"- Activity Level: {activity}\n"
                    f"- Workout Location: {workout_loc}\n"
                    f"- Equipment Available: {equipment}\n"
                    f"- Injuries or Limitations: {injuries}\n"
                    f"- Workout Days Per Week: {days_per_week}\n"
                )
                
                if user_bmi:
                    system_prompt += f"- BMI: {user_bmi:.1f} ({bmi_cat.capitalize()})\n"
                
                if diet_context:
                    system_prompt += f"- Integrated Diet Plan: {diet_context}\n"
                if exercise_context:
                    system_prompt += f"- Integrated Exercises: {exercise_context}\n"
                
                system_prompt += (
                    "\nFITNESS COACHING RULES:\n"
                    "1. Generate personalized exercise plans based on the user's goal, location, and equipment.\n"
                    "2. Adapt workouts: Fat Loss (Compound + Cardio, mod reps), Bulking (Progressive Overload, 6-12 reps), Maintenance (Balanced).\n"
                    "3. For Beginners: Simple movements, clear instructions, lower volume.\n"
                    "4. If injuries are mentioned, avoid stressing that area and suggest safer alternatives.\n"
                    "5. Ensure exercises are safe and realistic. Avoid extreme or unsafe training advice.\n"
                    "\nRESPONSE FORMAT FOR WORKOUT PLANS:\n"
                    "Workout Plan Title: (e.g., 5-Day Muscle Gain Split)\n"
                    "Weekly Structure:\n"
                    "Day 1 – [Focus]\n"
                    "Day 2 – [Focus]\n"
                    "...\n"
                    "For Each Workout Day:\n"
                    "Exercise Name: \n"
                    "Sets: __ \n"
                    "Reps: __ \n"
                    "Rest: __ seconds\n"
                    "...\n"
                    "Cardio Recommendation: (Type + Duration)\n"
                    "Progression Advice: (How to increase weight or reps weekly)\n"
                    "Safety Note: (Brief form and injury prevention advice)\n"
                    "\nGENERAL INSTRUCTIONS:\n"
                    "1. Be professional, motivating, and clear. Avoid unnecessary long explanations.\n"
                    "2. Reference the user's specific diet plan and meals when they ask for recommendations.\n"
                    "3. Emphasize traditional Indian and Kerala foods when discussing nutrition.\n"
                    "4. Keep responses concise and actionable."
                )

                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": chat_input.message}
                    ],
                    max_tokens=250,
                    temperature=0.7
                )
                return {
                    "reply": completion.choices[0].message.content,
                    "user": current_user.email
                }
            except Exception as e:
                print(f"OpenAI Error: {e}")
                # Fall through to rule-based logic

        # Fallback/Rule-based logic (if OpenAI fails or key is missing)
        response = ""
        
        # Protein specific queries
        if any(word in user_msg for word in ["protein", "protien", "amino"]):
            if "burger" in user_msg:
                response = "A typical beef burger contains about 20-25g of protein, while a chicken burger has around 18-22g. For a healthier high-protein option, I recommend grilled fish or lentils!"
            elif "egg" in user_msg:
                response = "One large egg contains approximately 6g of high-quality protein. It's a gold standard for protein bioavailability!"
            elif "chicken" in user_msg:
                response = "Chicken breast is excellent! It has about 31g of protein per 100g. I recommend it for muscle repair and satiety."
            else:
                response = f"Protein is crucial for your {goal}! Aim for 1.2g-1.6g of protein per kg of body weight. Good sources include eggs, lean meats, dal, and paneer."

        # Calorie specific queries
        elif any(word in user_msg for word in ["calorie", "calories", "kcal", "energy"]):
            if "burger" in user_msg:
                response = "A standard fast-food burger can range from 250 to over 600 calories. If you're targeting your goal of {goal}, consider a homemade version with whole-grain buns!"
            else:
                response = f"Managing calories is key to {goal}. Try tracking your meals to maintain a healthy balance. I can analyze your food photos in the 'AI Analysis' section if you'd like!"

        # Common greetings and social talk
        elif any(word in user_msg for word in ["hello", "hi", "hey", "greetings", "how are you"]):
            response = f"Hello {nickname}! I'm your Diet Engine Assistant, feeling great! How can I help you today with your journey to {goal}?"
        
        # Specific diet plan advice
        elif any(word in user_msg for word in ["diet recommendation", "what should i eat", "my diet", "suggest a meal", "recommend a diet", "food suggestions"]):
            if bmi_cat:
                plan = db.query(models_recommendations.DietPlan).filter(
                    models_recommendations.DietPlan.bmi_category == bmi_cat
                ).first()
                if plan:
                    meals_summary = ", ".join([f"{m.meal_type.capitalize()}: {m.name} ({m.quantity})" for m in plan.meals[:3]])
                    response = f"For your {bmi_cat} BMI category, I recommend the '{plan.name}'. Based on our system, your best meals are— {meals_summary}."
                else:
                    response = f"I'm sorry {nickname}, I couldn't find a specific diet plan for you right now, but focusing on protein-rich Kerala staples like Puttu or Kadala is highly recommended!"
            else:
                response = f"I'd love to give you a diet recommendation, {nickname}! Please complete your Profile Setup (Height, Weight, Age) first so I can calculate your requirements."

        # Exercises
        elif any(word in user_msg for word in ["exercise", "workout", "training", "gym", "activity"]):
            if exercise_context:
                response = f"Based on your profile, {nickname}, I recommend these: {exercise_context} Consistency is key!"
            else:
                response = "For general fitness, I recommend 30 minutes of brisk walking or light jogging daily. Please finish your profile for a customized plan!"

        # BMI information
        elif any(word in user_msg for word in ["bmi", "category", "body mass index", "weight"]):
            if user_bmi:
                response = f"Your current BMI is {user_bmi:.1f}, {nickname}. This places you in the '{bmi_cat.capitalize()}' category. We are targeting your goal: {goal}."
            else:
                response = f"I'd love to help with your BMI, {nickname}! Please enter your height and weight in your profile page first."

        # Cultural & Kerala Specifics
        elif any(word in user_msg for word in ["kerala", "culture", "traditional", "indian", "local"]):
            response = f"Traditional Kerala food like Red Rice, Avial, and Appam are incredible for your health, {nickname}! They are budget-friendly and nutrient-dense. I've integrated these into your recommendations."

        # Budget & Cost
        elif any(word in user_msg for word in ["budget", "cheap", "cost", "price", "expensive"]):
            response = f"Don't worry about the cost, {nickname}! Most of my recommendations focus on home-cooked staples like lentils, eggs, and local vegetables which are very affordable (often under ₹30 per meal)."

        # Hydration
        elif any(word in user_msg for word in ["water", "hydrate", "drink", "sambharam", "buttermilk"]):
            response = "Hydration is essential for metabolism! Try Sambharam (spiced buttermilk) with ginger and green chilies for a healthy, low-calorie Kerala-style drink."

        # Nutrition & Snacks
        elif any(word in user_msg for word in ["snack", "junk", "food", "eat", "hungry", "munch"]):
            if "healthy" in user_msg or "good" in user_msg:
                response = f"For healthy snacks, {nickname}, I recommend boiled eggs, sprouted mung bean salad (Payar), or roasted peanuts. They are high in protein and keep you full!"
            else:
                response = f"If you're looking for a quick bite, try to avoid deep-fried items like Samosas. Instead, a small bowl of fruit or some spiced buttermilk is a great choice for your goal to {goal}."

        # New Food Items Integration
        elif any(word in user_msg for word in ["biriyani", "biryani", "dosa", "alfham", "grilled"]):
            if "biriyani" in user_msg:
                response = "Chicken Masala Biriyani is a great treat! It has about 650 kcal and 28g of protein. Just be mindful of the portion size if you're on a weight loss plan."
            elif "dosa" in user_msg:
                response = "A Masala Dosa is roughly 420 kcal. It's a balanced meal with about 9g of protein. Pairing it with plenty of sambar increases the fiber content!"
            elif "alfham" in user_msg:
                response = "Alfham Grilled Chicken is an excellent high-protein choice (45g protein per quarter). It's much healthier than deep-fried chicken!"
            else:
                response = "Those are great local choices! I can give you exact nutritional details for them if you upload a photo in the AI Analysis section."

        # Appreciation
        elif any(word in user_msg for word in ["thank", "thanks", "great", "awesome", "good"]):
            response = f"You're very welcome, {nickname}! I'm happy to help you reach your goals. Is there anything else you want to know?"

        # AI identity
        elif any(word in user_msg for word in ["who are you", "what are you", "your name"]):
            response = "I am the Diet Engine Expert AI, your personal health and nutrition consultant. I'm here to guide you with diet plans, exercises, and AI analysis!"

        # Generic catch-all
        else:
            tip = random.choice(CHAT_RESPONSES)
            response = f"That's an interesting question! While I'm still learning, here's a professional tip: {tip}"
    
    except Exception as e:
        print(f"CRITICAL CHAT ERROR: {e}")
        traceback.print_exc()
        # Ensure we always return a valid response even on global failure
        return {
            "reply": "I'm having a bit of trouble processing that right now. Could you please try asking in a different way, or check back in a moment?", 
            "user": current_user.email
        }
    
    return {
        "reply": response,
        "user": current_user.email
    }
