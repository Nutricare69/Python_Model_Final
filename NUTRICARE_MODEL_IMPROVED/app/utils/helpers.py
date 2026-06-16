# # 🚀 Backend Developer Integration Guide (MongoDB, React, API)
# 1. Usage in API Endpoints
# Any FastAPI endpoint can import Helpers and use its methods:

# python
# from fastapi import APIRouter
# from app.utils.helpers import Helpers

# router = APIRouter()

# @router.get("/stats")
# def get_stats():
#     score = Helpers.clamp(150, 0, 100)  # -> 100
#     label = Helpers.create_day_label(3)  # -> "Day 03"
#     return {"score": score, "label": label}
# 2. Usage in MongoDB Repositories
# When fetching data from MongoDB, use safe conversion methods to handle missing/irregular fields:

# python
# def get_user(self, user_id: str):
#     user = self.collection.find_one({"user_id": user_id})
#     if user:
#         # Ensure weight is a float
#         user["weight"] = Helpers.safe_float(user.get("weight"))
#         # Ensure activity_level is not empty
#         if Helpers.is_empty(user.get("activity_level")):
#             user["activity_level"] = "Sedentary"
#     return user
# 3. React Frontend Integration
# Frontend developers can directly use formatted strings from the API without extra processing:

# javascript
# // React component
# const MealMacros = ({ protein, carbs, fat }) => {
#   const { protein_percent, carb_percent, fat_percent } = 
#     Helpers.calculate_macro_percentages(protein, carbs, fat);
#   // Display percentages in a pie chart or progress bars
# };
# 4. Key Points for Backend Developers
# Statelessness: All methods are @staticmethod, so no self parameter. Just call Helpers.method_name().

# Error Resilience: Methods like safe_float, safe_int, and is_empty help handle messy data from MongoDB or external inputs without crashing.

# Consistent Formatting: Formatting methods (format_calories, format_grams, format_liters) ensure all numbers are displayed uniformly across the frontend.

# Testability: Because the class is stateless, unit testing these helpers is straightforward:

# python
# def test_safe_float():
#     assert Helpers.safe_float("123") == 123.0
#     assert Helpers.safe_float("abc", default=5) == 5.0
# 
# ============================================================================
# FILE: app/utils/helpers.py
# ROLE: This file provides a collection of reusable helper functions used
#       throughout the application. These helpers handle common operations like
#       safe type conversion, data formatting, validation, and utility tasks.
#       By centralizing these utilities, the backend developer avoids code
#       duplication and ensures consistent behavior across services.
# CONNECTIONS:
#   - API Layer: Any FastAPI endpoint can import these helpers for tasks like
#     safe float conversion, percentage calculation, score normalization,
#     UUID generation, and timestamp creation.
#   - MongoDB: Helper functions like `safe_float`, `safe_int`, and `is_empty`
#     are useful when processing data retrieved from MongoDB where fields might
#     be missing, None, or of unexpected types.
#   - React Frontend: Helper functions like `format_calories`, `format_grams`,
#     `format_liters`, `calculate_macro_percentages`, and `calculate_bmi_category_color`
#     are designed to produce human-readable strings that can be directly
#     consumed by the React frontend. They help maintain consistent formatting.
#   - Services: All service classes (e.g., CalorieService, RankingService,
#     MealGenerator) use these helpers to avoid reinventing the wheel for
#     common tasks like rounding, percentage calculation, and UUID generation.
# ============================================================================

import uuid
from datetime import datetime
from typing import Any, Optional


