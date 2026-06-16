# Endpoint Paths:
# React will call the following endpoints:
# GET /analytics/overview
# GET /analytics/states
# GET /analytics/regions
# GET /analytics/meal-types
# GET /analytics/food-groups
# GET /analytics/top-protein
# GET /analytics/top-fiber
# GET /analytics/goals
# GET /analytics/medical-conditions
# GET /analytics/diet-types
# GET /analytics/favorites
# GET /analytics/feedback
# GET /analytics/dataset-health
# GET /analytics/calories
# GET /analytics/health
# ============================================================================
# FILE: app/api/analytics.py
# ROLE: This file is the AGGREGATION AND ANALYTICS ROUTER.
#       It provides endpoints for the React Frontend to display dashboards 
#       and statistics about the app's data (food, users, meals, feedback).
# CONNECTIONS:
#   - React Frontend calls these endpoints (e.g., /analytics/overview).
#   - MongoDB Connection is handled implicitly via the *Repository files.
#   - Food data is loaded statically from DATASET_PATH (CSV/Excel) into a 
#     Pandas DataFrame via FoodRepository.
# ============================================================================

from collections import Counter

from fastapi import APIRouter

# ===== REPOSITORY IMPORTS =====
# ROLE: These are the DATA ACCESS LAYER. They abstract away MongoDB/CSV complexity.
#       The Backend Developer must ensure these repositories connect to the
#       correct data sources (MongoDB for users/meals/feedback, File for foods).
from app.repositories.feedback_repository import (
    FeedbackRepository
)
from app.repositories.food_repository import (
    FoodRepository
)
from app.repositories.meal_repository import (
    MealRepository
)
from app.repositories.user_repository import (
    UserRepository
)

# ===== UTILITY IMPORTS =====
from app.utils.constants import (
    DATASET_PATH  # This string contains the file path to the Indian Food Dataset CSV.
)


# ==========================================
# ROUTER SETUP
# ==========================================

# Initializes the FastAPI router for this specific file.
# PREFIX: All endpoints in this file will start with /analytics.
# TAGS: Groups these endpoints under "Analytics" in the Swagger UI docs.
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# ==========================================
# REPOSITORY INITIALIZATION
# ==========================================
# IMPORTANT: These repositories are instantiated here so they can be shared
# across all endpoints in this file.

# FoodRepository is initialized with DATASET_PATH.
# It loads the dataset (CSV) into a Pandas DataFrame (self.foods_df).
# WARNING FOR BACKEND DEV: If you add new food items to MongoDB, this will
# NOT pick them up unless you reload the file or update FoodRepository to 
# query MongoDB instead.
food_repository = FoodRepository(
    DATASET_PATH
)

# These repositories likely wrap MongoDB collections.
# They should be fully functional (CRUD operations) for their respective data.
user_repository = UserRepository()
meal_repository = MealRepository()
feedback_repository = (
    FeedbackRepository()
)


# ==========================================
# SYSTEM OVERVIEW
# ==========================================

@router.get("/overview")
def system_overview():
    """
    PURPOSE: Returns key counts for the admin dashboard in React.
    FRONTEND EXPECTATION: { success: True, total_foods: 100, total_users: 50, ... }
    MONGODB CONNECTION: Gets users, meals, and feedback from MongoDB. 
    FOOD DATA: Gets food count from the static Dataframe.
    """
    
    # Fetch all food items as a Pandas DataFrame.
    foods_df = (
        food_repository
        .get_all_foods()
    )

    # Fetch all users as a list of dictionaries from MongoDB.
    users = (
        user_repository
        .get_all_users()
    )

    # Fetch all meal plans as a list of dictionaries from MongoDB.
    meal_plans = (
        meal_repository
        .get_all_meal_plans()
    )

    # Fetch all feedback as a list of dictionaries from MongoDB.
    feedback = (
        feedback_repository
        .get_all_feedback()
    )

    return {
        "success": True,
        # len(foods_df) returns the number of rows in the CSV/Dataframe.
        "total_foods":
            len(foods_df),
        "total_users":
            len(users),
        "total_meal_plans":
            len(meal_plans),
        "total_feedback":
            len(feedback)
    }


# ==========================================
# STATE ANALYTICS
# ==========================================

