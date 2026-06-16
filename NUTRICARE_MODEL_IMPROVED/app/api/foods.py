# # 🚀 Critical Integration Notes for the Backend Developer
# 1. MongoDB vs. Static CSV Data
# This file does not use MongoDB directly. It uses a CSV file defined by DATASET_PATH.

# If you want to keep it static: Ensure the CSV file is updated whenever the food database changes. You must restart the backend server to load changes.

# If you want to migrate to MongoDB: You will need to edit app/repositories/food_repository.py. The endpoints in this file will not require changes if the repository methods update their return type to a Pandas DataFrame or a list of dictionaries.

# 2. React Frontend Connection Example
# Here is how a React developer would call the search endpoint:

# javascript
# import axios from 'axios';

# const searchFoods = async (searchTerm) => {
#     try {
#         const response = await axios.get(`http://localhost:8000/foods/search/`, {
#             params: { query: searchTerm }
#         });
#         if (response.data.success) {
#             console.log(`Found ${response.data.count} foods:`, response.data.foods);
#         }
#     } catch (error) {
#         console.error("Error searching foods:", error);
#     }
# };
# 3. Error Handling
# This API uses HTTPException (404, 400). Always check if (!foods || foods.length === 0) in your frontend to display "No foods found" to the user gracefully rather than crashing the UI.

# 4. Absolute Paths
# In app/utils/constants.py, make sure DATASET_PATH points to the correct absolute path for your CSV file. Relative paths can break depending on the directory you run the uvicorn command from. A safe way to define it:

# python
# import os
# DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "Cleaned_Indian_Food_Dataset.csv")
# 5. Pagination (Future Improvement)
# Right now, get_all_foods returns the entire dataset at once. If you have 10,000+ foods, this will slow down your API and crash the frontend. In the future, consider adding skip and limit query parameters to all endpoints returning lists.
#
# 
# ============================================================================
# FILE: app/api/foods.py
# ROLE: This file is the FOOD DATA API ROUTER. 
#       It provides endpoints for the React Frontend to browse, search, and 
#       filter food items stored in the application.
# CRITICAL NOTE FOR BACKEND DEVELOPER:
#       This API currently serves STATIC data. The `FoodRepository` is initialized
#       with `DATASET_PATH` (a CSV file path), NOT a MongoDB connection.
#       If you want this data to come from MongoDB (e.g., to reflect user-added 
#       foods), you must update the `FoodRepository` in `app/repositories/food_repository.py`
#       to connect to MongoDB instead of loading the CSV file. All responses in 
#       this file are formatted as Pandas DataFrames converted to JSON.
# ============================================================================

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query

# Import the repository responsible for loading and querying the food dataset.
from app.repositories.food_repository import (
    FoodRepository
)

# Import the file path constant for the CSV dataset.
from app.utils.constants import (
    DATASET_PATH
)

# ============================================================================
# ROUTER SETUP
# ============================================================================

# Initializes the FastAPI router WITHOUT a prefix or tags.
# This means endpoints will be accessible directly at the router's mount point
# (e.g., if mounted at `/foods` in `main.py`, endpoints will be `/foods/`, `/foods/{food_id}`, etc.)
# TIP: Add `tags=["Foods"]` to the APIRouter() call to group this API properly in Swagger UI.
router = APIRouter()

# ============================================================================
# REPOSITORY INSTANCE
# ============================================================================

# Loads the food dataset into memory via the FoodRepository.
# Because DATASET_PATH is used, this repository is STATIC.
# If the CSV file changes, the backend must be RESTARTED to see the changes.
food_repository = (
    FoodRepository(
        DATASET_PATH
    )
)


# ==========================================
# GET ALL FOODS
# ==========================================

@router.get("/")
def get_all_foods():
    """
    PURPOSE: Retrieve every single food item from the static dataset.
    CONNECTS TO: Static CSV data loaded into a Pandas DataFrame via FoodRepository.
    REACT FRONTEND EXPECTATION (Request): GET /foods/
    RETURNS (JSON Response):
        {
            "success": True,
            "total_foods": 2500,
            "foods": [
                { "food_id": "1", "canonical_food_name": "Roti", ... },
                { "food_id": "2", "canonical_food_name": "Dal", ... }
            ]
        }
    NOTE: For very large datasets, this endpoint might be slow. Consider pagination for future updates.
    """
    
    # Fetch the full Pandas DataFrame from the repository.
    foods = (
        food_repository
        .get_all_foods()
    )

    return {
        "success": True,
        "total_foods": len(
            foods
        ),
        # `to_dict(orient="records")` converts the DataFrame into a list of dictionaries
        # where each dictionary is a row. This is the standard JSON format React expects.
        "foods": foods.to_dict(
            orient="records"
        )
    }


