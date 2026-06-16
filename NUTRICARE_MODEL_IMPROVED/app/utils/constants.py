# # 🚀 Integration Guide for Backend Developer (MongoDB, React, API)
# 1. React Frontend Usage
# Dropdowns & Multi-selects: Use SUPPORTED_DIET_TYPES, SUPPORTED_GOALS, SUPPORTED_ALLERGIES, and SUPPORTED_MEDICAL_CONDITIONS to populate UI elements.

# Never hardcode strings: Always refer to these constants or their API equivalents to ensure frontend values match backend expectations.

# Example React code:

# javascript
# const DIET_TYPES = ['Veg', 'Eggitarian', 'Non-Veg'];
# // Use DIET_TYPES to render a dropdown.
# 2. MongoDB Storage
# When storing users in MongoDB, ensure the allergies and medical_conditions arrays contain only values from SUPPORTED_ALLERGIES and SUPPORTED_MEDICAL_CONDITIONS. This ensures compatibility with AllergyService and DiseaseService.

# The DATASET_PATH constant becomes optional when you fully migrate to MongoDB. The FoodRepository should query the foods collection directly, not load a CSV file.

# 3. API Validation
# Use SUPPORTED_DIET_TYPES and SUPPORTED_GOALS inside Pydantic validators in UserProfileSchema to reject invalid values immediately:

# python
# from pydantic import validator
# from app.utils.constants import SUPPORTED_DIET_TYPES

# class UserProfileSchema(BaseModel):
#     diet_type: str

#     @validator('diet_type')
#     def validate_diet_type(cls, v):
#         if v not in SUPPORTED_DIET_TYPES:
#             raise ValueError(f"diet_type must be one of {SUPPORTED_DIET_TYPES}")
#         return v
# 4. Modifying Global Settings
# To change the calorie split (e.g., give Dinner 30% and Lunch 30% instead of 25%/35%), update MEAL_DISTRIBUTION and the corresponding method in NutritionService.

# To make diversity stricter (e.g., 5 days gap instead of 3), update FOOD_REPEAT_GAP_DAYS.

# All changes take effect immediately because these constants are imported by the services at runtime.
# 
# 
# ============================================================================
# FILE: app/utils/constants.py
# ROLE: This file serves as the SINGLE SOURCE OF TRUTH for all static data
#       and configuration values used throughout the application. Every constant
#       defined here should be imported by services, schemas, repositories,
#       and API routes instead of using hardcoded strings or numbers.
# CONNECTIONS:
#   - MongoDB / React Frontend: The lists of supported values (e.g., diet types,
#     goals, allergies, medical conditions) define the ENUMERATION of valid
#     choices that React dropdowns/radio buttons should display. When moving to
#     MongoDB, these lists ensure that the data stored in the database is valid
#     and consistent.
#   - API / Services: These constants control the business logic (e.g., activity
#     multipliers for TDEE calculation, calorie distribution percentages for
#     meals, gap days for diversity rules).
#   - File Paths: Currently point to local JSON/CSV files. When migrating to
#     MongoDB, these file paths become less relevant, but they serve as a
#     fallback or indicate data source locations during development.
# ============================================================================

"""
Application Constants
"""


# ==========================================
# BMI CATEGORIES
# ==========================================
# These strings are used by the BMIService (app/services/bmi_service.py) to
# label the user's BMI status. They are returned to the React frontend as
# human-readable categories (e.g., "Normal Weight").

BMI_UNDERWEIGHT = "Underweight"
BMI_NORMAL = "Normal Weight"
BMI_OVERWEIGHT = "Overweight"
BMI_OBESE_CLASS_1 = "Obese Class I"
BMI_OBESE_CLASS_2 = "Obese Class II"
BMI_OBESE_CLASS_3 = "Obese Class III"


# ==========================================
# DIET TYPES
# ==========================================
# These constants define the supported dietary preferences in the system.
# - React frontend should show a dropdown limited to these values.
# - MongoDB user documents should store one of these strings.
# - FoodRepository (app/repositories/food_repository.py) uses `DIET_VEG` and
#   `DIET_EGGITARIAN` to filter foods via the `filter_by_diet()` method.
# - The `SUPPORTED_DIET_TYPES` list is ideal for Pydantic validation.

DIET_VEG = "Veg"
DIET_EGGITARIAN = "Eggitarian"
DIET_NON_VEG = "Non-Veg"

SUPPORTED_DIET_TYPES = [
    DIET_VEG,
    DIET_EGGITARIAN,
    DIET_NON_VEG
]


# ==========================================
# ACTIVITY LEVELS
# ==========================================
# These strings represent the user's self-reported physical activity level.
# - React frontend should map these to a dropdown/selector.
# - `ACTIVITY_MULTIPLIERS` is used by CalorieService (app/services/calorie_service.py)
#   to calculate Total Daily Energy Expenditure (TDEE) from BMR.
# - Example: If user selects "Moderate", TDEE = BMR * 1.55.
# - The backend developer should ensure these keys match exactly with what
#   is stored in the MongoDB user document and what the React UI sends.

