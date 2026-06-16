# #🚀 Backend Developer Integration Guide (MongoDB & React)
# 1. Current Implementation (JSON File)
# This repository stores all feedback in database/feedback.json.

# Pros: No external dependencies, easy to move between environments.

# Cons: Not suitable for large-scale, high-concurrency production.

# 2. How to Migrate to MongoDB
# To switch to MongoDB, replace the file I/O methods with MongoDB collection operations. Keep all method signatures identical so the API layer doesn't need to change.

# Example MongoDB Migration:

# python
# from pymongo import MongoClient, ASCENDING
# from bson import ObjectId

# class FeedbackRepository:
#     def __init__(self, mongo_uri="mongodb://localhost:27017/"):
#         self.client = MongoClient(mongo_uri)
#         self.db = self.client.food_app
#         self.collection = self.db.feedback
#         # Create indexes for fast queries
#         self.collection.create_index("user_id")
#         self.collection.create_index("food_id")
#         self.collection.create_index("feedback_id", unique=True)

#     def save_feedback(self, feedback):
#         feedback_id = str(uuid.uuid4())
#         record = {
#             "feedback_id": feedback_id,
#             "created_at": datetime.utcnow().isoformat(),
#             **feedback
#         }
#         self.collection.insert_one(record)
#         return feedback_id

#     def get_feedback_by_user(self, user_id):
#         return list(self.collection.find({"user_id": user_id}))
# 3. React Frontend Integration
# The API endpoints in app/api/feedback.py use this repository. React calls those endpoints.

# Example React call:

# javascript
# // Submit a rating
# const rateFood = async (userId, foodId, rating) => {
#   const response = await fetch('http://localhost:8000/feedback/rating', {
#     method: 'POST',
#     headers: { 'Content-Type': 'application/json' },
#     body: JSON.stringify({ user_id: userId, food_id: foodId, rating })
#   });
#   const data = await response.json();
#   return data;
# };
# 4. Important Notes for Production
# Concurrency: The JSON file approach is not thread-safe if multiple API requests write simultaneously. Use MongoDB for production.

# Indexing: When moving to MongoDB, add indexes on user_id, food_id, and feedback_id for fast queries.

# Cleanup: Over time, feedback.json can grow large. MongoDB handles that gracefully.
# 
# 
#  ============================================================================
# FILE: app/repositories/feedback_repository.py
# ROLE: This file is the DATA ACCESS LAYER for feedback operations.
#       It currently uses a JSON file (database/feedback.json) as storage
#       but is designed to be easily replaced with MongoDB for production.
# CONNECTIONS:
#   - API Layer (app/api/feedback.py): This file is used by the Feedback API
#     to read, write, and query feedback data.
#   - MongoDB (Future): When moving to MongoDB, keep the same method signatures
#     but replace file I/O with MongoDB collection operations.
#   - React Frontend: React never calls this file directly. React calls the API
#     endpoints which use these repository methods.
# ============================================================================

