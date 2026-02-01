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

@router.post("/")
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

    # Personalization data
    nickname = current_user.full_name.split()[0] if current_user.full_name else "friend"
    goal = current_user.health_goals.lower() if current_user.health_goals else "improve your health"
    age = current_user.age
    gender = current_user.gender
    activity = current_user.activity_level.replace('_', ' ') if current_user.activity_level else "moderate"
    
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
                f"You are the 'Diet Engine Expert AI', a professional health, nutrition, and fitness consultant. \n"
                f"Current User Profile:\n"
                f"- Name: {nickname}\n"
                f"- Goal: {goal}\n"
                f"- Age: {age if age else 'Unknown'}\n"
                f"- Gender: {gender if gender else 'Unknown'}\n"
                f"- Activity Level: {activity}\n"
            )
            
            if user_bmi:
                system_prompt += f"- BMI: {user_bmi:.1f} ({bmi_cat.capitalize()})\n"
            
            if diet_context:
                system_prompt += f"- Integrated Diet Plan: {diet_context}\n"
            if exercise_context:
                system_prompt += f"- Integrated Exercises: {exercise_context}\n"
            
            system_prompt += (
                "\nINSTRUCTIONS:\n"
                "1. Provide highly personalized, accurate, and scientifically-grounded advice.\n"
                "2. Reference the user's specific diet plan and meals when they ask for recommendations.\n"
                "3. Emphasize traditional Indian and Kerala foods (Puttu, Appam, Red Rice, Avial) as budget-friendly, high-nutrition options.\n"
                "4. Be empathetic but professional. Use the user's name occasionally.\n"
                "5. If asked about quantities, mention specific weights (grams) and measures (cups) as defined in our system.\n"
                "6. If you don't have enough data to be certain, recommend they check with a doctor or nutritionist.\n"
                "7. Keep responses concise (under 200 words) and actionable."
            )

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
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
    
    # Common greetings and social talk
    if any(word in user_msg for word in ["hello", "hi", "hey", "greetings", "how are you"]):
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
    
    return {
        "reply": response,
        "user": current_user.email
    }
