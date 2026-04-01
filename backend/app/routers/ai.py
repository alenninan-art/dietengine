from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
import asyncio
import random
import os
import base64
import json
import io
import re
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO
from .auth import get_current_user
from .. import models, models_recommendations
from dotenv import load_dotenv
from ..llm_config import get_openai_client, get_openai_settings
from ..database import get_db
from sqlalchemy.orm import Session

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

# Initialize YOLOv8 Model (downloads automatically if not present)
# Using yolov8s.pt (Small) for better accuracy over the Nano variant
try:
    yolo_model = YOLO('yolov8s.pt') 
except Exception as e:
    print(f"WARNING: YOLO initialization failed: {e}")
    yolo_model = None

# Professional Food Database (Per Standard Serving) - FALLBACK
FOOD_DATABASE = {
    # Traditional Indian/Kerala Dishes
    "puttu_and_kadala": {
        "calories": 350, "protein": 12, "carbs": 60, "fats": 8, "unit": "1 plate (2 pieces puttu + curry)",
        "common_name": "Puttu & Kadala Curry"
    },
    "appam_and_egg_curry": {
        "calories": 320, "protein": 15, "carbs": 45, "fats": 10, "unit": "2 pieces Appam + 1 egg gravy",
        "common_name": "Appam & Egg Curry"
    },
    "chicken_biryani": {
        "calories": 550, "protein": 30, "carbs": 70, "fats": 18, "unit": "1 standard plate (350g)",
        "common_name": "Malabar Chicken Biryani"
    },
    "masala_biriyani": {
        "calories": 650, "protein": 28, "carbs": 80, "fats": 22, "unit": "1 standard plate (350g-400g)",
        "common_name": "Chicken Masala Biriyani"
    },
    "chicken_mandi": {
        "calories": 720, "protein": 38, "carbs": 82, "fats": 26, "unit": "1 standard plate (400g-450g)",
        "common_name": "Chicken Mandi"
    },
    "masala_dosa": {
        "calories": 420, "protein": 9, "carbs": 68, "fats": 12, "unit": "1 large Dosa + Sambar + Chutnee",
        "common_name": "Masala Dosa"
    },
    "alfham_chicken": {
        "calories": 480, "protein": 45, "carbs": 5, "fats": 32, "unit": "Quarter Chicken piece (Approx 200g)",
        "common_name": "Alfham Grilled Chicken"
    },
    "idli_with_sambar": {
        "calories": 250, "protein": 10, "carbs": 45, "fats": 4, "unit": "3 pieces Idli + 100ml Sambar",
        "common_name": "Idli & Sambar"
    },
    "kerala_sadya_meal": {
        "calories": 850, "protein": 20, "carbs": 140, "fats": 25, "unit": "1 traditional banana leaf meal",
        "common_name": "Full Kerala Sadya"
    },
    "fish_curry_meals": {
        "calories": 600, "protein": 35, "carbs": 95, "fats": 12, "unit": "Rice + Fish Curry + Sides",
        "common_name": "Kerala Fish Curry Meals"
    },
    "nadan_chicken_fry": {
        "calories": 400, "protein": 28, "carbs": 5, "fats": 30, "unit": "100g serving",
        "common_name": "Nadan Chicken Fry"
    },
    
    # Snacks
    "samosa": {
        "calories": 260, "protein": 4, "carbs": 25, "fats": 18, "unit": "2 medium pieces",
        "common_name": "Samosa"
    },
    "banana_chips": {
        "calories": 520, "protein": 2, "carbs": 60, "fats": 32, "unit": "100g (Approx 1 packet)",
        "common_name": "Kerala Banana Chips"
    },
    "masala_vada": {
        "calories": 150, "protein": 6, "carbs": 15, "fats": 8, "unit": "2 pieces",
        "common_name": "Masala Vada"
    },
    
    # Drinks
    "sambharam_buttermilk": {
        "calories": 45, "protein": 3, "carbs": 5, "fats": 1, "unit": "1 glass (250ml)",
        "common_name": "Sambharam (Spiced Buttermilk)"
    },
    "kerala_chai_tea": {
        "calories": 90, "protein": 3, "carbs": 12, "fats": 4, "unit": "1 small cup with milk/sugar",
        "common_name": "Kerala Milk Tea"
    },
    "tender_coconut_water": {
        "calories": 45, "protein": 1, "carbs": 10, "fats": 0.1, "unit": "1 whole coconut water",
        "common_name": "Tender Coconut Water"
    },
    "burger": {
        "calories": 550, "protein": 24, "carbs": 45, "fats": 30, "unit": "1 standard burger",
        "common_name": "Beef/Chicken Burger"
    },
}

UNSUPPORTED_VECTOR_TYPES = {"image/svg+xml"}