ACTIVITY_SEDENTARY = "Sedentary"
ACTIVITY_LIGHT = "Light"
ACTIVITY_MODERATE = "Moderate"
ACTIVITY_ACTIVE = "Active"
ACTIVITY_VERY_ACTIVE = "Very Active"

ACTIVITY_MULTIPLIERS = {
    ACTIVITY_SEDENTARY: 1.20,
    ACTIVITY_LIGHT: 1.375,
    ACTIVITY_MODERATE: 1.55,
    ACTIVITY_ACTIVE: 1.725,
    ACTIVITY_VERY_ACTIVE: 1.90
}


# ==========================================
# USER GOALS
# ==========================================
# These constants define the fitness/health goals a user can select.
# - React frontend should display these as options.
# - MongoDB user documents store one of these values.
# - `GOAL_WEIGHT_LOSS` and `GOAL_MUSCLE_GAIN` are used by RankingService
#   (app/services/ranking_service.py) to apply different scoring weights
#   (e.g., `weight_loss_score` vs `muscle_gain_score`).
# - `SUPPORTED_GOALS` can be used for Pydantic validation.

GOAL_WEIGHT_LOSS = "Weight Loss"
GOAL_WEIGHT_GAIN = "Weight Gain"
GOAL_MAINTENANCE = "Maintenance"
GOAL_MUSCLE_GAIN = "Muscle Gain"

SUPPORTED_GOALS = [
    GOAL_WEIGHT_LOSS,
    GOAL_WEIGHT_GAIN,
    GOAL_MAINTENANCE,
    GOAL_MUSCLE_GAIN
]


# ==========================================
# MEAL TYPES
# ==========================================
# These constants correspond to the `meal_type` column in the food dataset.
# - Used by `FoodRepository.get_foods_by_meal_type()` and `MealGenerator`
#   to filter foods for specific meals.
# - `SUPPORTED_MEAL_TYPES` can be used to validate incoming requests.
# - React frontend can use these labels to render meal sections.

BREAKFAST = "Breakfast"
LUNCH = "Lunch"
SNACKS = "Snacks"
DINNER = "Dinner"

SUPPORTED_MEAL_TYPES = [
    BREAKFAST,
    LUNCH,
    SNACKS,
    DINNER
]


# ==========================================
# MEAL CALORIE DISTRIBUTION
# ==========================================
# These ratios define how daily calories and macros are split across meals.
# - Used by NutritionService (app/services/nutrition_service.py) to create
#   `MealNutritionTarget` objects for breakfast, lunch, snacks, and dinner.
# - The values sum to 1.0 (100%).
# - If you change these ratios, update the corresponding percentage strings
#   in `get_meal_distribution()` inside the NutritionService to keep the
#   frontend display consistent.

MEAL_DISTRIBUTION = {
    BREAKFAST: 0.25,
    LUNCH: 0.35,
    SNACKS: 0.15,
    DINNER: 0.25
}


# ==========================================
# PLAN DURATIONS
# ==========================================
# These constants define how many days a meal plan can be generated for.
# - `DEFAULT_PLAN_DAYS` is used by `MealGenerator.generate_meal_plan()`
#   if the `days` field is missing from the user profile.
# - `MIN_PLAN_DAYS` and `MAX_PLAN_DAYS` can be used for request validation.
# - `PREMIUM_PLAN_DAYS` is reserved for future subscription-based features.

DEFAULT_PLAN_DAYS = 7
PREMIUM_PLAN_DAYS = 14
MIN_PLAN_DAYS = 1
MAX_PLAN_DAYS = 14


# ==========================================
# ALLERGIES
# ==========================================
# These constants define the allergies recognized by the system.
# - The `ALLERGY_*` constants are the actual allergy names.
# - `SUPPORTED_ALLERGIES` should be used by the React frontend to populate
#   a list of checkboxes or multi-select.
# - `AllergyService` (app/services/allergy_service.py) maps these allergy names
#   to column names in the food dataset (e.g., "Gluten" -> "is_allergen_gluten").
# - When storing user data in MongoDB, the `allergies` array should only contain
#   values from this list (validated by Pydantic).

ALLERGY_GLUTEN = "Gluten"
ALLERGY_DAIRY = "Dairy"
ALLERGY_NUTS = "Nuts"
ALLERGY_SOY = "Soy"
ALLERGY_SHELLFISH = "Shellfish"
ALLERGY_EGGS = "Eggs"
ALLERGY_FISH = "Fish"

SUPPORTED_ALLERGIES = [
    ALLERGY_GLUTEN,
    ALLERGY_DAIRY,
    ALLERGY_NUTS,
    ALLERGY_SOY,
    ALLERGY_SHELLFISH,
    ALLERGY_EGGS,
    ALLERGY_FISH
]


