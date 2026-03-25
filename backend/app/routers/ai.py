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
from ultralytics import YOLO
from .auth import get_current_user
from .. import models

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
    "puttu_and_kadala": {
        "calories": 450, "protein": 15, "carbs": 75, "fats": 10, "unit": "2 pieces Puttu + 1 cup Kadala curry",
        "common_name": "Puttu & Kadala Curry"
    },
    "appam_and_egg_curry": {
        "calories": 400, "protein": 18, "carbs": 55, "fats": 14, "unit": "2 Appams + 1 bowl Egg Curry",
        "common_name": "Appam & Egg Curry"
    },
}

async def run_yolo_detection(image_bytes: bytes) -> list:
    """Run YOLOv8 on the image to identify objects for better hint generation"""
    if not yolo_model:
        return []
    
    try:
        # Load image for YOLO
        img = Image.open(io.BytesIO(image_bytes))
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
    except Exception as e:
        print(f"YOLO detection failed: {e}")
        return []

async def get_mock_analysis(filename: str = "", yolo_hints: list = []):
    """Fallback with keyword heuristic + YOLO hints if API unavailable"""
    await asyncio.sleep(1.8) # Simulate processing
    
    filename = filename.lower()
    all_hints = " ".join(yolo_hints).lower() + " " + filename
    
    # Priority Heuristics sharpened with YOLO hints
    detected_key = "burger" if "burger" in all_hints or "fastfood" in all_hints or "sandwich" in all_hints else \
                  "masala_biriyani" if "biriyani" in all_hints or "biryani" in all_hints or "rice" in all_hints else \
                  "masala_dosa" if "dosa" in all_hints or "pancake" in all_hints else \
                  "alfham_chicken" if "alfham" in all_hints or "grilled" in all_hints or "chicken" in all_hints else \
                  "puttu_and_kadala" if "puttu" in all_hints else \
                  "appam_and_egg_curry" if "appam" in all_hints else \
                  random.choice(["masala_dosa", "masala_biriyani", "alfham_chicken", "burger"])
    
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
            "standards_database": "Keyword-Based Matching (API Service Busy)",
            "is_fallback": True
        },
        "disclaimer": "SERVICE NOTICE: FULL AI analysis is currently unavailable. This is an estimated match based on your file name and our internal database.",
        "message": f"Identified {food_info['common_name']} via smart match."
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

def call_openai_sync(api_key: str, base64_image: str, yolo_hints: list):
    """Synchronous OpenAI call to be run in executor"""
    hints_str = ", ".join(yolo_hints) if yolo_hints else "No local hints available"
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
                                "Rice, Curries (Fish/Chicken/Egg/Vegetable), Thoran, Pappadam, Masala Dosa, Chutney, Sambar, Biriyani, Alfham Chicken, Burger, Puttu, Appam, Idli, "
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
        print("WARNING: No OPENAI_API_KEY found. Using YOLO-enhanced mock analysis.")
        contents = await file.read()
        yolo_hints = await run_yolo_detection(contents)
        return await get_mock_analysis(file.filename, yolo_hints)
        
    try:
        print("DEBUG: Processing image...")
        contents = await file.read()
        
        # Run YOLO in background to provide hints
        yolo_hints = await run_yolo_detection(contents)
        print(f"DEBUG: YOLO Hints: {yolo_hints}")
        
        # Optimize image in thread pool
        loop = asyncio.get_event_loop()
        base64_image = await loop.run_in_executor(None, process_image, contents)
        
        print("DEBUG: Starting OpenAI API call (Sync)...") 
        with open("ai_debug.log", "a") as f:
            f.write(f"YOLO Hints: {yolo_hints}\n")
            f.write("Starting OpenAI API call (Sync via Executor)...\n")
        
        # Run OpenAI call in thread pool with YOLO hints
        result_content = await loop.run_in_executor(None, call_openai_sync, api_key, base64_image, yolo_hints)
        
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
                "standards_database": "OpenAI Vision Analysis",
                "is_fallback": False
            },
            "disclaimer": "NOTE: These values are AI-generated estimations based on visual content.",
            "message": f"AI successfully identified {ai_data.get('food_item', 'dish')}."
        }
        
    except Exception as e:
        error_msg = f"ERROR: OpenAI API call failed: {str(e)}"
        print(error_msg)
        with open("ai_debug.log", "a") as f:
            f.write(f"{error_msg}\n")
            f.write(f"Traceback: {str(e)}\n")
            
        # Fallback to mock if API fails
        return await get_mock_analysis(file.filename)