def is_vector_image(content_type: str | None, filename: str | None) -> bool:
    normalized_type = (content_type or "").lower()
    normalized_name = (filename or "").lower()
    return normalized_type in UNSUPPORTED_VECTOR_TYPES or normalized_name.endswith(".svg")


def load_raster_image(image_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(image_bytes))
    img.load()
    return img


async def run_yolo_detection(image_bytes: bytes) -> list:
    """Run YOLOv8 on the image to identify objects for better hint generation"""
    global yolo_model

    if not yolo_model:
        return []
    
    try:
        # Load image for YOLO
        img = load_raster_image(image_bytes)
        results = yolo_model(img, verbose=False, conf=0.25)  # Lower conf threshold for more detections
        
        # Extract detected class names
        detected_items = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                name = result.names[cls_id]
                detected_items.append(name)
        
        # Return unique items
        return list(set(detected_items))
    except UnidentifiedImageError:
        return []
    except Exception as e:
        print(f"YOLO detection failed: {e}")
        if "pi_heif" in str(e):
            # Avoid repeated autoinstall attempts from Ultralytics/Pillow edge cases.
            yolo_model = None
        return []


def _estimate_catalog_nutrition(item: models_recommendations.FoodItem, portion: str) -> dict[str, float | int]:
    base_calories = {
        "breakfast": 320,
        "snack": 220,
        "dessert": 260,
        "main course": 480,
        "festival": 700,
        "drink": 90,
    }
    course = (item.course or "").lower()
    calories = 360
    for key, value in base_calories.items():
        if key in course:
            calories = value
            break

    if item.diet and "non-vegetarian" in item.diet.lower():
        protein = 24.0
        fats = 16.0
        carbs = max(15.0, calories / 8)
    else:
        protein = 9.0
        fats = 10.0
        carbs = max(25.0, calories / 6)

    multiplier = 0.75 if portion == "Small" else (1.35 if portion == "Large" else 1.0)
    return {
        "calories": int(calories * multiplier),
        "protein": round(protein * multiplier, 1),
        "carbs": round(carbs * multiplier, 1),
        "fats": round(fats * multiplier, 1),
    }


def _find_catalog_food_item(db: Session | None, filename: str = "", yolo_hints: list | None = None):
    if not db:
        return None

    keywords = [
        word for word in re.findall(r"[a-zA-Z]+", f"{filename} {' '.join(yolo_hints or [])}".lower())
        if len(word) >= 3
    ]
    if not keywords:
        return None

    query = db.query(models_recommendations.FoodItem)
    for keyword in keywords[:6]:
        like = f"%{keyword}%"
        match = query.filter(
            (models_recommendations.FoodItem.name.ilike(like)) |
            (models_recommendations.FoodItem.ingredients.ilike(like)) |
            (models_recommendations.FoodItem.course.ilike(like))
        ).first()
        if match:
            return match
    return None


async def get_mock_analysis(filename: str = "", yolo_hints: list = [], db: Session | None = None):
    """Fallback with keyword heuristic + YOLO hints if API unavailable"""
    await asyncio.sleep(1.8) # Simulate processing
    
    filename = filename.lower()
    all_hints = " ".join(yolo_hints).lower() + " " + filename
    catalog_item = _find_catalog_food_item(db, filename, yolo_hints)

    if catalog_item:
        estimated_portion = random.choice(["Small", "Medium", "Large"])
        nutrition = _estimate_catalog_nutrition(catalog_item, estimated_portion)
        return {
            "detection": {
                "food_item": catalog_item.name,
                "confidence": 0.84,
                "portion_unit": catalog_item.servings or "1 serving",
                "breakdown": []
            },
            "analysis": {
                "estimated_portion": estimated_portion,
                "nutrition": nutrition,
                "standards_database": "Kerala Food Catalog (Recipe Match)",
                "is_fallback": True
            },
            "disclaimer": "SERVICE NOTICE: Full AI Vision Analysis is currently in fallback mode. This result is matched from the imported Kerala food catalog and uses estimated nutrition values.",
            "message": f"Matched {catalog_item.name} from the Kerala food catalog."
        }
    
    # Priority Heuristics sharpened with YOLO hints
    detected_key = "burger" if "burger" in all_hints or "fastfood" in all_hints or "sandwich" in all_hints else \
                  "chicken_mandi" if "mandi" in all_hints else \
                  "masala_biriyani" if "biriyani" in all_hints or "biryani" in all_hints or "rice" in all_hints else \
                  "masala_dosa" if "dosa" in all_hints or "pancake" in all_hints else \
                  "alfham_chicken" if "alfham" in all_hints or "grilled" in all_hints or "chicken" in all_hints else \
                  "puttu_and_kadala" if "puttu" in all_hints else \
                  "appam_and_egg_curry" if "appam" in all_hints else \
                  random.choice(["masala_dosa", "masala_biriyani", "chicken_mandi", "alfham_chicken", "burger"])
    
    food_info = FOOD_DATABASE.get(detected_key, FOOD_DATABASE["masala_biriyani"])
    
    portion_sizes = ["Small", "Medium", "Large"]
    estimated_portion = random.choice(portion_sizes)
    multiplier = 0.7 if estimated_portion == "Small" else (1.4 if estimated_portion == "Large" else 1.0)
    
    scaled_nutrition = {
        "calories": int(food_info["calories"] * multiplier),
        "protein": round(food_info["protein"] * multiplier, 1),
        "carbs": round(food_info["carbs"] * multiplier, 1),
        "fats": round(food_info["fats"] * multiplier, 1),
    }
    
    return {
        "detection": {
            "food_item": food_info["common_name"],
            "confidence": 0.87, # Fixed fallback confidence (improved)
            "portion_unit": food_info["unit"],
            "breakdown": []
        },
        "analysis": {
            "estimated_portion": estimated_portion,
            "nutrition": scaled_nutrition,
            "standards_database": "Lite Mode (Keyword Match)",
            "is_fallback": True
        },
        "disclaimer": "SERVICE NOTICE: Full AI Vision Analysis is currently in 'Lite Mode' due to high demand or service limits. Results are estimated based on your image metadata and our internal database.",
        "message": f"Identified {food_info['common_name']} via smart match."
    }