class Helpers:
    """
    PURPOSE: A static utility class containing various helper functions.
    All methods are @staticmethod, meaning they can be called without
    instantiating the class. This class is stateless and purely functional.

    USAGE EXAMPLES:
        # Convert a string to float safely
        value = Helpers.safe_float("123.45", default=0.0)  # returns 123.45

        # Calculate macro percentages
        macros = Helpers.calculate_macro_percentages(150, 200, 50)

        # Generate a day label for frontend display
        label = Helpers.create_day_label(3)  # returns "Day 03"

        # Get a color for BMI category
        color = Helpers.calculate_bmi_category_color("Normal Weight")  # returns "green"
    """

    # ==========================================
    # SAFE FLOAT CONVERSION
    # ==========================================
    @staticmethod
    def safe_float(
        value: Any,
        default: float = 0.0
    ) -> float:
        """
        PURPOSE: Safely convert any input value to a float.
        PARAMETERS:
            value (Any): The input value (e.g., from MongoDB, CSV, or request).
            default (float): Value to return if conversion fails (default 0.0).
        RETURNS: float – The converted value, or `default` if conversion fails.
        CONNECTS TO:
            - MongoDB: When retrieving numeric fields that might be stored as
              strings or might be missing, this function prevents crashes.
            - API Layer: When parsing query parameters or request bodies.
        EXAMPLE:
            Helpers.safe_float("42.5")       -> 42.5
            Helpers.safe_float("invalid")    -> 0.0
            Helpers.safe_float(None)         -> 0.0
        """
        try:
            return float(value)
        except (
            ValueError,
            TypeError
        ):
            return default

    # ==========================================
    # SAFE INT CONVERSION
    # ==========================================
    @staticmethod
    def safe_int(
        value: Any,
        default: int = 0
    ) -> int:
        """
        PURPOSE: Safely convert any input value to an integer.
        PARAMETERS:
            value (Any): The input value.
            default (int): Value to return if conversion fails (default 0).
        RETURNS: int – The converted value, or `default` if conversion fails.
        CONNECTS TO:
            - MongoDB: Used when reading numeric IDs or counts that might be
              stored as strings or missing.
            - API: When processing `top_n` parameters from query strings.
        EXAMPLE:
            Helpers.safe_int("42")       -> 42
            Helpers.safe_int("invalid")  -> 0
            Helpers.safe_int(None)       -> 0
        """
        try:
            return int(value)
        except (
            ValueError,
            TypeError
        ):
            return default

    # ==========================================
    # ROUND VALUE
    # ==========================================
    @staticmethod
    def round_value(
        value: float,
        digits: int = 2
    ) -> float:
        """
        PURPOSE: Round a float value to a specified number of decimal places.
        PARAMETERS:
            value (float): The number to round.
            digits (int): Number of decimal places (default 2).
        RETURNS: float – The rounded value.
        CONNECTS TO:
            - Services: Used when formatting nutritional values for frontend display.
            - API: When returning aggregated statistics (e.g., BMI, calorie targets).
        EXAMPLE:
            Helpers.round_value(24.5678, 2)  -> 24.57
            Helpers.round_value(24.5678, 1)  -> 24.6
        """
        return round(
            value,
            digits
        )

    # ==========================================
    # PERCENTAGE CALCULATION
    # ==========================================
    @staticmethod
    def calculate_percentage(
        value: float,
        total: float
    ) -> float:
        """
        PURPOSE: Calculate what percentage `value` is of `total`.
        PARAMETERS:
            value (float): The partial amount.
            total (float): The total amount (denominator).
        RETURNS: float – Percentage rounded to 2 decimal places. Returns 0.0 if
                 total <= 0.
        CONNECTS TO:
            - Services: Used in scorecards (e.g., calorie_match_percent,
              protein_match_percent).
            - API: Used in analytics to compute percentages (e.g., regional_match_percent).
        EXAMPLE:
            Helpers.calculate_percentage(45, 100)  -> 45.0
            Helpers.calculate_percentage(0, 100)   -> 0.0
            Helpers.calculate_percentage(10, 0)    -> 0.0
        """
        if total <= 0:
            return 0.0

        return round(
            (value / total) * 100,
            2
        )

    # ==========================================
    # NORMALIZE SCORE
    # ==========================================
    @staticmethod
    def normalize_score(
        value: float,
        min_value: float,
        max_value: float
    ) -> float:
        """
        PURPOSE: Normalize a value from an arbitrary range [min_value, max_value]
                 to a score between 0 and 100.
        PARAMETERS:
            value (float): The input value.
            min_value (float): The minimum possible value in the original range.
            max_value (float): The maximum possible value in the original range.
        RETURNS: float – Normalized score (0-100), clamped to the range.
        CONNECTS TO:
            - RankingService: Potentially used to normalize nutrition scores or
              health scores into a 0-100 scale.
            - ML Predictor: When converting raw model outputs to a 0-100 scale.
        EXAMPLE:
            # Normalize a score from [1, 10] to [0, 100]
            Helpers.normalize_score(5, 1, 10)  -> 44.44
            Helpers.normalize_score(10, 1, 10) -> 100.0
            Helpers.normalize_score(0, 1, 10)  -> 0.0
        """
        if max_value == min_value:
            return 0.0

        normalized = (
            (
                value - min_value
            )
            /
            (
                max_value - min_value
            )
        ) * 100

        return round(
            max(
                0,
                min(100, normalized)
            ),
            2
        )

    # ==========================================
    # UUID GENERATION
    # ==========================================
    @staticmethod
    def generate_uuid() -> str:
        """
        PURPOSE: Generate a random UUID (Universally Unique Identifier) as a string.
        PARAMETERS: None.
        RETURNS: str – A UUID v4 string (e.g., "123e4567-e89b-12d3-a456-426614174000").
        CONNECTS TO:
            - Repositories: Used by UserRepository, MealRepository, FeedbackRepository
              to generate unique IDs for new records.
            - API: When returning newly created resource IDs to the frontend.
        EXAMPLE:
            Helpers.generate_uuid()  -> "550e8400-e29b-41d4-a716-446655440000"
        """
        return str(
            uuid.uuid4()
        )

    # ==========================================
    # CURRENT TIMESTAMP
    # ==========================================
    @staticmethod
    def current_timestamp() -> str:
        """
        PURPOSE: Return the current UTC timestamp in ISO 8601 format.
        PARAMETERS: None.
        RETURNS: str – ISO formatted datetime string (e.g., "2024-01-15T12:34:56.789012").
        CONNECTS TO:
            - Repositories: Used when setting `created_at` and `updated_at` fields
              in MongoDB or JSON documents.
            - API: When returning timestamps for analytics or logging.
        EXAMPLE:
            Helpers.current_timestamp()  -> "2024-03-01T10:20:30.123456"
        """
        return (
            datetime.utcnow()
            .isoformat()
        )

    # ==========================================
    # CURRENT DATE
    # ==========================================
    @staticmethod
    def current_date() -> str:
        """
        PURPOSE: Return the current UTC date as a string in YYYY-MM-DD format.
        PARAMETERS: None.
        RETURNS: str – Date string (e.g., "2024-01-15").
        CONNECTS TO:
            - Services: May be used for logging or date-based filtering.
            - Frontend: Could be used to display the date of meal plan generation.
        EXAMPLE:
            Helpers.current_date()  -> "2024-03-01"
        """
        return (
            datetime.utcnow()
            .strftime(
                "%Y-%m-%d"
            )
        )

    # ==========================================
    # FORMAT CALORIES
    # ==========================================
    @staticmethod
    def format_calories(
        calories: float
    ) -> str:
        """
        PURPOSE: Format a calorie value as a human-readable string with "kcal".
        PARAMETERS:
            calories (float): The calorie amount.
        RETURNS: str – Formatted string (e.g., "250 kcal").
        CONNECTS TO:
            - API: Used to format response data for the React frontend.
            - React: The frontend can directly display this string without
              additional formatting logic.
        EXAMPLE:
            Helpers.format_calories(245.678)  -> "246 kcal"
            Helpers.format_calories(0)        -> "0 kcal"
        """
        return (
            f"{round(calories)} kcal"
        )

    # ==========================================
    # FORMAT GRAMS
    # ==========================================
    @staticmethod
    def format_grams(
        value: float
    ) -> str:
        """
        PURPOSE: Format a weight value in grams as a human-readable string with "g".
        PARAMETERS:
            value (float): The value in grams.
        RETURNS: str – Formatted string (e.g., "30.5 g").
        CONNECTS TO:
            - API: Used to format protein, carbs, fat, and fiber for frontend display.
            - React: Frontend can display this string directly.
        EXAMPLE:
            Helpers.format_grams(30.567)  -> "30.6 g"
            Helpers.format_grams(0)       -> "0.0 g"
        """
        return (
            f"{round(value, 1)} g"
        )

    # ==========================================
    # FORMAT LITERS
    # ==========================================
    @staticmethod
    def format_liters(
        value: float
    ) -> str:
        """
        PURPOSE: Format a volume value in liters as a human-readable string with "L".
        PARAMETERS:
            value (float): The value in liters.
        RETURNS: str – Formatted string (e.g., "2.5 L").
        CONNECTS TO:
            - API: Used to format water intake recommendations for frontend display.
            - React: Frontend can display this string directly.
        EXAMPLE:
            Helpers.format_liters(2.567)  -> "2.6 L"
            Helpers.format_liters(1)      -> "1.0 L"
        """
        return (
            f"{round(value, 1)} L"
        )

    # ==========================================
    # CALCULATE MACRO PERCENTAGES
    # ==========================================
    @staticmethod
    def calculate_macro_percentages(
        protein_g: float,
        carbs_g: float,
        fat_g: float
    ) -> dict:
        """
        PURPOSE: Calculate the percentage distribution of calories from protein,
                 carbs, and fat, based on the gram amounts.
        PARAMETERS:
            protein_g (float): Grams of protein.
            carbs_g (float): Grams of carbohydrates.
            fat_g (float): Grams of fat.
        RETURNS: dict – Contains keys 'protein_percent', 'carb_percent',
                 'fat_percent', each as a float percentage (0-100), rounded to 2 decimals.
                 If total calories = 0, all percentages are 0.
        CONNECTS TO:
            - API: Used to provide macronutrient breakdowns to the frontend.
            - React: The frontend can use these percentages to render pie charts
              or progress bars.
        EXAMPLE:
            Helpers.calculate_macro_percentages(150, 200, 50)
            # Returns: {'protein_percent': 28.05, 'carb_percent': 37.38, 'fat_percent': 34.58}
        """
        protein_calories = (
            protein_g * 4
        )

        carb_calories = (
            carbs_g * 4
        )

        fat_calories = (
            fat_g * 9
        )

        total_calories = (
            protein_calories
            + carb_calories
            + fat_calories
        )

        if total_calories == 0:
            return {
                "protein_percent": 0,
                "carb_percent": 0,
                "fat_percent": 0
            }

        return {
            "protein_percent": round(
                (
                    protein_calories
                    /
                    total_calories
                ) * 100,
                2
            ),
            "carb_percent": round(
                (
                    carb_calories
                    /
                    total_calories
                ) * 100,
                2
            ),
            "fat_percent": round(
                (
                    fat_calories
                    /
                    total_calories
                ) * 100,
                2
            )
        }

    # ==========================================
    # CLAMP VALUE
    # ==========================================
    @staticmethod
    def clamp(
        value: float,
        min_value: float,
        max_value: float
    ) -> float:
        """
        PURPOSE: Constrain a value to lie within the range [min_value, max_value].
        PARAMETERS:
            value (float): The input value.
            min_value (float): The minimum allowed value.
            max_value (float): The maximum allowed value.
        RETURNS: float – The clamped value.
        CONNECTS TO:
            - Services: Used to ensure scores remain within valid bounds (e.g., 0-100).
            - API: When processing user input that should not exceed certain limits.
        EXAMPLE:
            Helpers.clamp(150, 0, 100)  -> 100
            Helpers.clamp(-5, 0, 100)   -> 0
            Helpers.clamp(50, 0, 100)   -> 50
        """
        return max(
            min_value,
            min(
                value,
                max_value
            )
        )

    # ==========================================
    # REMOVE DUPLICATES
    # ==========================================
    @staticmethod
    def remove_duplicates(
        items: list
    ) -> list:
        """
        PURPOSE: Remove duplicate items from a list while preserving order.
        PARAMETERS:
            items (list): The input list (may contain duplicates).
        RETURNS: list – A new list with duplicates removed, order preserved.
        CONNECTS TO:
            - Services: Used when normalizing user-provided lists (e.g., allergies,
              medical conditions) to avoid redundant processing.
            - API: When processing arrays from frontend that might have duplicates.
        EXAMPLE:
            Helpers.remove_duplicates([1, 2, 2, 3, 1])  -> [1, 2, 3]
        """
        return list(
            dict.fromkeys(items)
        )

    # ==========================================
    # IS EMPTY
    # ==========================================
    @staticmethod
    def is_empty(
        value: Optional[Any]
    ) -> bool:
        """
        PURPOSE: Check whether a value is considered "empty" (None, empty string,
                 empty list, or empty dict).
        PARAMETERS:
            value (Optional[Any]): The value to check.
        RETURNS: bool – True if empty, False otherwise.
        CONNECTS TO:
            - Repositories: Used when validating data from MongoDB before
              performing operations.
            - API: When checking if a request field is provided but empty.
        EXAMPLE:
            Helpers.is_empty(None)           -> True
            Helpers.is_empty("")             -> True
            Helpers.is_empty([])             -> True
            Helpers.is_empty({})             -> True
            Helpers.is_empty("Hello")        -> False
            Helpers.is_empty([1,2])          -> False
        """
        return (
            value is None
            or value == ""
            or value == []
            or value == {}
        )

    # ==========================================
    # CREATE DAY LABEL
    # ==========================================
    @staticmethod
    def create_day_label(
        day_number: int
    ) -> str:
        """
        PURPOSE: Create a formatted string label for a day number (e.g., "Day 01").
        PARAMETERS:
            day_number (int): The day number (1-indexed).
        RETURNS: str – Formatted label with zero-padding (e.g., "Day 03").
        CONNECTS TO:
            - API: Used to generate human-readable day labels in the meal plan
              response.
            - React: The frontend can display these labels as section headings
              for each day of the plan.
        EXAMPLE:
            Helpers.create_day_label(1)  -> "Day 01"
            Helpers.create_day_label(10) -> "Day 10"
        """
        return (
            f"Day {day_number:02d}"
        )

    # ==========================================
    # BMI CATEGORY COLOR MAPPING
    # ==========================================
    @staticmethod
    def calculate_bmi_category_color(
        bmi_category: str
    ) -> str:
        """
        PURPOSE: Map a BMI category string to a color name for UI display.
        PARAMETERS:
            bmi_category (str): The BMI category (e.g., "Normal Weight").
        RETURNS: str – A color name (e.g., "green", "red", "gray").
        CONNECTS TO:
            - API: Used to add a color hint to the health summary response.
            - React: The frontend can use this color name to style the BMI
            display (e.g., a colored badge or progress bar).
        EXAMPLE:
            Helpers.calculate_bmi_category_color("Normal Weight") -> "green"
            Helpers.calculate_bmi_category_color("Underweight")   -> "blue"
            Helpers.calculate_bmi_category_color("Obese Class III") -> "dark_red"
            Helpers.calculate_bmi_category_color("Unknown")       -> "gray"
        """
        mapping = {
            "Underweight": "blue",
            "Normal Weight": "green",
            "Overweight": "orange",
            "Obese Class I": "red",
            "Obese Class II": "red",
            "Obese Class III": "dark_red"
        }

        return mapping.get(
            bmi_category,
            "gray"
        )