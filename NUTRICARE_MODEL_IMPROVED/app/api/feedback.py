# 🚀 Additional Notes for the Backend Developer (React ↔ MongoDB Integration)
# MongoDB Collection Structure (feedback collection):
# This API expects that feedback_repository.py handles documents with fields like:

# json
# {
#     "_id": ObjectId("..."),
#     "user_id": "user123",
#     "food_id": "food456",
#     "feedback_text": "Really tasty!",
#     "feedback_type": "positive",
#     "liked": true,
#     "rating": 5,
#     "created_at": "2024-01-01T12:00:00Z"
# }
# React Frontend Calls (Example):

# javascript
# Like a food
# const response = await axios.post(
#     'http://localhost:8000/feedback/like',
#     { user_id: '123', food_id: '456' }
# );

#  Get liked foods
# const likedFoods = await axios.get(
#     'http://localhost:8000/feedback/user/123/liked-foods'
# );
# Error Handling: This API uses HTTPException for errors (e.g., 404 for missing feedback, 400 for invalid ratings). Your React frontend should handle these errors gracefully (e.g., show a toast notification).


# ============================================================================
# FILE: app/api/feedback.py
# ROLE: This file is the FEEDBACK MANAGEMENT API ROUTER.
#       It handles all operations related to user feedback, likes, dislikes, 
#       ratings, and food-specific feedback from the React frontend.
# CONNECTIONS:
#   - MongoDB: All data is handled by FeedbackRepository (which performs 
#     CRUD operations on a MongoDB collection named 'feedback').
#   - React: React calls these endpoints to submit feedback, retrieve user 
#     preferences, and calculate average ratings.
#   - Other Backend Files: This file interacts with `app/repositories/feedback_repository.py`.
# ============================================================================

from fastapi import APIRouter
from fastapi import HTTPException

# Import the repository responsible for database operations on feedback data.
from app.repositories.feedback_repository import (
    FeedbackRepository
)

# ============================================================================
# ROUTER SETUP
# ============================================================================

# Initializes the FastAPI router with a prefix '/feedback'.
# All endpoints in this file will be accessed like:
#   POST /feedback/
#   GET /feedback/{feedback_id}
#   GET /feedback/user/{user_id}
#   etc.
# TAG: Groups these endpoints under "Feedback" in the Swagger UI documentation.
router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)

# ============================================================================
# REPOSITORY INSTANCE
# ============================================================================

# Instantiate the FeedbackRepository object. 
# This repository handles MongoDB connection and operations.
feedback_repository = (
    FeedbackRepository()
)


# ==========================================
# SUBMIT FEEDBACK
# ==========================================

@router.post("/")
def submit_feedback(
    payload: dict
):
    """
    PURPOSE: Endpoint to save generic feedback from a user.
    CONNECTS TO: MongoDB via feedback_repository.save_feedback().
    REACT EXPECTATION (Request Body - JSON):
        {
            "user_id": "user123",          # (string) MongoDB ObjectId or user ID
            "food_id": "food456",          # (string) Food ID or Name
            "feedback_text": "Great food!",# (string) User's text feedback
            "feedback_type": "positive"    # (string) "positive", "negative", "neutral"
        }
    RETURNS (JSON Response):
        {
            "success": True,
            "feedback_id": "Feedback entry's ObjectId",
            "message": "Feedback submitted successfully"
        }
    """
    
    # Delegates the storage of feedback to the repository.
    # The repository handles the database insertion and returns the newly 
    # created feedback record's ID (likely the MongoDB ObjectId string).
    feedback_id = (
        feedback_repository
        .save_feedback(
            payload
        )
    )

    return {
        "success": True,
        "feedback_id": feedback_id,
        "message":
            "Feedback submitted successfully"
    }


# ==========================================
# GET FEEDBACK
# ==========================================

@router.get("/{feedback_id}")
def get_feedback(
    feedback_id: str
):
    """
    PURPOSE: Retrieve a single feedback record by its unique ID.
    CONNECTS TO: MongoDB via feedback_repository.get_feedback().
    REACT EXPECTATION: Pass feedback_id in the URL, e.g., GET /feedback/67890
    RETURNS (JSON Response):
        If found: { "success": True, "feedback": { ...feedback document... } }
        If not found: Raises HTTP 404 error with detail "Feedback not found"
    """
    
    # Try to fetch the feedback document from MongoDB using the provided ID.
    feedback = (
        feedback_repository
        .get_feedback(
            feedback_id
        )
    )

    # If the repository returns None or an empty result, raise a 404 HTTP error.
    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

    return {
        "success": True,
        "feedback": feedback
    }


# ==========================================
# DELETE FEEDBACK
# ==========================================