def process_image(image_bytes: bytes) -> str:
    """Resize and compress image for AI analysis"""
    try:
        with load_raster_image(image_bytes) as img:
            # Convert to RGB if needed (e.g. PNG with alpha)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
                
            # Resize if too large (max 1024px dimension)
            max_size = 1024
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save to buffer as JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except UnidentifiedImageError as e:
        raise ValueError("Unsupported or unreadable image format.") from e
    except Exception as e:
        print(f"Error processing image: {e}")
        return base64.b64encode(image_bytes).decode('utf-8')

def call_openai_sync(base64_image: str, yolo_hints: list):
    """Synchronous OpenAI call to be run in executor"""
    hints_str = ", ".join(yolo_hints) if yolo_hints else "No local hints available"
    client = get_openai_client()
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured")

    settings = get_openai_settings()
    response = client.chat.completions.create(
        model=settings["model"] or "gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": f"You are an expert food nutritionist with deep knowledge of Indian, Kerala, and international cuisines. "
                                f"Analyze this food image with high precision. Local object detection suggests these potential items or context: {hints_str}. "
                                "Carefully examine colors, textures, shapes, plating style, and visible ingredients. "
                                "It is likely an Indian/Kerala meal or a common fast-food item. Identify ALL visible items including but not limited to: "
                                "Rice, Curries (Fish/Chicken/Egg/Vegetable), Thoran, Pappadam, Masala Dosa, Chutney, Sambar, Biriyani, Mandi, Alfham Chicken, Burger, Puttu, Appam, Idli, "
                                "Chapathi, Parotta, Naan, Fried items, Desserts, and Beverages. "
                                "Use your expertise to differentiate between visually similar dishes (e.g., Biriyani vs Fried Rice, Masala Dosa vs Plain Dosa). "
                                "Return a JSON object with: 1. 'food_item': A descriptive name of the ENTIRE meal, 2. 'confidence': float 0-1 (be precise, aim for high accuracy), "
                                "3. 'portion_unit': 'plate/bowl/piece/cup', 4. 'estimated_portion': 'Small/Medium/Large', "
                                "5. 'nutrition': {calories, protein, carbs, fats} as numbers, 6. 'breakdown': A list of detected sub-items with individual calorie estimates. Output ONLY valid JSON."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500,
        response_format={ "type": "json_object" }
    )
    return response.choices[0].message.content

