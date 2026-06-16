# # 🚀 Backend Developer Integration Guide (MongoDB, React, API)
# 1. Current Implementation (JSON File)
# Pros: Simple, no external dependencies, easy to move between environments.

# Cons: Not suitable for large-scale, high-concurrency production; file locking issues; no indexing; slow for large datasets.

# 2. How to Migrate to MongoDB (Step-by-Step)
# Step 1: Install pymongo
# bash
# pip install pymongo
# Step 2: Update __init__ to accept MongoDB client
# python
# from pymongo import MongoClient, ASCENDING

# class UserRepository:
#     def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="food_app"):
#         self.client = MongoClient(mongo_uri)
#         self.db = self.client[db_name]
#         self.collection = self.db["users"]
#         # Create indexes for efficient queries
#         self.collection.create_index("user_id", unique=True)
#         self.collection.create_index("email", unique=True)
#         self.collection.create_index("created_at")
# Step 3: Replace file-based methods with MongoDB CRUD
# _load_users → Remove, use list(self.collection.find({})) directly.

# _save_users → Remove, use individual updates.

# create_user:

# python
# def create_user(self, user_data: Dict) -> str:
#     user_id = str(uuid.uuid4())
#     timestamp = datetime.utcnow().isoformat()
#     user_record = {
#         "user_id": user_id,
#         "created_at": timestamp,
#         "updated_at": timestamp,
#         **user_data,
#         "meal_history": [],
#         "feedback_history": [],
#         "food_preferences": [],
#         "food_dislikes": []
#     }
#     self.collection.insert_one(user_record)
#     return user_id
# get_user:

# python
# def get_user(self, user_id: str) -> Optional[Dict]:
#     return self.collection.find_one({"user_id": user_id})
# update_user:

# python
# def update_user(self, user_id: str, updated_data: Dict) -> bool:
#     updated_data["updated_at"] = datetime.utcnow().isoformat()
#     result = self.collection.update_one(
#         {"user_id": user_id},
#         {"$set": updated_data}
#     )
#     return result.modified_count > 0
# add_food_preference (MongoDB $addToSet for deduplication):

# python
# def add_food_preference(self, user_id: str, food_name: str) -> bool:
#     result = self.collection.update_one(
#         {"user_id": user_id},
#         {"$addToSet": {"food_preferences": food_name}}
#     )
#     return result.modified_count > 0
# 3. React Frontend Integration
# React never calls UserRepository directly. It calls the API endpoints in app/api/users.py.

# Example React call:

# javascript
# // Register a new user
# const registerUser = async (userData) => {
#   const response = await fetch('http://localhost:8000/users/', {
#     method: 'POST',
#     headers: { 'Content-Type': 'application/json' },
#     body: JSON.stringify(userData)
#   });
#   const data = await response.json();
#   return data.user_id;
# };

# // Update user weight and activity level
# const updateUser = async (userId, updates) => {
#   const response = await fetch(`http://localhost:8000/users/${userId}`, {
#     method: 'PUT',
#     headers: { 'Content-Type': 'application/json' },
#     body: JSON.stringify(updates)
#   });
#   return response.ok;
# };
# 4. Important Notes for Production
# Current (JSON)	MongoDB Migration
# ✅ No external dependencies	✅ Scalable, concurrent writes
# ❌ File I/O not thread-safe	✅ Atomic operations via update_one
# ❌ No indexing	✅ Indexes on user_id, email, created_at
# ❌ Manual file rewriting	✅ Document-level updates
# ❌ Limited to local filesystem	✅ Distributed databases (Atlas, replica sets)
# 5. Indexing Recommendations for MongoDB
# Once migrated, create these indexes for optimal performance:

