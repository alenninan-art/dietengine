import os
import random
import traceback
import re

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
import google.generativeai as genai
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, models_recommendations
from ..database import get_db
from ..llm_config import get_openai_client, get_openai_settings
from ..routers.auth import get_current_user

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        # Use gemini-1.5-flash for the best free-tier balance
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Gemini Init Error: {e}")
        return None


class ChatMessage(BaseModel):
    message: str


def get_bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obese"


CHAT_RESPONSES = [
    "To lose weight, it's important to maintain a calorie deficit while eating nutrient-dense foods.",
    "Protein is crucial for muscle repair. Try including chicken, tofu, or lentils in your meals.",
    "Brisk walking for 30 minutes a day is a great way to start your fitness journey.",
    "Hydration is key! Aim for 2-3 liters of water daily.",
    "I recommend tracking your macros. Aim for a balance of protein, carbs, and healthy fats.",
    "Consistency is more important than intensity when you're starting out.",
    "Don't forget to get 7-9 hours of sleep; it's when your body recovers and burns fat efficiently.",
    "Small changes lead to big results. Focus on one habit at a time!",
    "Processed foods often contain hidden sugars. Try to stick to whole foods when possible.",
    "Fiber-rich foods like vegetables and oats keep you full longer and help with digestion.",
]

DIET_KEYWORDS = [
    "diet", "food", "eat", "meal", "nutrition", "recommendation", "weight loss",
    "lose weight", "reduce weight", "reducing weight", "fat loss", "burn fat",
]
WORKOUT_KEYWORDS = ["exercise", "exercises", "workout", "workouts", "training", "gym", "activity", "cardio", "strength"]
BMI_KEYWORDS = ["bmi", "body mass index", "my weight", "check my weight", "current weight"]
PROTEIN_KEYWORDS = ["protein", "protien", "amino"]
CALORIE_KEYWORDS = ["calorie", "calories", "kcal", "energy"]
PREWORKOUT_KEYWORDS = ["preworkout", "pre workout", "pre-workout", "before workout", "before gym", "before training"]
SNACK_KEYWORDS = ["snack", "snacks", "hungry", "munch", "munching", "light food", "evening snack"]
PLAN_REQUEST_KEYWORDS = [
    "diet plan", "meal plan", "weight loss plan", "lose weight", "reduce weight",
    "reducing weight", "weight reducing", "give me diet", "full plan",
]

HEALTHY_SNACK_SUGGESTIONS = [
    "boiled eggs with cucumber",
    "fruit with curd",
    "sprouts salad",
    "roasted chana or peanuts",
    "paneer pepper bites",
    "buttermilk with a small handful of nuts",
]


def has_any_keyword(message: str, keywords: list[str]) -> bool:
    return any(keyword in message for keyword in keywords)


def user_asked_for_tips(message: str) -> bool:
    return has_any_keyword(message, ["tip", "tips", "advice", "guidance", "suggest", "suggestion"])


def build_general_fallback_response(message: str) -> str:
    if has_any_keyword(message, PREWORKOUT_KEYWORDS):
        return (
            "Pre-Workout:\n"
            "- Eat a light snack 30-90 minutes before training, like a banana with curd, oats, or toast with peanut butter.\n"
            "Tip:\n"
            "- If you use a pre-workout supplement, start with a low dose and avoid taking it late in the evening."
        )
    if "oats" in message:
        return "Diet:\n- Oats are a good breakfast choice because they are filling and high in fiber."
    if "breakfast" in message:
        return "Diet:\n- A balanced breakfast with protein and fiber can help you stay full longer."
    if "lunch" in message or "dinner" in message:
        return "Diet:\n- Try to build meals around protein, vegetables, and a moderate portion of carbs."
    if "water" in message or "hydrate" in message:
        return "Hydration:\n- Aim to sip water through the day and drink extra around workouts."
    if "sleep" in message:
        return "Recovery:\n- Good sleep supports hunger control, recovery, and consistent progress."
    return (
        "Diet:\n"
        "- Focus on simple, balanced meals with protein, fiber, and enough water.\n"
        "Tip:\n"
        "- Ask me for a diet plan, workout plan, or calorie estimate for more specific help."
    )


def get_requested_workout_location(message: str, fallback_location: str) -> str:
    if "gym" in message:
        return "Gym"
    if "home" in message or "house" in message:
        return "Home"
    return fallback_location


def format_meal_list(plan: models_recommendations.DietPlan) -> str:
    meals = []
    for meal in plan.meals:
        quantity = f" ({meal.quantity})" if meal.quantity else ""
        meals.append(f"- {meal.meal_type.capitalize()}: {meal.name}{quantity}")
    return "\n".join(meals)