@router.get("/states")
def state_analytics():
    """
    PURPOSE: Returns a count of foods grouped by Indian state.
    DATA SOURCE: Only FoodRepository (Static CSV data).
    ERROR HANDLING: Checks if 'state' column exists in the dataframe first.
    FRONTEND EXPECTATION: { success: True, states: { "Punjab": 15, "Gujarat": 10 } }
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    # Validate if the column exists to avoid a KeyError crash.
    if "state" not in foods_df.columns:
        return {
            "success": True,
            "states": {}
        }

    return {
        "success": True,
        # .value_counts() counts unique values.
        # .to_dict() converts the Pandas Series to a Python dict for JSON serialization.
        "states":
            foods_df[
                "state"
            ]
            .value_counts()
            .to_dict()
    }


# ==========================================
# REGION ANALYTICS
# ==========================================

@router.get("/regions")
def region_analytics():
    """
    PURPOSE: Returns a count of foods grouped by region (North, South, etc).
    FRONTEND EXPECTATION: { success: True, regions: { "North": 5, "South": 8 } }
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    if "region" not in foods_df.columns:
        return {
            "success": True,
            "regions": {}
        }

    return {
        "success": True,
        "regions":
            foods_df[
                "region"
            ]
            .value_counts()
            .to_dict()
    }


# ==========================================
# MEAL TYPE ANALYTICS
# ==========================================

@router.get("/meal-types")
def meal_type_analytics():
    """
    PURPOSE: Returns the number of foods suitable for Breakfast, Lunch, Dinner.
    FRONTEND EXPECTATION: { success: True, meal_types: { "Breakfast": 40, "Dinner": 30 } }
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    if "meal_type" not in foods_df.columns:
        return {
            "success": True,
            "meal_types": {}
        }

    return {
        "success": True,
        "meal_types":
            foods_df[
                "meal_type"
            ]
            .value_counts()
            .to_dict()
    }


# ==========================================
# FOOD GROUP ANALYTICS
# ==========================================

@router.get("/food-groups")
def food_group_analytics():
    """
    PURPOSE: Returns the count of foods grouped by categories (Grains, Fruits, etc).
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    if "food_group" not in foods_df.columns:
        return {
            "success": True,
            "food_groups": {}
        }

    return {
        "success": True,
        "food_groups":
            foods_df[
                "food_group"
            ]
            .value_counts()
            .to_dict()
    }


# ==========================================
# TOP PROTEIN FOODS
# ==========================================

@router.get("/top-protein")
def top_protein_foods():
    """
    PURPOSE: Returns the top 20 foods with the highest protein content.
    FRONTEND EXPECTATION: [ { food_id: 1, canonical_food_name: "Chicken", protein: 40 }, ... ]
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    # Validate column existence to avoid errors.
    if (
        "protein"
        not in foods_df.columns
    ):
        return {
            "success": True,
            "foods": []
        }

    # Sort by protein in descending order (largest first).
    # .head(20) takes only the top 20 entries.
    top_foods = (
        foods_df
        .sort_values(
            by="protein",
            ascending=False
        )
        .head(20)
    )

    return {
        "success": True,
        # orient="records" returns a list of dictionaries [{col1: val1}, {col2: val2}]
        # This is the easiest format for React frontends to iterate over.
        "foods":
            top_foods[
                [
                    "food_id",
                    "canonical_food_name",
                    "protein"
                ]
            ]
            .to_dict(
                orient="records"
            )
    }


# ==========================================
# TOP FIBER FOODS
# ==========================================

@router.get("/top-fiber")
def top_fiber_foods():
    """
    PURPOSE: Returns the top 20 foods with the highest fiber content.
    FRONTEND EXPECTATION: Same format as top-protein.
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    if (
        "fiber_g"
        not in foods_df.columns
    ):
        return {
            "success": True,
            "foods": []
        }

    top_foods = (
        foods_df
        .sort_values(
            by="fiber_g",
            ascending=False
        )
        .head(20)
    )

    return {
        "success": True,
        "foods":
            top_foods[
                [
                    "food_id",
                    "canonical_food_name",
                    "fiber_g"
                ]
            ]
            .to_dict(
                orient="records"
            )
    }


# ==========================================
# USER GOALS
# ==========================================

@router.get("/goals")
def goal_analytics():
    """
    PURPOSE: Counts users grouped by their fitness goal (e.g., Weight Loss, Muscle Gain).
    DATA SOURCE: Live MongoDB data (UserRepository).
    """
    
    # Fetch all users from MongoDB.
    users = (
        user_repository
        .get_all_users()
    )

    # Safely extract the 'goal' field. If missing, default to 'Unknown'.
    goals = [
        user.get(
            "goal",
            "Unknown"
        )
        for user in users
    ]

    return {
        "success": True,
        # Counter is a Python built-in that counts occurrences.
        "goals":
            dict(
                Counter(goals)
            )
    }


# ==========================================
# MEDICAL CONDITIONS
# ==========================================