# ==========================================
# MEDICAL CONDITIONS
# ==========================================
# These constants define the medical conditions recognized by the system.
# - `SUPPORTED_MEDICAL_CONDITIONS` is the master list for the React frontend.
# - `DiseaseService` (app/services/disease_service.py) maps these condition names
#   to column names in the food dataset (e.g., "Diabetes" -> "suitable_diabetes").
# - When storing user data in MongoDB, the `medical_conditions` array should
#   only contain values from this list.
# - `SUPPORTED_MEDICAL_CONDITIONS` should also be used to validate user input
#   in the `UserProfileSchema`.

CONDITION_DIABETES = "Diabetes"
CONDITION_HYPERTENSION = "Hypertension"
CONDITION_HEART_DISEASE = "Heart Disease"
CONDITION_THYROID = "Thyroid"
CONDITION_PCOS = "PCOS"
CONDITION_KIDNEY_DISEASE = "Kidney Disease"
CONDITION_GERD = "GERD"

SUPPORTED_MEDICAL_CONDITIONS = [
    CONDITION_DIABETES,
    CONDITION_HYPERTENSION,
    CONDITION_HEART_DISEASE,
    CONDITION_THYROID,
    CONDITION_PCOS,
    CONDITION_KIDNEY_DISEASE,
    CONDITION_GERD
]


# ==========================================
# SCORING CONSTANTS
# ==========================================
# These constants are used by the RankingService (app/services/ranking_service.py)
# to normalize and cap scoring values.
# - `MIN_FOOD_SCORE` and `MAX_FOOD_SCORE` define the allowable range for
#   `suitability_score` and `ml_score`.
# - `DEFAULT_MATCH_SCORE` is used as a neutral fallback when a score cannot
#   be calculated (e.g., no matching region).
# - `PERFECT_MATCH_SCORE` represents a perfect score (100).

MAX_FOOD_SCORE = 100
MIN_FOOD_SCORE = 0
DEFAULT_MATCH_SCORE = 50
PERFECT_MATCH_SCORE = 100


# ==========================================
# DIVERSITY RULES
# ==========================================
# These constants control the diversity enforcement in meal plans.
# - `FOOD_REPEAT_GAP_DAYS` defines how many days must pass before a food
#   can be repeated (default 3 days). Used by `DiversityService.get_recent_foods()`.
# - `MAX_SAME_CUISINE_STREAK` and `MAX_SAME_STATE_STREAK` are placeholders
#   for future advanced diversity rules (e.g., rotation of cuisines/states).
# - The backend developer can adjust these values to change the strictness
#   of diversity enforcement.

FOOD_REPEAT_GAP_DAYS = 3
MAX_SAME_CUISINE_STREAK = 2
MAX_SAME_STATE_STREAK = 2


# ==========================================
# WATER INTAKE
# ==========================================
# Used by CalorieService (app/services/calorie_service.py) to calculate daily
# water intake recommendations. The formula is `weight_kg * WATER_PER_KG_ML`,
# then converted to liters.
# This constant can be adjusted based on updated nutritional guidelines.

WATER_PER_KG_ML = 35


# ==========================================
# FIBER RULE
# ==========================================
# Used by CalorieService (app/services/calorie_service.py) to calculate daily
# fiber intake recommendations. The formula is `(target_calories / 1000) * FIBER_PER_1000_KCAL`.
# This is based on general dietary guidelines (e.g., 14g per 1000 calories).

FIBER_PER_1000_KCAL = 14


# ==========================================
# FILE PATHS
# ==========================================
# These constants define the paths for local JSON/CSV storage during development.
# - When migrating to MongoDB, these file paths become largely irrelevant,
#   but they are kept here for backward compatibility and debugging.
# - `DATASET_PATH`: Path to the Indian food dataset CSV. Used by FoodRepository.
#   If moving to MongoDB, the CSV is no longer needed; data lives in the
#   `foods` collection.
# - `USER_STORAGE_FILE`, `MEAL_PLAN_STORAGE_FILE`, `FEEDBACK_STORAGE_FILE`:
#   Paths for the JSON-based repositories (UserRepository, MealRepository,
#   FeedbackRepository). When moving to MongoDB, these can be removed or
#   kept as a fallback.

DATASET_PATH = (
    "datasets/"
    "Cleaned_Indian_Food_Dataset_Enriched_UTF8.csv"
)

USER_STORAGE_FILE = (
    "database/users.json"
)

MEAL_PLAN_STORAGE_FILE = (
    "database/meal_plans.json"
)

FEEDBACK_STORAGE_FILE = (
    "database/feedback.json"
)


# ==========================================
# APPLICATION INFO
# ==========================================
# These constants are used for API metadata and health checks.
# - `APP_NAME` and `APP_VERSION` are returned by the `/health` endpoint
#   (app/api/health.py) for monitoring and diagnostics.
# - `API_VERSION` is used to version the API routes (e.g., `/api/v1/...`).
# - The backend developer should update these values when deploying a new
#   version of the application to help debugging and version tracking.

APP_NAME = (
    "AI Meal Recommendation System"
)

APP_VERSION = "1.0.0"

API_VERSION = "v1"