# ============================================================================
# FILE: app/services/nutrition_service.py
# ROLE: STATELESS MEAL MACRO SPLITTER SERVICE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This service acts as an isolated mathematical utility. It contains zero
# database drivers or connection loops.
#
# THE DATAFLOW:
# 1. Node.js fetches raw user profile records from MongoDB and forwards them to Python.
# 2. Python computes daily total calories and macros via CalorieService.
# 3. NutritionService receives that daily CalorieResult object and applies a 
#    fractional split matrix (25/35/15/25) to generate specific targets for 
#    Breakfast, Lunch, Snacks, and Dinner.
# ============================================================================

from dataclasses import dataclass
from typing import Dict
from app.services.calorie_service import CalorieResult


# ==========================================
# MEAL NUTRITION TARGET (DATACLASS)
# ==========================================
@dataclass
class MealNutritionTarget:
    """
    PURPOSE: Holds the calculated nutritional targets for an individual meal.
    ROLE: Data Transfer Object (DTO) passed to the MealGenerator to guide food choices.
    """
    meal_name: str
    target_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float

    def to_dict(self) -> dict:
        """
        Converts the meal target properties into a standard serializable dictionary.
        """
        return {
            "meal_name": self.meal_name,
            "target_calories": self.target_calories,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "fiber_g": self.fiber_g
        }


# ==========================================
# DAILY NUTRITION PLAN (DATACLASS)
# ==========================================
@dataclass
class DailyNutritionPlan:
    """
    PURPOSE: Encapsulates the entire daily nutrition target matrix.
    ROLE: Combines overall daily totals with specific per-meal target sub-objects.
    """
    breakfast: MealNutritionTarget
    lunch: MealNutritionTarget
    snacks: MealNutritionTarget
    dinner: MealNutritionTarget
    daily_calories: float
    daily_protein_g: float
    daily_carbs_g: float
    daily_fat_g: float
    daily_fiber_g: float
    daily_water_l: float

    def to_dict(self) -> dict:
        """
        Flattens and serializes the complete day's nutrition matrix into a JSON-ready dict.
        """
        return {
            "daily_calories": self.daily_calories,
            "daily_protein_g": self.daily_protein_g,
            "daily_carbs_g": self.daily_carbs_g,
            "daily_fat_g": self.daily_fat_g,
            "daily_fiber_g": self.daily_fiber_g,
            "daily_water_l": self.daily_water_l,
            "breakfast": self.breakfast.to_dict(),
            "lunch": self.lunch.to_dict(),
            "snacks": self.snacks.to_dict(),
            "dinner": self.dinner.to_dict()
        }


# ==========================================
# NUTRITION SERVICE
# ==========================================
class NutritionService:
    """
    Provides pure, stateless class methods to split macro and calorie distributions.
    """

    # Fractional proportions of daily limits allocated to each macro window.
    # CRITICAL: These ratios must always sum to exactly 1.0 (100%).
    MEAL_DISTRIBUTION = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "snacks": 0.15,
        "dinner": 0.25
    }

    # ==========================================
    # HELPER: CREATE A SINGLE MEAL TARGET
    # ==========================================
    @classmethod
    def _create_meal_target(cls, meal_name: str, ratio: float, calories: float, 
                            protein: float, carbs: float, fat: float, fiber: float) -> MealNutritionTarget:
        """
        Internal utility to execute fractional matrix multiplication across macro targets.
        """
        return MealNutritionTarget(
            meal_name=meal_name,
            target_calories=round(calories * ratio, 1),
            protein_g=round(protein * ratio, 1),
            carbs_g=round(carbs * ratio, 1),
            fat_g=round(fat * ratio, 1),
            fiber_g=round(fiber * ratio, 1)
        )

    # ==========================================
    # MAIN PUBLIC METHOD
    # ==========================================
    @classmethod
    def generate_daily_nutrition_plan(cls, calorie_result: CalorieResult) -> DailyNutritionPlan:
        """
        PURPOSE: Transforms a total daily CalorieResult into a segmented DailyNutritionPlan.
        INPUT EXPECTATION: CalorieResult instance parsed via dot notation attributes.
        """
        breakfast = cls._create_meal_target(
            meal_name="Breakfast", ratio=cls.MEAL_DISTRIBUTION["breakfast"],
            calories=calorie_result.target_calories, protein=calorie_result.protein_target_g,
            carbs=calorie_result.carb_target_g, fat=calorie_result.fat_target_g, fiber=calorie_result.fiber_target_g
        )

        lunch = cls._create_meal_target(
            meal_name="Lunch", ratio=cls.MEAL_DISTRIBUTION["lunch"],
            calories=calorie_result.target_calories, protein=calorie_result.protein_target_g,
            carbs=calorie_result.carb_target_g, fat=calorie_result.fat_target_g, fiber=calorie_result.fiber_target_g
        )

        snacks = cls._create_meal_target(
            meal_name="Snacks", ratio=cls.MEAL_DISTRIBUTION["snacks"],
            calories=calorie_result.target_calories, protein=calorie_result.protein_target_g,
            carbs=calorie_result.carb_target_g, fat=calorie_result.fat_target_g, fiber=calorie_result.fiber_target_g
        )

        dinner = cls._create_meal_target(
            meal_name="Dinner", ratio=cls.MEAL_DISTRIBUTION["dinner"],
            calories=calorie_result.target_calories, protein=calorie_result.protein_target_g,
            carbs=calorie_result.carb_target_g, fat=calorie_result.fat_target_g, fiber=calorie_result.fiber_target_g
        )

        return DailyNutritionPlan(
            breakfast=breakfast,
            lunch=lunch,
            snacks=snacks,
            dinner=dinner,
            daily_calories=calorie_result.target_calories,
            daily_protein_g=calorie_result.protein_target_g,
            daily_carbs_g=calorie_result.carb_target_g,
            daily_fat_g=calorie_result.fat_target_g,
            daily_fiber_g=calorie_result.fiber_target_g,
            daily_water_l=calorie_result.water_target_liters
        )

    # ==========================================
    # HELPER: GET MEAL DISTRIBUTION PERCENTAGES
    # ==========================================
    @classmethod
    def get_meal_distribution(cls) -> Dict[str, float]:
        """
        Converts fractional ratios to integer percentages for frontend UI rendering components.
        """
        return {
            "Breakfast": cls.MEAL_DISTRIBUTION["breakfast"] * 100,
            "Lunch": cls.MEAL_DISTRIBUTION["lunch"] * 100,
            "Snacks": cls.MEAL_DISTRIBUTION["snacks"] * 100,
            "Dinner": cls.MEAL_DISTRIBUTION["dinner"] * 100
        }