# python
# self.collection.create_index("user_id", unique=True)  # For fast lookups
# self.collection.create_index("email", unique=True)     # For login/authentication
# self.collection.create_index("created_at")             # For sorting by registration date
# self.collection.create_index([("food_preferences", 1)]) # For preference-based queries
# 6. Security Note
# The user_data dictionary in create_user includes sensitive fields (email, password if used). In production, always hash passwords before storing and never log the entire user object. Use Pydantic schemas (UserProfileSchema) to validate input before reaching the repository.
# 
# 
# ============================================================================
# FILE: app/repositories/user_repository.py
# ROLE: This file is the DATA ACCESS LAYER for user data. It provides CRUD
#       operations and additional management features such as meal history,
#       feedback history, food preferences, and food dislikes. It currently
#       uses a JSON file (database/users.json) as the storage backend, but
#       is structured to be easily migrated to MongoDB for production use.
# CONNECTIONS:
#   - API Layer (app/api/users.py): The endpoints in the Users API (create_user,
#     get_user, update_user, etc.) call methods from this repository.
#   - MongoDB (Future): For migration, replace file I/O methods with MongoDB
#     collection operations. Keep method signatures identical to avoid API
#     layer changes.
#   - React Frontend: React never calls this repository directly. It calls the
#     API endpoints in app/api/users.py, which internally use this repository.
#   - Other Services: Services like MealGenerator or RankingService might
#     call get_user() to retrieve user preferences for personalized recommendations.
# ============================================================================

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class UserRepository:
    """
    PURPOSE: Handles all persistence operations for user accounts and their
             associated data (meal history, feedback, preferences, dislikes).
    CURRENT STORAGE: JSON file (simple, portable, no external dependencies).
    KEY FEATURES:
        - Create a new user with a unique UUID.
        - Retrieve a user by ID.
        - Update user fields (partial updates).
        - Delete a user.
        - Track meal plan generation history.
        - Track feedback history.
        - Manage food preferences and dislikes (used for recommendation filtering).
    BACKEND NOTE: For production, replace the JSON file with MongoDB. The method
                  signatures are designed to be compatible with MongoDB, so the
                  API layer won't require changes.
    """

    def __init__(
        self,
        storage_file: str = "database/users.json"
    ):
        """
        PURPOSE: Initialize the repository with the path to the JSON storage file.
        PARAMETERS:
            storage_file (str): Path to the JSON file (default: "database/users.json").
        BEHAVIOR:
            - Converts the path to a Path object.
            - Creates the parent directory if it doesn't exist.
            - Calls _initialize_storage() to ensure the file exists.
        """
        self.storage_file = Path(
            storage_file
        )

        self._initialize_storage()

    def _initialize_storage(
        self
    ) -> None:
        """
        PURPOSE: Ensure the storage file and its parent directory exist.
        BEHAVIOR:
            - Creates the 'database/' directory if missing.
            - Creates an empty JSON list '[]' if the file doesn't exist.
        CONNECTS TO: File system (disk).
        BACKEND NOTE: When migrating to MongoDB, this method becomes unnecessary.
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

    def _load_users(
        self
    ) -> List[Dict]:
        """
        PURPOSE: Load all user records from the JSON file into memory.
        RETURNS: List[Dict] - A list of user dictionaries.
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
            json.JSONDecodeError,
            FileNotFoundError
        ):
            # If the file is corrupted or missing, start fresh.
            return []

    def _save_users(
        self,
        users: List[Dict]
    ) -> None:
        """
        PURPOSE: Write the entire users list back to the JSON file.
        PARAMETERS: users (List[Dict]) - The updated list of users.
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
                users,
                file,
                indent=4,
                ensure_ascii=False  # Allows non-ASCII characters (e.g., emojis)
            )

    def create_user(
        self,
        user_data: Dict
    ) -> str:
        """
        PURPOSE: Create a new user and store it in the database.
        PARAMETERS:
            user_data (Dict): The user's profile data. Must contain at least the
                              fields required by UserProfileSchema (age, gender,
                              weight, height, activity_level, goal, etc.).
        RETURNS: str - A unique UUID for the user.
        BEHAVIOR:
            - Generates a UUID4 for user_id.
            - Adds timestamps (created_at, updated_at).
            - Initializes empty lists for meal_history, feedback_history,
              food_preferences, food_dislikes.
            - Appends the user record to the JSON file.
        CONNECTS TO: API endpoint POST /users/ (in app/api/users.py).
        BACKEND NOTE: The user_data dict should contain at least the fields
                      expected by the API's UserProfileSchema. No validation
                      is performed here; the API layer handles validation.
        """
        users = self._load_users()

        user_id = str(
            uuid.uuid4()
        )

        timestamp = (
            datetime.utcnow()
            .isoformat()
        )

        user_record = {
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            **user_data,  # Spread the original user data into the record.
            "meal_history": [],
            "feedback_history": [],
            "food_preferences": [],
            "food_dislikes": []
        }

        users.append(
            user_record
        )

        self._save_users(
            users
        )

        return user_id

    def get_user(
        self,
        user_id: str
    ) -> Optional[Dict]:
        """
        PURPOSE: Retrieve a user's full record by their unique ID.
        PARAMETERS:
            user_id (str): The UUID of the user.
        RETURNS: Optional[Dict] - The user record if found, else None.
        CONNECTS TO: API endpoint GET /users/{user_id} (in app/api/users.py).
        """
        users = self._load_users()

        for user in users:
            if (
                user.get(
                    "user_id"
                )
                ==
                user_id
            ):
                return user

        return None

    def get_all_users(
        self
    ) -> List[Dict]:
        """
        PURPOSE: Retrieve all user records from the database.
        RETURNS: List[Dict] - A list of all users.
        CONNECTS TO: API endpoints for analytics or admin dashboards.
        BACKEND NOTE: This method loads the entire file into memory. For large
                      user bases (>10,000), consider pagination or MongoDB queries.
        """
        return self._load_users()

    def user_exists(
        self,
        user_id: str
    ) -> bool:
        """
        PURPOSE: Check if a user exists by ID.
        PARAMETERS:
            user_id (str): The UUID of the user.
        RETURNS: bool - True if the user exists, False otherwise.
        CONNECTS TO: API validation before operations like update or delete.
        """
        return (
            self.get_user(
                user_id
            )
            is not None
        )

    def update_user(
        self,
        user_id: str,
        updated_data: Dict
    ) -> bool:
        """
        PURPOSE: Update specific fields of a user's record.
        PARAMETERS:
            user_id (str): The UUID of the user.
            updated_data (Dict): A dictionary of fields to update (partial update).
        RETURNS: bool - True if updated, False if user not found.
        CONNECTS TO: API endpoint PUT /users/{user_id} (in app/api/users.py).
        BEHAVIOR:
            - Finds the user by ID.
            - Updates the user record with the provided fields.
            - Updates the 'updated_at' timestamp.
            - Saves changes to the JSON file.
        BACKEND NOTE: The API layer should use UserUpdateSchema with
                      `exclude_none=True` to ensure only provided fields are updated.
        """
        users = self._load_users()

        for user in users:
            if (
                user.get(
                    "user_id"
                )
                ==
                user_id
            ):
                user.update(
                    updated_data
                )

                user[
                    "updated_at"
                ] = (
                    datetime.utcnow()
                    .isoformat()
                )

                self._save_users(
                    users
                )

                return True

        return False

    def delete_user(
        self,
        user_id: str
    ) -> bool:
        """
        PURPOSE: Permanently delete a user from the database.
        PARAMETERS:
            user_id (str): The UUID of the user to delete.
        RETURNS: bool - True if deleted, False if not found.
        CONNECTS TO: API endpoint DELETE /users/{user_id} (in app/api/users.py).
        BEHAVIOR:
            - Removes the user from the list.
            - Rewrites the JSON file.
        """
        users = self._load_users()

        original_count = len(
            users
        )

        # Filter out the user with the matching ID.
        users = [
            user
            for user in users
            if user.get(
                "user_id"
            )
            != user_id
        ]

        # If the count didn't change, nothing was deleted.
        if (
            len(users)
            ==
            original_count
        ):
            return False

        self._save_users(
            users
        )

        return True

    def add_meal_plan_history(
        self,
        user_id: str,
        meal_plan: Dict
    ) -> bool:
        """
        PURPOSE: Record that a user generated a meal plan, adding it to their history.
        PARAMETERS:
            user_id (str): The UUID of the user.
            meal_plan (Dict): The meal plan data (as generated by MealGenerator).
        RETURNS: bool - True if added, False if user not found.
        CONNECTS TO: API endpoint POST /meal-plans/generate (or a background process).
        BEHAVIOR:
            - Finds the user by ID.
            - Appends the meal plan to the 'meal_history' list.
            - Saves changes to the JSON file.
        BACKEND NOTE: This can be called automatically when a user generates a meal plan
                      via the meal_plans API. It allows users to see their past meal plans.
        """
        users = self._load_users()

        for user in users:
            if (
                user.get(
                    "user_id"
                )
                ==
                user_id
            ):
                user.setdefault(
                    "meal_history",
                    []
                )

                user[
                    "meal_history"
                ].append(
                    meal_plan
                )

                self._save_users(
                    users
                )

                return True

        return False

    def get_meal_history(
        self,
        user_id: str
    ) -> List[Dict]:
        """
        PURPOSE: Retrieve the meal plan history for a user.
        PARAMETERS:
            user_id (str): The UUID of the user.
        RETURNS: List[Dict] - A list of meal plans the user has generated.
                  Returns empty list if user not found or no history exists.
        CONNECTS TO: API endpoint GET /users/{user_id}/meal-history (or similar).
        """
        user = self.get_user(
            user_id
        )

        if not user:
            return []

        return user.get(
            "meal_history",
            []
        )

    def add_feedback(
        self,
        user_id: str,
        feedback: Dict
    ) -> bool:
        """
        PURPOSE: Record feedback submitted by a user in their history.
        PARAMETERS:
            user_id (str): The UUID of the user.
            feedback (Dict): The feedback data (from FeedbackRepository).
        RETURNS: bool - True if added, False if user not found.
        CONNECTS TO: API endpoint POST /feedback/ (and its variations).
        BEHAVIOR:
            - Finds the user by ID.
            - Appends the feedback to the 'feedback_history' list.
            - Saves changes to the JSON file.
        BACKEND NOTE: This keeps a copy of feedback in the user's record.
                      Useful for analyzing user behavior over time.
        """
        users = self._load_users()

        for user in users:
            if (
                user.get(
                    "user_id"
                )
                ==
                user_id
            ):
                user.setdefault(
                    "feedback_history",
                    []
                )

                user[
                    "feedback_history"
                ].append(
                    feedback
                )

                self._save_users(
                    users
                )

                return True

        return False

    def get_feedback_history(
        self,
        user_id: str
    ) -> List[Dict]:
        """
        PURPOSE: Retrieve the feedback history for a user.
        PARAMETERS:
            user_id (str): The UUID of the user.
        RETURNS: List[Dict] - A list of feedback entries the user has submitted.
                  Returns empty list if user not found or no feedback history exists.
        CONNECTS TO: API endpoint GET /users/{user_id}/feedback-history (or similar).
        """
        user = self.get_user(
            user_id
        )

        if not user:
            return []

        return user.get(
            "feedback_history",
            []
        )

    def add_food_preference(
        self,
        user_id: str,
        food_name: str
    ) -> bool:
        """
        PURPOSE: Add a food to the user's list of preferred foods.
        PARAMETERS:
            user_id (str): The UUID of the user.
            food_name (str): The name of the food (canonical_food_name).
        RETURNS: bool - True if added, False if user not found.
        CONNECTS TO: API endpoint (e.g., POST /users/{user_id}/preferences).
        BEHAVIOR:
            - Finds the user by ID.
            - Adds the food name to the 'food_preferences' list if not already present.
            - Saves changes to the JSON file.
        BACKEND NOTE: The list is deduplicated (set-like behavior). This data is
                      used by recommendation systems to boost foods the user likes.
        """
        users = self._load_users()

        for user in users:
            if (
                user.get(
                    "user_id"
                )
                ==
                user_id
            ):
                preferences = (
                    user.setdefault(
                        "food_preferences",
                        []
                    )
                )

                if (
                    food_name
                    not in preferences
                ):
                    preferences.append(
                        food_name
                    )

                self._save_users(
                    users
                )

                return True

        return False

    def add_food_dislike(
        self,
        user_id: str,
        food_name: str
    ) -> bool:
        """
        PURPOSE: Add a food to the user's list of disliked foods.
        PARAMETERS:
            user_id (str): The UUID of the user.
            food_name (str): The name of the food (canonical_food_name).
        RETURNS: bool - True if added, False if user not found.
        CONNECTS TO: API endpoint (e.g., POST /users/{user_id}/dislikes).
        BEHAVIOR:
            - Finds the user by ID.
            - Adds the food name to the 'food_dislikes' list if not already present.
            - Saves changes to the JSON file.
        BACKEND NOTE: The list is deduplicated. This data is used by recommendation
                      systems to filter out foods the user dislikes.
        """
        users = self._load_users()

        for user in users:
            if (
                user.get(
                    "user_id"
                )
                ==
                user_id
            ):
                dislikes = (
                    user.setdefault(
                        "food_dislikes",
                        []
                    )
                )

                if (
                    food_name
                    not in dislikes
                ):
                    dislikes.append(
                        food_name
                    )

                self._save_users(
                    users
                )

                return True

        return False