@router.delete("/{feedback_id}")
def delete_feedback(
    feedback_id: str
):
    """
    PURPOSE: Delete a specific feedback record by its ID.
    CONNECTS TO: MongoDB via feedback_repository.delete_feedback().
    REACT EXPECTATION: DELETE /feedback/{feedback_id} (no request body).
    RETURNS (JSON Response):
        If successful: { "success": True, "message": "Feedback deleted successfully" }
        If not found: Raises HTTP 404 error with detail "Feedback not found"
    """
    
    # Attempts to delete the feedback document. Returns True if successful, False if not found.
    deleted = (
        feedback_repository
        .delete_feedback(
            feedback_id
        )
    )

    # If deletion fails (probably because the record doesn't exist), raise an error.
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

    return {
        "success": True,
        "message":
            "Feedback deleted successfully"
    }


# ==========================================
# ALL FEEDBACK
# ==========================================

@router.get("/")
def get_all_feedback():
    """
    PURPOSE: Retrieve all feedback entries from the database.
    CONNECTS TO: MongoDB via feedback_repository.get_all_feedback().
    REACT EXPECTATION: GET /feedback/
    RETURNS (JSON Response):
        { 
            "success": True, 
            "count": 120, 
            "feedback": [ {feedback1}, {feedback2}, ... ] 
        }
    """
    
    # Fetch all feedback documents from MongoDB as a list of dictionaries.
    feedback = (
        feedback_repository
        .get_all_feedback()
    )

    return {
        "success": True,
        "count": len(feedback),
        "feedback": feedback
    }


# ==========================================
# USER FEEDBACK
# ==========================================

@router.get("/user/{user_id}")
def get_user_feedback(
    user_id: str
):
    """
    PURPOSE: Retrieve all feedback left by a specific user.
    CONNECTS TO: MongoDB via feedback_repository.get_feedback_by_user().
    REACT EXPECTATION: GET /feedback/user/101
    RETURNS (JSON Response):
        { 
            "success": True, 
            "user_id": "101", 
            "count": 5, 
            "feedback": [ {feedback1}, {feedback2}, ... ] 
        }
    """
    
    # Fetch feedback entries where user_id matches the parameter.
    feedback = (
        feedback_repository
        .get_feedback_by_user(
            user_id
        )
    )

    return {
        "success": True,
        "user_id": user_id,
        "count": len(feedback),
        "feedback": feedback
    }


# ==========================================
# FOOD FEEDBACK
# ==========================================

@router.get("/food/{food_id}")
def get_food_feedback(
    food_id: str
):
    """
    PURPOSE: Retrieve all feedback related to a specific food item.
    CONNECTS TO: MongoDB via feedback_repository.get_feedback_by_food().
    REACT EXPECTATION: GET /feedback/food/555
    RETURNS (JSON Response):
        { 
            "success": True, 
            "food_id": "555", 
            "count": 12, 
            "feedback": [ {feedback1}, {feedback2}, ... ] 
        }
    """
    
    # Fetch feedback entries where food_id matches the parameter.
    feedback = (
        feedback_repository
        .get_feedback_by_food(
            food_id
        )
    )

    return {
        "success": True,
        "food_id": food_id,
        "count": len(feedback),
        "feedback": feedback
    }


# ==========================================
# LIKE FOOD
# ==========================================

@router.post("/like")
def like_food(
    payload: dict
):
    """
    PURPOSE: Record that a user "liked" a specific food.
    CONNECTS TO: MongoDB via feedback_repository.save_feedback().
    REACT EXPECTATION (Request Body - JSON):
        {
            "user_id": "user123",
            "food_id": "food456"
            // No "liked" field needed in the request; the API adds it automatically.
        }
    RETURNS (JSON Response):
        { 
            "success": True, 
            "feedback_id": "New feedback record ID", 
            "message": "Food liked successfully" 
        }
    """
    
    # Force the 'liked' flag to be True for this endpoint.
    # This ensures that even if the React frontend sends a payload without this field,
    # it is treated as a 'like'.
    payload["liked"] = True

    # Save the feedback to MongoDB using the repository.
    feedback_id = (
        feedback_repository
        .save_feedback(
            payload
        )
    )

    return {
        "success": True,
        "feedback_id": feedback_id,
        "message":
            "Food liked successfully"
    }


# ==========================================
# DISLIKE FOOD
# ==========================================

