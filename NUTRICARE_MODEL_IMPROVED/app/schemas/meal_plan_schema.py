# ============================================================================
# FILE: app/schemas/meal_plan_schema.py
# ROLE: OUTGOING RESPONSE VALIDATION GATEKEEPER
# ============================================================================

from pydantic import BaseModel
from typing import List

class FoodItemResponse(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float

class MealBlockResponse(BaseModel):
    mealType: str
    foods: List[FoodItemResponse]

class DayPlanResponse(BaseModel):
    dayNumber: int
    meals: List[MealBlockResponse]

class UserProfileResponse(BaseModel):
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    region: str
    state: str

class DailyTargetsResponse(BaseModel):
    target_calories: float
    target_protein: float
    target_fat: float
    target_carbs: float

class PythonMLMealPlanResponseSchema(BaseModel):
    days: List[DayPlanResponse]
    user_profile: UserProfileResponse
    daily_targets: DailyTargetsResponse