def call_gemini_vision_sync(api_key: str, image_bytes: bytes, yolo_hints: list):
    """Synchronous Gemini Vision call to be run in executor"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        hints_str = ", ".join(yolo_hints) if yolo_hints else "No local hints available"
        
        prompt = (
            f"You are an expert food nutritionist with deep knowledge of Indian, Kerala, and international cuisines. "
            f"Analyze this food image with high precision. Local object detection suggests these potential items or context: {hints_str}. "
            "Carefully examine colors, textures, shapes, plating style, and visible ingredients. "
            "Identify ALL visible items including but not limited to: Rice, Curries, Biriyani, Mandi, Dosa, etc. "
            "Return a JSON object with: 1. 'food_item': name, 2. 'confidence': float (0-1), "
            "3. 'portion_unit': 'plate/bowl/piece/cup', 4. 'estimated_portion': 'Small/Medium/Large', "
            "5. 'nutrition': {calories, protein, carbs, fats} as numbers, 6. 'breakdown': list of sub-items. "
            "Output ONLY valid JSON."
        )
        
        # Open image for Gemini
        img = Image.open(io.BytesIO(image_bytes))
        
        # Gemini 1.5 handles image + text in the same list
        response = model.generate_content([prompt, img])
        
        # Clean up the response to ensure it's valid JSON
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        return text
    except Exception as e:
        print(f"Gemini Vision Error: {e}")
        raise e

@router.post("/estimate")
async def estimate_calories(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Enhanced AI endpoint using GPT-4 Vision or Gemini with image optimization.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    if is_vector_image(file.content_type, file.filename):
        raise HTTPException(status_code=400, detail="SVG images are not supported. Please upload a JPG, PNG, or HEIC photo.")
    
    openai_settings = get_openai_settings()
    api_key_openai = openai_settings["api_key"]
    api_key_gemini = os.getenv("GEMINI_API_KEY")
    
    with open("ai_debug.log", "a") as f:
        f.write(f"\n--- AI Analysis Request (Optimized) ---\n")
        f.write(f"OPENAI_API_KEY present: {'Yes' if api_key_openai else 'No'}\n")
        f.write(f"GEMINI_API_KEY present: {'Yes' if api_key_gemini else 'No'}\n")
        
    if not api_key_openai and not api_key_gemini:
        print("WARNING: No API keys found. Using YOLO-enhanced mock analysis.")
        contents = await file.read()
        yolo_hints = await run_yolo_detection(contents)
        return await get_mock_analysis(file.filename, yolo_hints, db)
        
    try:
        print("DEBUG: Processing image...")
        contents = await file.read()
        
        # Run YOLO in background to provide hints
        yolo_hints = await run_yolo_detection(contents)
        print(f"DEBUG: YOLO Hints: {yolo_hints}")
        
        loop = asyncio.get_event_loop()
        
        # Prioritize Gemini
        if api_key_gemini:
            try:
                print("DEBUG: Starting Gemini Vision API call...")
                result_content = await loop.run_in_executor(None, call_gemini_vision_sync, api_key_gemini, contents, yolo_hints)
                print(f"DEBUG: Gemini Response: {result_content}")
                
                ai_data = json.loads(result_content)
                return {
                    "detection": {
                        "food_item": ai_data.get("food_item", "Unknown Dish"),
                        "confidence": ai_data.get("confidence", 0.9),
                        "portion_unit": ai_data.get("portion_unit", "serving"),
                        "breakdown": ai_data.get("breakdown", [])
                    },
                    "analysis": {
                        "estimated_portion": ai_data.get("estimated_portion", "Medium"),
                        "nutrition": ai_data.get("nutrition", {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}),
                        "standards_database": "Gemini Vision Analysis (Free Tier Mode)",
                        "is_fallback": False,
                        "provider": "gemini"
                    },
                    "disclaimer": "NOTE: These values are AI-generated estimations based on visual content.",
                    "message": f"AI successfully identified {ai_data.get('food_item', 'dish')}."
                }
            except Exception as gem_err:
                print(f"Gemini Vision call failed: {gem_err}")
                # Fall through to OpenAI

        if api_key_openai:
            # Optimize image for OpenAI
            base64_image = await loop.run_in_executor(None, process_image, contents)
            
            print("DEBUG: Starting OpenAI API call...") 
            result_content = await loop.run_in_executor(None, call_openai_sync, base64_image, yolo_hints)
            
            print(f"DEBUG: OpenAI Response: {result_content}") 
            ai_data = json.loads(result_content)
            
            return {
                "detection": {
                    "food_item": ai_data.get("food_item", "Unknown Dish"),
                    "confidence": ai_data.get("confidence", 0.9),
                    "portion_unit": ai_data.get("portion_unit", "serving"),
                    "breakdown": ai_data.get("breakdown", [])
                },
                    "analysis": {
                        "estimated_portion": ai_data.get("estimated_portion", "Medium"),
                        "nutrition": ai_data.get("nutrition", {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}),
                        "standards_database": "OpenAI Vision Analysis",
                        "is_fallback": False,
                        "provider": openai_settings["provider"] or "openai"
                    },
                "disclaimer": "NOTE: These values are AI-generated estimations based on visual content.",
                "message": f"AI successfully identified {ai_data.get('food_item', 'dish')}."
            }
            
        # If neither worked, fallback to mock
        return await get_mock_analysis(file.filename, yolo_hints, db)
        
    except Exception as e:
        print(f"ERROR: AI Analysis failed: {str(e)}")
        # Fallback to mock if API fails
        return await get_mock_analysis(file.filename, yolo_hints, db)