def format_exercise_list(exercises: list[models_recommendations.Exercise]) -> str:
    lines = []
    for exercise in exercises:
        equipment = f" | Equipment: {exercise.equipment_needed}" if exercise.equipment_needed else ""
        lines.append(
            f"- {exercise.name}: {exercise.duration_minutes} min, {exercise.intensity} intensity{equipment}"
        )
    return "\n".join(lines)


def search_food_catalog(db: Session, message: str, limit: int = 3) -> list[models_recommendations.FoodItem]:
    keywords = [word for word in re.findall(r"[a-zA-Z]+", message.lower()) if len(word) >= 3]
    if keywords:
        filters = []
        for keyword in keywords[:6]:
            like = f"%{keyword}%"
            filters.extend([
                models_recommendations.FoodItem.name.ilike(like),
                models_recommendations.FoodItem.ingredients.ilike(like),
                models_recommendations.FoodItem.course.ilike(like),
            ])
        return db.query(models_recommendations.FoodItem).filter(or_(*filters)).limit(limit).all()

    return db.query(models_recommendations.FoodItem).limit(limit).all()


def build_food_catalog_response(items: list[models_recommendations.FoodItem]) -> str:
    if not items:
        return "Diet:\n- I couldn't find matching Kerala dishes in the food catalog right now."

    lines = ["Kerala Foods:"]
    for item in items[:3]:
        course = f" ({item.course})" if item.course else ""
        diet = f" - {item.diet}" if item.diet else ""
        lines.append(f"- {item.name}{course}{diet}")
    return "\n".join(lines)


def build_diet_response(
    nickname: str,
    goal: str,
    bmi_cat: str | None,
    plan: models_recommendations.DietPlan | None,
    user_msg: str,
) -> str:
    if not bmi_cat:
        return (
            f"I'd love to give you a diet recommendation for your goal ({goal}), {nickname}! "
            "Please complete your Profile Setup (Height, Weight, Age) first so I can calculate your requirements."
        )

    if not plan:
        return (
            f"I'm sorry {nickname}, I couldn't find a specific diet plan for you right now, "
            "but focusing on protein-rich Kerala staples like Puttu, Kadala, eggs, and curd rice is a good start."
        )

    meals = format_meal_list(plan).splitlines()[:2]
    response_lines = [
        "Diet:",
        f"- Plan: {plan.name}",
    ]
    response_lines.extend(meals)
    if user_asked_for_tips(user_msg):
        response_lines.extend([
            "Tip:",
            "- Keep dinner light and avoid sugary drinks.",
        ])
    return "\n".join(response_lines)


def build_workout_response(
    nickname: str,
    goal: str,
    exercises: list[models_recommendations.Exercise],
    workout_loc: str,
    equipment: str,
    injuries: str,
    days_per_week: int,
    user_msg: str,
) -> str:
    if not exercises:
        return (
            "For general fitness, I recommend 30 minutes of brisk walking or light jogging daily. "
            "Please finish your profile for a more customized plan."
        )

    top_exercises = format_exercise_list(exercises).splitlines()[:2]
    requested_location = get_requested_workout_location(user_msg, workout_loc)
    response_lines = [
        "Workout:",
        f"- {days_per_week} days per week",
        f"- Place: {requested_location}",
    ]
    response_lines.extend(top_exercises)
    if user_asked_for_tips(user_msg):
        response_lines.extend([
            "Tip:",
            "- Focus on good form and increase slowly.",
        ])
    return "\n".join(response_lines)


def build_preworkout_response(user_msg: str) -> str:
    wants_supplement = any(word in user_msg for word in ["supplement", "powder", "caffeine", "drink", "booster"])
    wants_meal = any(word in user_msg for word in ["eat", "food", "meal", "snack", "banana", "oats", "bread", "toast"])

    if wants_supplement and wants_meal:
        return (
            "Pre-Workout:\n"
            "- A light carb snack like banana, toast, or oats 30-90 minutes before training works well.\n"
            "- If you use a pre-workout supplement, start with a low dose and check your caffeine tolerance.\n"
            "Tip:\n"
            "- Avoid high-stimulant pre-workouts close to bedtime and drink water before training."
        )

    if wants_supplement:
        return (
            "Pre-Workout Supplement:\n"
            "- Start with a low dose to assess tolerance, especially if it contains caffeine.\n"
            "- Avoid mixing multiple stimulant products and do not use it late in the evening.\n"
            "Tip:\n"
            "- If you feel jittery, reduce the dose or switch to a simple pre-workout snack instead."
        )

    return (
        "Pre-Workout:\n"
        "- Good options are banana with peanut butter, oats with curd, or toast with eggs 30-90 minutes before training.\n"
        "- Keep it light so you have energy without feeling too full during the workout.\n"
        "Tip:\n"
        "- Add water before your session, especially if you train in the heat."
    )


