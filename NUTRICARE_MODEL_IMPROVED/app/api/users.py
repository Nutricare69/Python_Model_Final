# ============================================================================
# FILE: app/api/users.py
# ROLE: USER HEALTH COMPUTE ENGINE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This Python service operates completely headless and stateless. 
# It DOES NOT connect to MongoDB. 
# Basic CRUD (Create, Read, Update, Delete) for users is now handled 
# entirely by the Node.js API Gateway.
#
# THE PIPELINE:
# 1. React asks Node.js for a user's health summary.
# 2. Node.js fetches the User Profile from MongoDB.
# 3. Node.js sends an internal HTTP POST to this Python router with the profile.
# 4. Python runs the BMI, Calorie, and Nutrition services.
# 5. Python returns the calculated metrics to Node.js.
# 6. Node.js returns the metrics to React (and optionally saves them).
# ============================================================================

from fastapi import APIRouter, HTTPException

# Import the Pydantic schema for validation
from app.schemas.user_schema import UserProfileSchema

# Import health calculation services
from app.services.bmi_service import BMIService
from app.services.calorie_service import CalorieService
from app.services.nutrition_service import NutritionService

# Initializes the FastAPI router
router = APIRouter()

# ==========================================
# COMPUTE USER HEALTH SUMMARY
# ==========================================

@router.post("/summary")
def compute_user_summary(user: UserProfileSchema):
    """
    PURPOSE: Compute a comprehensive health, fitness, and nutritional summary.
    EXPECTS POST BODY FROM NODE.JS: 
        The full UserProfile JSON object.
    RETURNS:
        Calculated targets for BMI, BMR, TDEE, Macros, and Micros.
    """
    try:
        # Convert Pydantic model to a standard dictionary
        user_data = user.model_dump()

        # ===== STEP 1: BMI Calculation =====
        bmi_result = BMIService.calculate_bmi(
            weight_kg=user_data["weight"],
            height_cm=user_data["height"]
        )

        # ===== STEP 2: Calorie Calculation =====
        calorie_result = CalorieService.generate_calorie_report(
            gender=user_data["gender"],
            weight_kg=user_data["weight"],
            height_cm=user_data["height"],
            age=user_data["age"],
            activity_level=user_data["activity_level"],
            goal=user_data["goal"],
            bmi_result=bmi_result
        )

        # ===== STEP 3: Nutrition Plan Generation =====
        nutrition_plan = NutritionService.generate_daily_nutrition_plan(
            calorie_result
        )

        # ===== FINAL RESPONSE =====
        # Indented exactly 8 spaces to remain perfectly inside the try block
        return {
            "success": True,
            "message": "Health summary computed successfully",
            "summary": {
                "bmi": bmi_result.bmi,
                "bmi_category": bmi_result.category,
                "health_risk": bmi_result.health_risk,
                "bmr": calorie_result.bmr,
                "tdee": calorie_result.tdee,
                "target_calories": calorie_result.target_calories,
                "protein_target": calorie_result.protein_target_g,
                "carb_target": calorie_result.carb_target_g,
                "fat_target": calorie_result.fat_target_g,
                "fiber_target": calorie_result.fiber_target_g,
                "water_target": calorie_result.water_target_liters
            }
        }

    except Exception as e:
        # Indented exactly 4 spaces to match the 'try:' block declaration line
        raise HTTPException(
            status_code=500,
            detail=f"Health Compute Engine Error: {str(e)}"
        )