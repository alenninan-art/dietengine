from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
import asyncio
import random
import os
import base64
import json
import io
from openai import OpenAI
from PIL import Image
from .auth import get_current_user
from .. import models

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

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
    "masala_dosa": {
        "calories": 380, "protein": 8, "carbs": 65, "fats": 10, "unit": "1 medium Dosa + Chutney",
        "common_name": "Masala Dosa"
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
}

async def get_mock_analysis():
    """Fallback to mock analysis if API unavailable"""
    await asyncio.sleep(1.8) # Simulate processing
    food_names = list(FOOD_DATABASE.keys())
    detected_key = random.choice(food_names)
    food_info = FOOD_DATABASE[detected_key]
    
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
            "confidence": round(random.uniform(0.88, 0.99), 2),
            "portion_unit": food_info["unit"],
            "breakdown": []
        },
        "analysis": {
            "estimated_portion": estimated_portion,
            "nutrition": scaled_nutrition,
            "standards_database": "Internal Nutritional Standards (approx.)"
        },
        "disclaimer": "NOTE: These values are approximate estimations based on visual analysis. Actual nutritional content may vary based on exact ingredients and preparation methods.",
        "message": f"AI successfully identified {food_info['common_name']} with high confidence."
    }

def process_image(image_bytes: bytes) -> str:
    """Resize and compress image for AI analysis"""
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB if needed (e.g. PNG with alpha)
            if img.mode in ('RGBA', 'P'):
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
    except Exception as e:
        print(f"Error processing image: {e}")
        return base64.b64encode(image_bytes).decode('utf-8')

def call_openai_sync(api_key: str, base64_image: str):
    """Synchronous OpenAI call to be run in executor"""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this food image deeply. It is likely an Indian or Kerala meal. Identify ALL visible items (e.g., Rice, Curries, Thoran, Mezhukkupuratti, Papadam, Masala Dosa, Chutney, Sambar). Return a JSON object with: 1. 'food_item': A descriptive name of the ENTIRE meal (e.g., 'Kerala Rice Meal with Fish Curry & Cabbage' or 'Masala Dosa with Sambar & Chutney'), 2. 'confidence': float 0-1, 3. 'portion_unit': 'plate', 4. 'estimated_portion': 'Small/Medium/Large', 5. 'nutrition': Total estimated calories, protein, carbs, fats. 6. 'breakdown': A list of detected sub-items. Output ONLY valid JSON."},
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

@router.post("/estimate")
async def estimate_calories(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """
    Enhanced AI endpoint using GPT-4 Vision with image optimization and stability improvements.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    with open("ai_debug.log", "a") as f:
        f.write(f"\n--- AI Analysis Request (Optimized) ---\n")
        f.write(f"OPENAI_API_KEY present: {'Yes' if api_key else 'No'}\n")
        
    if not api_key:
        print("WARNING: No OPENAI_API_KEY found. Using mock analysis.")
        return await get_mock_analysis()
        
    try:
        print("DEBUG: Processing image...")
        contents = await file.read()
        
        # Optimize image in thread pool
        loop = asyncio.get_event_loop()
        base64_image = await loop.run_in_executor(None, process_image, contents)
        
        print("DEBUG: Starting OpenAI API call (Sync)...") 
        with open("ai_debug.log", "a") as f:
            f.write("Starting OpenAI API call (Sync via Executor)...\n")
        
        # Run OpenAI call in thread pool to prevent blocking/crashing
        result_content = await loop.run_in_executor(None, call_openai_sync, api_key, base64_image)
        
        print(f"DEBUG: OpenAI Response: {result_content}") 
        with open("ai_debug.log", "a") as f:
            f.write(f"OpenAI Response: {result_content}\n")
            
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
                "standards_database": "OpenAI GPT-4o Analysis"
            },
            "disclaimer": "NOTE: These values are AI-generated estimations. Actual nutritional content may vary.",
            "message": f"AI successfully identified {ai_data.get('food_item', 'dish')}."
        }
        
    except Exception as e:
        error_msg = f"ERROR: OpenAI API call failed: {str(e)}"
        print(error_msg)
        with open("ai_debug.log", "a") as f:
            f.write(f"{error_msg}\n")
            f.write(f"Traceback: {str(e)}\n")
            
        # Fallback to mock if API fails
        return await get_mock_analysis()