def build_snack_response(user_msg: str) -> str:
    wants_healthy = any(word in user_msg for word in ["healthy", "good", "best", "protein", "weight loss", "low calorie"])
    snack_list = ", ".join(HEALTHY_SNACK_SUGGESTIONS)

    if wants_healthy:
        return (
            "Snacks:\n"
            f"- Try {snack_list}.\n"
            "Tip:\n"
            "- Pick one protein or fiber-rich snack and keep fried bakery snacks for occasional cravings."
        )

    return (
        "Snacks:\n"
        "- Better snack swaps are fruit, buttermilk, boiled eggs, roasted chana, sprouts salad, or a small curd bowl.\n"
        "Tip:\n"
        "- If you get hungry often, add more protein to your main meals so snack cravings stay lower."
    )


def build_combined_plan_response(
    nickname: str,
    goal: str,
    bmi_cat: str | None,
    plan: models_recommendations.DietPlan | None,
    exercises: list[models_recommendations.Exercise],
    workout_loc: str,
    equipment: str,
    injuries: str,
    days_per_week: int,
    user_msg: str,
) -> str:
    diet_part = build_diet_response(nickname, goal, bmi_cat, plan, user_msg)
    workout_part = build_workout_response(
        nickname, goal, exercises, workout_loc, equipment, injuries, days_per_week, user_msg
    )
    return f"{diet_part}\n\n{workout_part}"


