# ============================================================================
# FILE: app/api/meal_plans.py
# ROLE: COMPUTE GATEWAY ROUTER LINK (With Unified Database Alignment Keys)
# ============================================================================

from fastapi import APIRouter, status, HTTPException
from app.schemas.user_schema import UserProfileSchema
from app.schemas.meal_plan_schema import PythonMLMealPlanResponseSchema
from app.services.meal_generator import MealGenerator

meal_generator = MealGenerator()
router = APIRouter()

@router.post("/generate", response_model=PythonMLMealPlanResponseSchema, status_code=status.HTTP_200_OK)
async def generate_meal_plan(payload: UserProfileSchema):
    try:
        # 1. INPUT DATA ADAPTER: Map strict incoming fields to core engine expectations
        user_data_dict = payload.model_dump()
        user_data_dict['weight'] = user_data_dict.get('weight_kg')
        user_data_dict['height'] = user_data_dict.get('height_cm')
        user_data_dict['days'] = user_data_dict.get('plan_duration_days')
        user_data_dict['food_preference'] = user_data_dict.get('diet_preference')
        user_data_dict['diet_type'] = user_data_dict.get('diet_preference')

        # Compute fallback cosmetic tokens for clean DB recording
        final_region = payload.region.strip() if payload.region and payload.region.strip() else "Global"
        final_state = payload.state.strip() if payload.state and payload.state.strip() else "All States"

        # 2. RUN MACHINE LEARNING COMPUTE LOOPS
        engine_output = meal_generator.generate_meal_plan(user_data_dict)

        metabolic = engine_output.get("metabolic_analysis", {})
        raw_meal_plan = engine_output.get("meal_plan", {})
        raw_days = engine_output.get("days", [])

        # Inline helper function to clean and map meal keys straight to your Mongoose fields
        def map_foods(food_list: list) -> list:
            if not food_list:
                return []
            return [
                {
                    "name": f.get("canonical_food_name") or f.get("name"),  # Handles alternative keys gracefully
                    "calories": round(f.get("calories", 0.0), 1),
                    "protein": round(f.get("protein", 0.0), 1),
                    "fat": round(f.get("fat", 0.0), 1),
                    "carbs": round(f.get("carbs", 0.0), 1)
                } for f in food_list if isinstance(f, dict)
            ]

        # 3. OUTPUT DATA ADAPTER: Universal parser built to prevent blank array allocations
        transformed_days_array = []

        # Track and convert structured string dictionary structures ("Day 1", "Day 2" labels)
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
                
        # Fallback tracking if the raw model core drops data arrays instead of keyed blocks
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

        # 4. CONSTRUCT SYNCHRONIZED PAYLOAD (Symmetrical properties mapping to Node.js / Mongoose properties)
        synchronized_payload = {
            "days": transformed_days_array,  # ➔ FIXED: Changed from "meal_plan" to match Node's destructured key
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
                "target_protein": metabolic.get("protein_target_g", 0.0),  # ➔ Mapped to target_protein
                "target_fat": metabolic.get("fat_target_g", 0.0),          # ➔ Mapped to target_fat
                "target_carbs": metabolic.get("carb_target_g", 0.0)        # ➔ Mapped to target_carbs
            }
        }

        return synchronized_payload

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Integration pipeline execution failed: {str(e)}"
        )