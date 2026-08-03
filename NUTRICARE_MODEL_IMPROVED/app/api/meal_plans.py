# ============================================================================
# FILE: app/api/meal_plans.py
# ROLE: COMPUTE GATEWAY ROUTER LINK (With Unified Database Alignment Keys)
# ============================================================================

import time
from fastapi import APIRouter, status, HTTPException
from app.schemas.user_schema import UserProfileSchema
from app.schemas.meal_plan_schema import PythonMLMealPlanResponseSchema
from app.services.meal_generator import MealGenerator

# Instantiate singleton globally at module boot
meal_generator = MealGenerator()
router = APIRouter()

@router.post("/generate", response_model=PythonMLMealPlanResponseSchema, status_code=status.HTTP_200_OK)
def generate_meal_plan(payload: UserProfileSchema):
    """
    Synchronous 'def' endpoint. Offloads CPU-intensive matrix calculations to 
    FastAPI's background ThreadPoolExecutor to prevent blocking the async event loop.
    """
    t_start = time.perf_counter()
    print("\n==========================================")
    print("🚀 [PROFILE RUN STARTED] Processing Meal Plan Request...")
    print("==========================================")
    
    try:
        # 1. INPUT DATA ADAPTER
        t0 = time.perf_counter()
        user_data_dict = payload.model_dump()
        user_data_dict['weight'] = user_data_dict.get('weight_kg')
        user_data_dict['height'] = user_data_dict.get('height_cm')
        user_data_dict['days'] = user_data_dict.get('plan_duration_days')
        user_data_dict['food_preference'] = user_data_dict.get('diet_preference')
        user_data_dict['diet_type'] = user_data_dict.get('diet_preference')

        final_region = payload.region.strip() if payload.region and payload.region.strip() else "Global"
        final_state = payload.state.strip() if payload.state and payload.state.strip() else "All States"
        t1 = time.perf_counter()
        print(f"⏱️ [PROFILE] Step 1 - Payload Adapter: {t1 - t0:.4f}s")

        # 2. MACHINE LEARNING COMPUTE LOOPS
        engine_output = meal_generator.generate_meal_plan(user_data_dict)
        t2 = time.perf_counter()
        print(f"⏱️ [PROFILE] Step 2 - ML Core Execution: {t2 - t1:.4f}s")

        metabolic = engine_output.get("metabolic_analysis", {})
        raw_meal_plan = engine_output.get("meal_plan", {})
        raw_days = engine_output.get("days", [])

        def map_foods(food_list: list) -> list:
            if not food_list:
                return []
            return [
                {
                    "name": f.get("canonical_food_name") or f.get("name"),
                    "calories": round(f.get("calories", 0.0), 1),
                    "protein": round(f.get("protein", 0.0), 1),
                    "fat": round(f.get("fat", 0.0), 1),
                    "carbs": round(f.get("carbs", 0.0), 1)
                } for f in food_list if isinstance(f, dict)
            ]

        # 3. OUTPUT DATA ADAPTER
        transformed_days_array = []

        if isinstance(raw_meal_plan, dict) and raw_meal_plan:
            for index, (day_label, day_data) in enumerate(raw_meal_plan.items(), start=1):
                day_object = {
                    "dayNumber": index,
                    "meals": [
                        {"mealType": "Breakfast", "foods": map_foods(day_data.get("Breakfast", day_data.get("breakfast", [])))},
                        {"mealType": "Lunch", "foods": map_foods(day_data.get("Lunch", day_data.get("lunch", [])))},
                        {"mealType": "Dinner", "foods": map_foods(day_data.get("Dinner", day_data.get("dinner", [])))}
                    ]
                }
                transformed_days_array.append(day_object)
                
        elif isinstance(raw_days, list) and raw_days:
            for index, day_data in enumerate(raw_days, start=1):
                day_object = {
                    "dayNumber": day_data.get("day_number", index),
                    "meals": [
                        {"mealType": "Breakfast", "foods": map_foods(day_data.get("breakfast", {}).get("foods", []))},
                        {"mealType": "Lunch", "foods": map_foods(day_data.get("lunch", {}).get("foods", []))},
                        {"mealType": "Dinner", "foods": map_foods(day_data.get("dinner", {}).get("foods", []))}
                    ]
                }
                transformed_days_array.append(day_object)

        # 4. CONSTRUCT SYNCHRONIZED PAYLOAD
        synchronized_payload = {
            "days": transformed_days_array,
            "user_profile": {
                "bmi": metabolic.get("bmi", 0.0),
                "bmi_category": metabolic.get("bmi_category", "Normal Weight"),
                "bmr": metabolic.get("bmr", 0.0),
                "tdee": metabolic.get("tdee", 0.0),
                "region": final_region,
                "state": final_state
            },
            "daily_targets": {
                "target_calories": metabolic.get("target_calories", 0.0),
                "target_protein": metabolic.get("protein_target_g", 0.0),
                "target_fat": metabolic.get("fat_target_g", 0.0),
                "target_carbs": metabolic.get("carb_target_g", 0.0)
            }
        }

        t3 = time.perf_counter()
        print(f"⏱️ [PROFILE] Step 3 - Payload Assembly: {t3 - t2:.4f}s")
        print(f"⚡ [PROFILE] TOTAL EXECUTION TIME: {t3 - t_start:.4f}s")
        print("==========================================\n")

        return synchronized_payload

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Integration pipeline execution failed: {str(e)}"
        )