@router.post("")
async def chat_with_ai(
    chat_input: ChatMessage,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    AI chatbot endpoint using Google Gemini (Priority) or OpenAI with a rule-based fallback.
    """
    user_msg = chat_input.message.lower().strip()

    if not user_msg:
        return {"reply": "I'm here to help! Ask me anything about your diet, exercises, or health goals."}

    try:
        name_parts = current_user.full_name.split() if current_user.full_name else []
        nickname = name_parts[0] if name_parts else "friend"
        goal = current_user.health_goals.lower() if current_user.health_goals else "improve your health"
        age = current_user.age
        gender = current_user.gender
        activity = str(current_user.activity_level).replace("_", " ") if current_user.activity_level else "moderate"

        workout_loc = current_user.workout_location or "Unknown"
        equipment = current_user.equipment_available or "Not specified"
        injuries = current_user.injuries_limitations or "No reported injuries"
        days_per_week = current_user.workout_days_per_week or 3

        requested_workout_loc = get_requested_workout_location(user_msg, workout_loc)

        user_bmi = None
        bmi_cat = None
        if current_user.height and current_user.weight:
            height_m = current_user.height / 100
            user_bmi = current_user.weight / (height_m ** 2)
            bmi_cat = get_bmi_category(user_bmi)

        plan = None
        exercises: list[models_recommendations.Exercise] = []
        diet_context = ""
        exercise_context = ""
        if bmi_cat:
            plan = db.query(models_recommendations.DietPlan).filter(
                models_recommendations.DietPlan.bmi_category == bmi_cat
            ).first()
            if plan:
                meal_summaries = [f"{meal.meal_type}: {meal.name} ({meal.quantity})" for meal in plan.meals]
                diet_context = f"The user's recommended diet plan is '{plan.name}'. Meals: {', '.join(meal_summaries)}."

            exercise_query = db.query(models_recommendations.Exercise).filter(
                models_recommendations.Exercise.bmi_category == bmi_cat
            )
            if requested_workout_loc in ["Gym", "Home"]:
                exercise_query = exercise_query.filter(
                    (models_recommendations.Exercise.location_type == requested_workout_loc) |
                    (models_recommendations.Exercise.location_type == "Any")
                )
            exercises = exercise_query.limit(4).all()
            if not exercises:
                exercises = db.query(models_recommendations.Exercise).filter(
                    models_recommendations.Exercise.bmi_category == bmi_cat
                ).limit(4).all()
            if exercises:
                exercise_items = [f"{exercise.name} ({exercise.duration_minutes} min)" for exercise in exercises]
                exercise_context = f"Recommended exercises: {', '.join(exercise_items)}."

        response = ""
        asks_for_diet = has_any_keyword(user_msg, DIET_KEYWORDS)
        asks_for_workout = has_any_keyword(user_msg, WORKOUT_KEYWORDS)
        asks_for_bmi = has_any_keyword(user_msg, BMI_KEYWORDS)
        asks_for_preworkout = has_any_keyword(user_msg, PREWORKOUT_KEYWORDS)
        asks_for_plan = has_any_keyword(user_msg, PLAN_REQUEST_KEYWORDS)
        asks_for_kerala_foods = any(
            word in user_msg for word in ["kerala", "culture", "traditional", "indian", "local", "recipe", "dish", "dishes"]
        )

        if asks_for_preworkout:
            response = build_preworkout_response(user_msg)

        elif asks_for_plan and asks_for_workout:
            response = build_combined_plan_response(
                nickname,
                goal,
                bmi_cat,
                plan,
                exercises,
                workout_loc,
                equipment,
                injuries,
                days_per_week,
                user_msg,
            )

        elif asks_for_workout and not asks_for_diet and not asks_for_plan:
            response = build_workout_response(
                nickname, goal, exercises, workout_loc, equipment, injuries, days_per_week, user_msg
            )

        elif asks_for_plan or user_msg in ["i want to lose weight", "lose weight", "weight loss", "weight reducing tips"]:
            response = build_diet_response(nickname, goal, bmi_cat, plan, user_msg)

        elif asks_for_kerala_foods:
            response = build_food_catalog_response(search_food_catalog(db, user_msg))

        elif asks_for_preworkout:
            response = build_preworkout_response(user_msg)

        if response:
            return {
                "reply": response,
                "user": current_user.email,
                "is_fallback": True,
            }

        # Prioritize Google Gemini (Free Tier Friendly)
        gemini_model = get_gemini_model()
        if gemini_model:
            try:
                system_prompt = (
                    "You are the 'Diet Engine Expert AI & Fitness Coach', a professional health, nutrition, and fitness consultant.\n"
                    "Current User Profile:\n"
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
                    "\nYou are an intelligent and friendly diet assistant chatbot.\n"
                    "Your goal is to provide clear, accurate, and helpful responses related to diet, nutrition, fitness, and healthy lifestyle.\n"
                    "Guidelines:\n"
                    "- Always give short, clear, and easy-to-understand answers.\n"
                    "- Respond in a friendly and conversational tone.\n"
                    "- Provide practical diet suggestions when possible.\n"
                    "- You can suggest pre-workout meals and basic pre-workout supplement safety guidance.\n"
                    "- Use simple language suitable for beginners.\n"
                    "- If the question is unclear, ask a follow-up question.\n"
                    "- Give personalized suggestions based on age, weight, and goal when available.\n"
                    "- Avoid medical advice; suggest consulting a professional when needed.\n"
                    "- Keep responses concise: 3-5 lines max.\n"
                    "- Stay focused only on diet, nutrition, and fitness topics.\n"
                    "- If the user asks about both diet and workout, answer both in the same response.\n"
                    "- If the user asks for a diet plan or weight-loss plan, include a real diet plan when available.\n"
                    "- Use section labels like Diet, Workout, and Tip when useful."
                )

                # Gemini handles system instructions slightly differently or as part of the content
                full_prompt = f"{system_prompt}\n\nUser Question: {chat_input.message}"
                
                response_gen = gemini_model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=250,
                        temperature=0.4,
                    )
                )
                
                return {
                    "reply": response_gen.text.strip(),
                    "user": current_user.email,
                    "is_fallback": False,
                    "provider": "gemini"
                }
            except Exception as gem_err:
                print(f"Gemini API Error: {gem_err}")
                # Fall through to OpenAI if Gemini fails

        client = get_openai_client()
        if client:
            try:
                openai_settings = get_openai_settings()
                system_prompt = (
                    "You are the 'Diet Engine Expert AI & Fitness Coach', a professional health, nutrition, and fitness consultant.\n"
                    "Current User Profile:\n"
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
                    "\nYou are an intelligent and friendly diet assistant chatbot.\n"
                    "Your goal is to provide clear, accurate, and helpful responses related to diet, nutrition, fitness, and healthy lifestyle.\n"
                    "Guidelines:\n"
                    "- Always give short, clear, and easy-to-understand answers.\n"
                    "- Respond in a friendly and conversational tone.\n"
                    "- Provide practical diet suggestions when possible.\n"
                    "- You can suggest pre-workout meals and basic pre-workout supplement safety guidance.\n"
                    "- Use simple language suitable for beginners.\n"
                    "- If the question is unclear, ask a follow-up question.\n"
                    "- Give personalized suggestions based on age, weight, and goal when available.\n"
                    "- Avoid medical advice; suggest consulting a professional when needed.\n"
                    "- Keep responses concise: 3-5 lines max.\n"
                    "- Stay focused only on diet, nutrition, and fitness topics.\n"
                    "- If the user asks about both diet and workout, answer both in the same response.\n"
                    "- If the user asks for a diet plan or weight-loss plan, include a real diet plan when available.\n"
                    "- Use section labels like Diet, Workout, and Tip when useful."
                )

                completion = client.chat.completions.create(
                    model=openai_settings["model"] or "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": chat_input.message},
                    ],
                    max_tokens=220,
                    temperature=0.4,
                )
                return {
                    "reply": completion.choices[0].message.content,
                    "user": current_user.email,
                    "is_fallback": False,
                    "provider": openai_settings["provider"] or "openai"
                }
            except Exception as exc:
                print(f"OpenAI Error: {exc}")

        if asks_for_diet and asks_for_workout:
            response = build_combined_plan_response(
                nickname,
                goal,
                bmi_cat,
                plan,
                exercises,
                workout_loc,
                equipment,
                injuries,
                days_per_week,
                user_msg,
            )

        elif has_any_keyword(user_msg, PROTEIN_KEYWORDS):
            if "burger" in user_msg:
                response = "Food:\n- A burger has about 18-25g protein."
            elif "egg" in user_msg:
                response = "Food:\n- One egg has about 6g protein."
            elif "chicken" in user_msg:
                response = "Food:\n- Chicken breast has about 31g protein per 100g."
            else:
                response = "Diet:\n- Good protein foods are eggs, chicken, dal, paneer, and curd."

        elif has_any_keyword(user_msg, CALORIE_KEYWORDS):
            if "burger" in user_msg:
                response = "Diet:\n- A burger can range from about 250 to 600+ calories."
            else:
                response = "Diet:\n- To lose weight, eat a little less than you burn each day."

        elif any(word in user_msg for word in ["hello", "hi", "hey", "greetings", "how are you"]):
            response = f"Hello {nickname}!\nI can help with diet and fitness."

        elif asks_for_diet:
            response = build_diet_response(nickname, goal, bmi_cat, plan, user_msg)

        elif asks_for_preworkout:
            response = build_preworkout_response(user_msg)

        elif asks_for_workout:
            response = build_workout_response(
                nickname, goal, exercises, workout_loc, equipment, injuries, days_per_week, user_msg
            )

        elif asks_for_bmi:
            if user_bmi:
                response = (
                    "Body Status:\n"
                    f"- Your BMI is {user_bmi:.1f}.\n"
                    f"- Category: {bmi_cat}\n"
                    f"- Goal: {goal}"
                )
            else:
                response = f"I'd love to help with your BMI, {nickname}! Please enter your height and weight in your profile page first."

        elif any(word in user_msg for word in ["budget", "cheap", "cost", "price", "expensive"]):
            response = "Diet:\n- Budget-friendly foods are eggs, dal, curd, oats, bananas, peanuts, and vegetables."

        elif any(word in user_msg for word in ["water", "hydrate", "drink", "sambharam", "buttermilk"]):
            response = "Hydration:\n- Drink enough water through the day.\n- Buttermilk and lemon water are good low-calorie choices."

        elif has_any_keyword(user_msg, SNACK_KEYWORDS) or "junk" in user_msg:
            response = build_snack_response(user_msg)

        elif any(word in user_msg for word in ["biriyani", "biryani", "dosa", "alfham", "grilled"]):
            if "biriyani" in user_msg or "biryani" in user_msg:
                response = "Diet:\n- Chicken biryani is okay sometimes, but keep the portion moderate."
            elif "dosa" in user_msg:
                response = "Diet:\n- Masala dosa is fine once in a while. Eat it with sambar for better balance."
            elif "alfham" in user_msg:
                response = "Diet:\n- Alfham grilled chicken is usually better than fried chicken."
            else:
                response = "Diet:\n- These foods can fit into your plan depending on portion size and frequency."

        elif any(word in user_msg for word in ["thank", "thanks", "great", "awesome"]):
            response = f"You're welcome, {nickname}!"

        elif any(word in user_msg for word in ["who are you", "what are you", "your name"]):
            response = "I am your diet and fitness assistant."

        else:
            response = build_general_fallback_response(user_msg)

    except Exception as exc:
        print(f"CRITICAL CHAT ERROR: {exc}")
        traceback.print_exc()
        return {
            "reply": "I'm having a bit of trouble processing that right now. Could you please try asking in a different way, or check back in a moment?",
            "user": current_user.email,
            "is_fallback": True,
            "error_type": "critical",
        }

    return {
        "reply": response,
        "user": current_user.email,
        "is_fallback": True,
    }