@router.get("/medical-conditions")
def medical_condition_analytics():
    """
    PURPOSE: Counts how many users have specific medical conditions (e.g., Diabetes, High BP).
    DATA SOURCE: Live MongoDB data (UserRepository).
    DATA STRUCTURE: medical_conditions in MongoDB is likely an array/list.
    """
    
    users = (
        user_repository
        .get_all_users()
    )

    # Initialize an empty list to collect all conditions from all users.
    conditions = []

    for user in users:
        # .extend() flattens the list of lists.
        # e.g., [["Diabetes"]] becomes ["Diabetes"]
        conditions.extend(
            user.get(
                "medical_conditions",
                []
            )
        )

    return {
        "success": True,
        "conditions":
            dict(
                Counter(
                    conditions
                )
            )
    }


# ==========================================
# DIET TYPES
# ==========================================

@router.get("/diet-types")
def diet_type_analytics():
    """
    PURPOSE: Counts users grouped by dietary preferences (Veg, Non-Veg, Vegan, etc.).
    """
    
    users = (
        user_repository
        .get_all_users()
    )

    diet_types = [
        user.get(
            "diet_type",
            "Unknown"
        )
        for user in users
    ]

    return {
        "success": True,
        "diet_types":
            dict(
                Counter(
                    diet_types
                )
            )
    }


# ==========================================
# FAVORITE MEAL PLANS
# ==========================================

@router.get("/favorites")
def favorite_meals():
    """
    PURPOSE: Returns the number of meal plans marked as 'favorite'.
    DATA SOURCE: Live MongoDB data (MealRepository).
    FRONTEND EXPECTATION: { success: True, favorite_meal_plans: 5 }
    """
    
    meal_plans = (
        meal_repository
        .get_all_meal_plans()
    )

    # Filter the list of meal plans, keeping only those with 'favorite: True'.
    favorites = [
        plan
        for plan in meal_plans
        if plan.get(
            "favorite",
            False
        )
    ]

    return {
        "success": True,
        "favorite_meal_plans":
            len(favorites)
    }


# ==========================================
# FEEDBACK ANALYTICS
# ==========================================

@router.get("/feedback")
def feedback_analytics():
    """
    PURPOSE: Returns the total feedback count and a breakdown by feedback type (Positive, Negative).
    DATA SOURCE: Live MongoDB data (FeedbackRepository).
    """
    
    feedback = (
        feedback_repository
        .get_all_feedback()
    )

    # Extract feedback_type from each entry.
    feedback_types = []

    for item in feedback:
        feedback_types.append(
            item.get(
                "feedback_type",
                "unknown"
            )
        )

    return {
        "success": True,
        "total_feedback":
            len(feedback),
        "feedback_breakdown":
            dict(
                Counter(
                    feedback_types
                )
            )
    }


# ==========================================
# DATASET HEALTH
# ==========================================

@router.get("/dataset-health")
def dataset_health():
    """
    PURPOSE: Returns metadata about the health of the Food Dataset (Static CSV).
    USAGE: Allows the admin dashboard to check if the dataset loaded correctly.
    RETURNS: Total rows, total columns, and a dictionary of missing values per column.
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    return {
        "success": True,
        "total_rows":
            len(foods_df),
        "total_columns":
            len(
                foods_df.columns
            ),
        # .isnull().sum() returns a Pandas Series of counts of NaN values.
        # .to_dict() converts it for JSON.
        "missing_values":
            foods_df
            .isnull()
            .sum()
            .to_dict()
    }


# ==========================================
# CALORIE STATISTICS
# ==========================================

@router.get("/calories")
def calorie_analytics():
    """
    PURPOSE: Returns aggregate statistics on food calories (Average, Min, Max).
    FRONTEND EXPECTATION: { success: True, average_calories: 250.5, ... }
    """
    
    foods_df = (
        food_repository
        .get_all_foods()
    )

    if (
        "calories"
        not in foods_df.columns
    ):
        return {
            "success": True
        }

    return {
        "success": True,
        # .mean(), .min(), .max() work on Pandas Series. .round(2) keeps it clean.
        "average_calories":
            round(
                foods_df[
                    "calories"
                ].mean(),
                2
            ),
        "minimum_calories":
            round(
                foods_df[
                    "calories"
                ].min(),
                2
            ),
        "maximum_calories":
            round(
                foods_df[
                    "calories"
                ].max(),
                2
            )
    }


# ==========================================
# HEALTH
# ==========================================

@router.get("/health")
def analytics_health():
    """
    PURPOSE: A lightweight heartbeat endpoint to ensure the Analytics router is alive.
    USE CASE: Monitoring systems (Kubernetes/Cloud) use this to check uptime.
    """
    
    return {
        "success": True,
        "service": "analytics",
        "status": "healthy"
    }