# ==========================================
# GET FOOD BY ID
# ==========================================

@router.get("/{food_id}")
def get_food_by_id(
    food_id: str
):
    """
    PURPOSE: Fetch a specific food item by its ID.
    CONNECTS TO: Static CSV data via FoodRepository.get_food_by_id().
    REACT FRONTEND EXPECTATION (Request): GET /foods/12345
    RETURNS (JSON Response):
        { 
            "success": True, 
            "food": { "food_id": "12345", "canonical_food_name": "Chicken Curry", ... }
        }
    ERROR HANDLING: Raises 404 error if the food ID is not found.
    """
    
    # Request the specific food item from the repository.
    food = (
        food_repository
        .get_food_by_id(
            food_id
        )
    )

    # If the repository returns None, it means the ID wasn't found in the CSV.
    if food is None:
        raise HTTPException(
            status_code=404,
            detail="Food not found"
        )

    return {
        "success": True,
        "food": food
    }


# ==========================================
# SEARCH FOODS
# ==========================================

@router.get("/search/")
def search_foods(
    query: str = Query(
        ...,
        min_length=1
    )
):
    """
    PURPOSE: Search for foods by name (or other text fields) based on a query string.
    CONNECTS TO: Static CSV data via FoodRepository.search_foods().
    REACT FRONTEND EXPECTATION (Request): GET /foods/search/?query=paneer
    REACT FRONTEND USAGE: 
        const response = await fetch('/foods/search/?query=' + encodeURIComponent(searchTerm));
    RETURNS (JSON Response):
        {
            "success": True,
            "query": "paneer",
            "count": 5,
            "foods": [ { "food_id": "201", "canonical_food_name": "Paneer Butter Masala", ... }, ... ]
        }
    """
    
    # Calls the repository to perform the text search. 
    # The repository is responsible for defining which columns to search against.
    foods = (
        food_repository
        .search_foods(
            query
        )
    )

    return {
        "success": True,
        "query": query,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# FILTER BY STATE
# ==========================================

@router.get("/state/{state}")
def get_foods_by_state(
    state: str
):
    """
    PURPOSE: Retrieve all food items belonging to a specific Indian state.
    CONNECTS TO: Static CSV data via FoodRepository.get_foods_by_state().
    REACT FRONTEND EXPECTATION (Request): GET /foods/state/Punjab
    RETURNS (JSON Response):
        {
            "success": True,
            "state": "Punjab",
            "count": 40,
            "foods": [ { "food_id": "1", "canonical_food_name": "Makki di Roti", ... }, ... ]
        }
    """
    
    # Filter the dataset by the 'state' column.
    foods = (
        food_repository
        .get_foods_by_state(
            state
        )
    )

    return {
        "success": True,
        "state": state,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# FILTER BY REGION
# ==========================================

@router.get("/region/{region}")
def get_foods_by_region(
    region: str
):
    """
    PURPOSE: Retrieve foods belonging to a geographic region (North, South, East, West, etc.).
    CONNECTS TO: Static CSV data via FoodRepository.get_foods_by_region().
    REACT FRONTEND EXPECTATION (Request): GET /foods/region/North
    RETURNS (JSON Response):
        {
            "success": True,
            "region": "North",
            "count": 120,
            "foods": [ ... ]
        }
    """
    
    # Filter the dataset by the 'region' column.
    foods = (
        food_repository
        .get_foods_by_region(
            region
        )
    )

    return {
        "success": True,
        "region": region,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# FILTER BY MEAL TYPE
# ==========================================

@router.get(
    "/meal-type/{meal_type}"
)
def get_foods_by_meal_type(
    meal_type: str
):
    """
    PURPOSE: Retrieve foods suitable for a specific meal type (Breakfast, Lunch, Dinner, Snacks).
    CONNECTS TO: Static CSV data via FoodRepository.get_foods_by_meal_type().
    REACT FRONTEND EXPECTATION (Request): GET /foods/meal-type/Breakfast
    RETURNS (JSON Response):
        {
            "success": True,
            "meal_type": "Breakfast",
            "count": 50,
            "foods": [ { "food_id": "3", "canonical_food_name": "Poha", ... }, ... ]
        }
    """
    
    # Filter the dataset by the 'meal_type' column.
    foods = (
        food_repository
        .get_foods_by_meal_type(
            meal_type
        )
    )

    return {
        "success": True,
        "meal_type": meal_type,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# FILTER BY DIET
# ==========================================

@router.get("/diet/{diet_type}")
def get_foods_by_diet(
    diet_type: str
):
    """
    PURPOSE: Retrieve foods suitable for a specific dietary preference (Veg, Non-Veg, Vegan).
    CONNECTS TO: Static CSV data via FoodRepository.get_foods_by_diet().
    REACT FRONTEND EXPECTATION (Request): GET /foods/diet/Veg
    RETURNS (JSON Response):
        {
            "success": True,
            "diet_type": "Veg",
            "count": 350,
            "foods": [ ... ]
        }
    """
    
    # Filter the dataset by the 'diet_type' column.
    foods = (
        food_repository
        .get_foods_by_diet(
            diet_type
        )
    )

    return {
        "success": True,
        "diet_type": diet_type,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# TOP FOODS
# ==========================================

@router.get("/top/{count}")
def get_top_foods(
    count: int = 20
):
    """
    PURPOSE: Retrieve the top 'count' foods (e.g., highest rated, most popular).
    CONNECTS TO: Static CSV data via FoodRepository.get_top_foods().
    REACT FRONTEND EXPECTATION (Request): GET /foods/top/10
    RETURNS (JSON Response):
        {
            "success": True,
            "count": 10,
            "foods": [ list_of_top_foods ]
        }
    NOTE: The definition of "top" depends entirely on how `get_top_foods` is implemented 
          in the repository (e.g., highest calories, highest protein, or most liked).
    """
    
    # Request the top 'count' foods from the repository.
    foods = (
        food_repository
        .get_top_foods(
            count
        )
    )

    return {
        "success": True,
        "count": count,
        "foods": foods
    }


# ==========================================
# BREAKFAST FOODS
# ==========================================

@router.get(
    "/category/breakfast"
)
def breakfast_foods():
    """
    PURPOSE: Shorthand endpoint for retrieving all foods marked as "Breakfast".
    CONNECTS TO: Reuses `get_foods_by_meal_type` internally.
    REACT FRONTEND EXPECTATION (Request): GET /foods/category/breakfast
    RETURNS (JSON Response): Same as `/foods/meal-type/Breakfast`.
    """
    
    # Directly call the function to get foods by meal type, hardcoded to 'Breakfast'.
    foods = (
        food_repository
        .get_foods_by_meal_type(
            "Breakfast"
        )
    )

    return {
        "success": True,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# LUNCH FOODS
# ==========================================

@router.get(
    "/category/lunch"
)
def lunch_foods():
    """
    PURPOSE: Shorthand endpoint for retrieving all foods marked as "Lunch".
    CONNECTS TO: Reuses `get_foods_by_meal_type` internally.
    REACT FRONTEND EXPECTATION (Request): GET /foods/category/lunch
    RETURNS (JSON Response): Same as `/foods/meal-type/Lunch`.
    """
    
    # Directly call the function to get foods by meal type, hardcoded to 'Lunch'.
    foods = (
        food_repository
        .get_foods_by_meal_type(
            "Lunch"
        )
    )

    return {
        "success": True,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# SNACKS FOODS
# ==========================================

@router.get(
    "/category/snacks"
)
def snacks_foods():
    """
    PURPOSE: Shorthand endpoint for retrieving all foods marked as "Snacks".
    CONNECTS TO: Reuses `get_foods_by_meal_type` internally.
    REACT FRONTEND EXPECTATION (Request): GET /foods/category/snacks
    RETURNS (JSON Response): Same as `/foods/meal-type/Snacks`.
    """
    
    # Directly call the function to get foods by meal type, hardcoded to 'Snacks'.
    foods = (
        food_repository
        .get_foods_by_meal_type(
            "Snacks"
        )
    )

    return {
        "success": True,
        "count": len(
            foods
        ),
        "foods": foods
    }


# ==========================================
# DINNER FOODS
# ==========================================

@router.get(
    "/category/dinner"
)
def dinner_foods():
    """
    PURPOSE: Shorthand endpoint for retrieving all foods marked as "Dinner".
    CONNECTS TO: Reuses `get_foods_by_meal_type` internally.
    REACT FRONTEND EXPECTATION (Request): GET /foods/category/dinner
    RETURNS (JSON Response): Same as `/foods/meal-type/Dinner`.
    """
    
    # Directly call the function to get foods by meal type, hardcoded to 'Dinner'.
    foods = (
        food_repository
        .get_foods_by_meal_type(
            "Dinner"
        )
    )

    return {
        "success": True,
        "count": len(
            foods
        ),
        "foods": foods
    }