@router.post("/dislike")
def dislike_food(
    payload: dict
):
    """
    PURPOSE: Record that a user "disliked" a specific food.
    CONNECTS TO: MongoDB via feedback_repository.save_feedback().
    REACT EXPECTATION (Request Body - JSON):
        {
            "user_id": "user123",
            "food_id": "food456"
        }
    RETURNS (JSON Response):
        { 
            "success": True, 
            "feedback_id": "New feedback record ID", 
            "message": "Food disliked successfully" 
        }
    """
    
    # Force the 'liked' flag to be False for this endpoint.
    payload["liked"] = False

    # Save the feedback to MongoDB.
    feedback_id = (
        feedback_repository
        .save_feedback(
            payload
        )
    )

    return {
        "success": True,
        "feedback_id": feedback_id,
        "message":
            "Food disliked successfully"
    }


# ==========================================
# RATE FOOD
# ==========================================

@router.post("/rating")
def rate_food(
    payload: dict
):
    """
    PURPOSE: Record a numerical rating (1-5) for a specific food by a user.
    CONNECTS TO: MongoDB via feedback_repository.save_feedback().
    REACT EXPECTATION (Request Body - JSON):
        {
            "user_id": "user123",
            "food_id": "food456",
            "rating": 5     // Must be integer between 1 and 5.
        }
    ERROR HANDLING: If 'rating' is less than 1 or greater than 5, raises HTTP 400.
    RETURNS (JSON Response):
        { 
            "success": True, 
            "feedback_id": "New feedback record ID", 
            "message": "Rating submitted successfully" 
        }
    """
    
    # Safely extract rating from payload; default to 0 if missing.
    rating = payload.get(
        "rating",
        0
    )

    # Validate rating range.
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=400,
            detail=
            "Rating must be between 1 and 5"
        )

    # Save the feedback to MongoDB.
    feedback_id = (
        feedback_repository
        .save_feedback(
            payload
        )
    )

    return {
        "success": True,
        "feedback_id": feedback_id,
        "message":
            "Rating submitted successfully"
    }


# ==========================================
# AVERAGE FOOD RATING
# ==========================================

@router.get(
    "/food/{food_id}/average-rating"
)
def get_average_food_rating(
    food_id: str
):
    """
    PURPOSE: Calculate the average rating for a specific food item.
    CONNECTS TO: MongoDB via feedback_repository.get_average_food_rating().
    REACT EXPECTATION: GET /feedback/food/999/average-rating
    RETURNS (JSON Response):
        { 
            "success": True, 
            "food_id": "999", 
            "average_rating": 4.5  // float, rounded or handled in repository.
        }
    """
    
    # Ask the repository to compute the average rating for the given food ID.
    # The repository is responsible for the MongoDB aggregation (e.g., $group, $avg).
    average_rating = (
        feedback_repository
        .get_average_food_rating(
            food_id
        )
    )

    return {
        "success": True,
        "food_id": food_id,
        "average_rating":
            average_rating
    }


# ==========================================
# LIKED FOODS
# ==========================================

@router.get(
    "/user/{user_id}/liked-foods"
)
def get_liked_foods(
    user_id: str
):
    """
    PURPOSE: Retrieve a list of food items that a user has liked.
    CONNECTS TO: MongoDB via feedback_repository.get_liked_foods().
    REACT EXPECTATION: GET /feedback/user/123/liked-foods
    RETURNS (JSON Response):
        { 
            "success": True, 
            "user_id": "123", 
            "liked_foods": [ "food1", "food2", ... ] // List of food IDs/names.
        }
    """
    
    # Fetch the list of liked foods for the specified user.
    foods = (
        feedback_repository
        .get_liked_foods(
            user_id
        )
    )

    return {
        "success": True,
        "user_id": user_id,
        "liked_foods": foods
    }


# ==========================================
# DISLIKED FOODS
# ==========================================

@router.get(
    "/user/{user_id}/disliked-foods"
)
def get_disliked_foods(
    user_id: str
):
    """
    PURPOSE: Retrieve a list of food items that a user has disliked.
    CONNECTS TO: MongoDB via feedback_repository.get_disliked_foods().
    REACT EXPECTATION: GET /feedback/user/123/disliked-foods
    RETURNS (JSON Response):
        { 
            "success": True, 
            "user_id": "123", 
            "disliked_foods": [ "food3", "food4", ... ] // List of food IDs/names.
        }
    """
    
    # Fetch the list of disliked foods for the specified user.
    foods = (
        feedback_repository
        .get_disliked_foods(
            user_id
        )
    )

    return {
        "success": True,
        "user_id": user_id,
        "disliked_foods": foods
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@router.get("/health")
def feedback_health():
    """
    PURPOSE: Lightweight health check for the Feedback API router.
    USE CASE: Kubernetes, AWS, or other cloud monitoring tools can ping this 
            endpoint to verify the feedback service is responding.
    RETURNS (JSON Response):
        { "success": True, "service": "feedback", "status": "healthy" }
    """
    
    return {
        "success": True,
        "service": "feedback",
        "status": "healthy"
    }