import json
import uuid

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class FeedbackRepository:
    """
    PURPOSE: Manages persistence for user feedback, ratings, likes, and dislikes.
    CURRENT STORAGE: JSON file (simple, portable, no external dependencies).
    FUTURE MIGRATION: To switch to MongoDB, modify _load_feedback, _save_feedback,
                      and replace all file operations with MongoDB CRUD.
    KEY METHODS:
        - save_feedback(feedback): Create a new feedback entry.
        - get_feedback_by_user(user_id): Retrieve all feedback for a user.
        - get_average_food_rating(food_id): Calculate average rating for a food.
        - get_liked_foods(user_id): Get list of foods a user has liked.
    """

    def __init__(
        self,
        storage_file: str = "database/feedback.json"
    ):
        """
        PURPOSE: Initialize the repository with the path to the JSON storage file.
        PARAMETERS:
            storage_file: str - Path to the JSON file (relative to project root).
        BEHAVIOR:
            - Creates the parent directory if it doesn't exist.
            - Calls _initialize_storage() to ensure the file exists.
        """
        self.storage_file = Path(
            storage_file
        )

        self._initialize_storage()

    def _initialize_storage(
        self
    ):
        """
        PURPOSE: Ensure the storage file and its parent directory exist.
        BEHAVIOR:
            - Creates the 'database/' directory if missing.
            - Creates an empty JSON list '[]' if the file doesn't exist.
        CONNECTS TO: File system (disk).
        """
        self.storage_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.storage_file.exists():
            # Create an empty JSON array as the initial data.
            with open(
                self.storage_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    [],
                    file,
                    indent=4
                )

    def _load_feedback(
        self
    ) -> List[Dict]:
        """
        PURPOSE: Load all feedback records from the JSON file into memory.
        RETURNS: List[Dict] - A list of feedback dictionaries.
        ERROR HANDLING:
            - If the file doesn't exist or contains invalid JSON, returns an empty list.
        BACKEND NOTE: If migrating to MongoDB, replace this method with
                      `list(self.collection.find({}))`.
        """
        try:
            with open(
                self.storage_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

                if isinstance(
                    data,
                    list
                ):
                    return data

                return []

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):
            # If the file is corrupted or missing, start fresh.
            return []

    def _save_feedback(
        self,
        feedback_list: List[Dict]
    ):
        """
        PURPOSE: Write the entire feedback list back to the JSON file.
        PARAMETERS: feedback_list (List[Dict]) - The updated list of feedback.
        CONNECTS TO: File system (disk).
        BACKEND NOTE: If migrating to MongoDB, this method becomes unnecessary
                      as each operation will directly update the database.
        """
        with open(
            self.storage_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                feedback_list,
                file,
                indent=4,
                ensure_ascii=False  # Allows non-ASCII characters (e.g., emojis)
            )

    def save_feedback(
        self,
        feedback: Dict
    ) -> str:
        """
        PURPOSE: Insert a new feedback record into the storage.
        PARAMETERS:
            feedback (Dict): The feedback data (e.g., user_id, food_id, rating, liked).
        RETURNS: str - A unique UUID for the feedback entry.
        BEHAVIOR:
            - Generates a UUID4 for feedback_id.
            - Adds a 'created_at' timestamp (UTC ISO format).
            - Appends the record to the list and saves to file.
        CONNECTS TO: API (app/api/feedback.py) via submit_feedback, like, dislike, rating.
        """
        feedback_list = (
            self._load_feedback()
        )

        feedback_id = str(
            uuid.uuid4()
        )

        record = {
            "feedback_id":
                feedback_id,
            "created_at":
                datetime.utcnow()
                .isoformat(),
            **feedback  # Spread the original feedback dict into the record.
        }

        feedback_list.append(
            record
        )

        self._save_feedback(
            feedback_list
        )

        return feedback_id

    def get_all_feedback(
        self
    ) -> List[Dict]:
        """
        PURPOSE: Retrieve all feedback records.
        RETURNS: List[Dict] - All feedback entries.
        BACKEND NOTE: Used by analytics endpoints to get total feedback count.
        """
        return (
            self._load_feedback()
        )

    def get_feedback(
        self,
        feedback_id: str
    ) -> Optional[Dict]:
        """
        PURPOSE: Retrieve a single feedback record by its unique ID.
        PARAMETERS: feedback_id (str) - The UUID of the feedback.
        RETURNS: Optional[Dict] - The feedback record if found, else None.
        CONNECTS TO: API endpoint GET /feedback/{feedback_id}.
        """
        for feedback in (
            self._load_feedback()
        ):
            if (
                feedback.get(
                    "feedback_id"
                )
                ==
                feedback_id
            ):
                return feedback

        return None

    def feedback_exists(
        self,
        feedback_id: str
    ) -> bool:
        """
        PURPOSE: Check if a feedback record exists by ID.
        PARAMETERS: feedback_id (str) - The UUID of the feedback.
        RETURNS: bool - True if the feedback exists, False otherwise.
        CONNECTS TO: API validation before delete/update operations.
        """
        return (
            self.get_feedback(
                feedback_id
            )
            is not None
        )

    def get_feedback_by_user(
        self,
        user_id: str
    ) -> List[Dict]:
        """
        PURPOSE: Retrieve all feedback submitted by a specific user.
        PARAMETERS: user_id (str) - The user's ID (from MongoDB or UserRepository).
        RETURNS: List[Dict] - List of feedback entries for that user.
        CONNECTS TO: API endpoint GET /feedback/user/{user_id}.
        BACKEND NOTE: This method uses a simple list comprehension. If the
                      feedback list grows very large (>10,000 entries), consider
                      indexing in MongoDB or using a dictionary lookup.
        """
        return [
            feedback
            for feedback in (
                self._load_feedback()
            )
            if (
                feedback.get(
                    "user_id"
                )
                ==
                user_id
            )
        ]

    def get_feedback_by_food(
        self,
        food_id: str
    ) -> List[Dict]:
        """
        PURPOSE: Retrieve all feedback related to a specific food item.
        PARAMETERS: food_id (str) - The food's ID (from FoodRepository).
        RETURNS: List[Dict] - List of feedback entries for that food.
        CONNECTS TO: API endpoints GET /feedback/food/{food_id} and
                     GET /feedback/food/{food_id}/average-rating.
        """
        return [
            feedback
            for feedback in (
                self._load_feedback()
            )
            if (
                feedback.get(
                    "food_id"
                )
                ==
                food_id
            )
        ]

    def get_feedback_by_meal_plan(
        self,
        meal_plan_id: str
    ) -> List[Dict]:
        """
        PURPOSE: Retrieve feedback entries associated with a specific meal plan.
        PARAMETERS: meal_plan_id (str) - The meal plan's ID.
        RETURNS: List[Dict] - Feedback entries for that meal plan.
        CONNECTS TO: API endpoints that need feedback on meal plans.
        """
        return [
            feedback
            for feedback in (
                self._load_feedback()
            )
            if (
                feedback.get(
                    "meal_plan_id"
                )
                ==
                meal_plan_id
            )
        ]

    def delete_feedback(
        self,
        feedback_id: str
    ) -> bool:
        """
        PURPOSE: Delete a feedback record by its ID.
        PARAMETERS: feedback_id (str) - The UUID of the feedback to delete.
        RETURNS: bool - True if deleted, False if not found.
        CONNECTS TO: API endpoint DELETE /feedback/{feedback_id}.
        BEHAVIOR: Removes the entry from the list and rewrites the JSON file.
        """
        feedback_list = (
            self._load_feedback()
        )

        original_count = len(
            feedback_list
        )

        # Filter out the feedback with the matching ID.
        feedback_list = [
            feedback
            for feedback in feedback_list
            if (
                feedback.get(
                    "feedback_id"
                )
                != feedback_id
            )
        ]

        # If the count didn't change, nothing was deleted.
        if (
            len(feedback_list)
            ==
            original_count
        ):
            return False

        self._save_feedback(
            feedback_list
        )

        return True

    def get_average_food_rating(
        self,
        food_id: str
    ) -> float:
        """
        PURPOSE: Compute the average rating (1-5) for a food item.
        PARAMETERS: food_id (str) - The food's ID.
        RETURNS: float - Average rating rounded to 2 decimal places.
                   Returns 0.0 if there are no ratings.
        CONNECTS TO: API endpoint GET /feedback/food/{food_id}/average-rating.
        BEHAVIOR: Ignores feedback entries without a 'rating' field.
        """
        feedback_items = (
            self.get_feedback_by_food(
                food_id
            )
        )

        # Extract only the ratings that are not None.
        ratings = [
            item.get(
                "rating"
            )
            for item in feedback_items
            if (
                item.get(
                    "rating"
                )
                is not None
            )
        ]

        if not ratings:
            return 0.0

        return round(
            sum(ratings)
            /
            len(ratings),
            2
        )

    def get_average_meal_plan_rating(
        self,
        meal_plan_id: str
    ) -> float:
        """
        PURPOSE: Compute the average rating for a meal plan.
        PARAMETERS: meal_plan_id (str) - The meal plan's ID.
        RETURNS: float - Average rating rounded to 2 decimal places.
        CONNECTS TO: API endpoints that display meal plan ratings.
        """
        feedback_items = (
            self.get_feedback_by_meal_plan(
                meal_plan_id
            )
        )

        ratings = [
            item.get(
                "rating"
            )
            for item in feedback_items
            if (
                item.get(
                    "rating"
                )
                is not None
            )
        ]

        if not ratings:
            return 0.0

        return round(
            sum(ratings)
            /
            len(ratings),
            2
        )

    def get_liked_foods(
        self,
        user_id: str
    ) -> List[str]:
        """
        PURPOSE: Retrieve the list of food IDs that a user has liked.
        PARAMETERS: user_id (str) - The user's ID.
        RETURNS: List[str] - A deduplicated list of food IDs.
        CONNECTS TO: API endpoint GET /feedback/user/{user_id}/liked-foods.
        BEHAVIOR: Filters feedback where 'liked' is True and returns food_id.
                  Uses set() to remove duplicates (if a user liked the same food
                  multiple times, it appears only once).
        """
        feedback_items = (
            self.get_feedback_by_user(
                user_id
            )
        )

        liked_foods = []

        for item in feedback_items:
            if (
                item.get(
                    "liked"
                )
                is True
            ):
                food_id = item.get(
                    "food_id"
                )
                if food_id:
                    liked_foods.append(
                        food_id
                    )

        # Remove duplicates by converting to set and back to list.
        return list(
            set(
                liked_foods
            )
        )

    def get_disliked_foods(
        self,
        user_id: str
    ) -> List[str]:
        """
        PURPOSE: Retrieve the list of food IDs that a user has disliked.
        PARAMETERS: user_id (str) - The user's ID.
        RETURNS: List[str] - A deduplicated list of food IDs.
        CONNECTS TO: API endpoint GET /feedback/user/{user_id}/disliked-foods.
        BEHAVIOR: Filters feedback where 'liked' is False and returns food_id.
        """
        feedback_items = (
            self.get_feedback_by_user(
                user_id
            )
        )

        disliked_foods = []

        for item in feedback_items:
            if (
                item.get(
                    "liked"
                )
                is False
            ):
                food_id = item.get(
                    "food_id"
                )
                if food_id:
                    disliked_foods.append(
                        food_id
                    )

        return list(
            set(
                disliked_foods
            )
        )