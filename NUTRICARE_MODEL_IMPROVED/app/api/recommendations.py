# ============================================================================
# FILE: app/api/recommendations.py
# ROLE: PERSONALIZED ML RECOMMENDATION API ROUTER (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This router functions as a pure algorithmic pipeline. It accepts a user profile 
# from the Node.js API Gateway, applies deep data filtering matrices, scores 
# candidates using the ML model, and returns ranked recommendations.
# ============================================================================

from fastapi import APIRouter, Query, HTTPException
from app.schemas.user_schema import UserProfileSchema
from app.services.meal_generator import MealGenerator
from app.repositories.food_repository import FoodRepository
from app.services.ranking_service import RankingService
from app.services.allergy_service import AllergyService
from app.services.disease_service import DiseaseService
from app.utils.constants import DATASET_PATH

# Initialize the Router
router = APIRouter()

# Instantiate Compute Services & Repositories
# NOTE: The food dataset remains localized to the Python environment for high-speed ML matrix lookups.
meal_generator = MealGenerator()
food_repository = FoodRepository(DATASET_PATH)
ranking_service = RankingService()


# ==========================================
# INTERNAL COMPUTATION ENGINE (CORE PIPELINE)
# ==========================================
def _compute_ranked_recommendations(profile_dict: dict) -> list:
    """
    Executes the multi-stage machine learning and constraint-filtering pipeline.
    """
    # 1. Fetch baseline food matrix into a Pandas DataFrame
    foods_df = food_repository.get_all_foods()

    # 2. Constraint Filter Stage I: Allergy Elimination
    foods_df = AllergyService.filter_foods(
        foods_df, 
        profile_dict.get("allergies", [])
    )

    # 3. Constraint Filter Stage II: Medical Condition Elimination
    foods_df = DiseaseService.filter_foods(
        foods_df, 
        profile_dict.get("medical_conditions", [])
    )

    # 4. Constraint Filter Stage III: Core Diet Type Alignment
    foods_df = food_repository.filter_by_diet(
        foods_df, 
        profile_dict["diet_type"]
    )

    # 5. Machine Learning Inference Stage: Run Scoring Model (food_ranker.pkl)
    ranked_df = ranking_service.rank_foods(foods_df, profile_dict)
    
    return ranked_df


# ==========================================
# GLOBAL TOP RECOMMENDATIONS
# ==========================================
@router.post("/")
def get_recommendations(
    user_profile: UserProfileSchema,
    top_n: int = Query(default=20, ge=1, le=100)
):
    """
    PURPOSE: Generate globally optimized personalized recommendations.
    PERFORMANCE UPGRADE: Swapped out .iterrows() loop for high-speed vector serialization.
    """
    try:
        profile = user_profile.model_dump()
        ranked_df = _compute_ranked_recommendations(profile)
        
        # Slice top N rows and extract records directly via vectorized conversion
        top_foods = ranked_df.head(top_n)
        recommendations_list = top_foods.to_dict(orient="records")

        return {
            "success": True,
            "message": "Global ML recommendations generated successfully",
            "total_recommendations": len(recommendations_list),
            "recommendations": recommendations_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation Matrix Error: {str(e)}")


# ==========================================
# MEAL-SPECIFIC RECOMMENDATION ENDPOINTS
# ==========================================

@router.post("/breakfast")
def breakfast_recommendations(user_profile: UserProfileSchema, top_n: int = 10):
    """
    Returns foods matching the user profile specifically categorized for breakfast.
    """
    try:
        profile = user_profile.model_dump()
        candidates = meal_generator.prepare_food_candidates(profile)
        top_foods = candidates["breakfast"].head(top_n)

        return {
            "success": True,
            "meal_type": "Breakfast",
            "recommendations": top_foods.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Breakfast Pipeline Error: {str(e)}")


@router.post("/lunch")
def lunch_recommendations(user_profile: UserProfileSchema, top_n: int = 10):
    """
    Returns foods matching the user profile specifically categorized for lunch.
    """
    try:
        profile = user_profile.model_dump()
        candidates = meal_generator.prepare_food_candidates(profile)
        top_foods = candidates["lunch"].head(top_n)

        return {
            "success": True,
            "meal_type": "Lunch",
            "recommendations": top_foods.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lunch Pipeline Error: {str(e)}")


@router.post("/snacks")
def snacks_recommendations(user_profile: UserProfileSchema, top_n: int = 10):
    """
    Returns foods matching the user profile specifically categorized for snacks.
    """
    try:
        profile = user_profile.model_dump()
        candidates = meal_generator.prepare_food_candidates(profile)
        top_foods = candidates["snacks"].head(top_n)

        return {
            "success": True,
            "meal_type": "Snacks",
            "recommendations": top_foods.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snacks Pipeline Error: {str(e)}")


@router.post("/dinner")
def dinner_recommendations(user_profile: UserProfileSchema, top_n: int = 10):
    """
    Returns foods matching the user profile specifically categorized for dinner.
    """
    try:
        profile = user_profile.model_dump()
        candidates = meal_generator.prepare_food_candidates(profile)
        top_foods = candidates["dinner"].head(top_n)

        return {
            "success": True,
            "meal_type": "Dinner",
            "recommendations": top_foods.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dinner Pipeline Error: {str(e)}")