# ============================================================================
# FILE: app/services/calorie_service.py
# ROLE: STATELESS METABOLIC COMPUTE ENGINE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This service acts as a localized pure mathematical utility. It contains zero
# database drivers or connection loops.
#
# THE DATAFLOW:
# 1. Node.js sends user profile parameters (gender, age, goal, metrics) to Python.
# 2. Python passes these parameters into CalorieService along with the calculated BMIResult.
# 3. This service executes standard metabolic equations (Mifflin-St Jeor) and
#    macro allocation splits, returning a structured CalorieResult DTO to the router.
# ============================================================================

from dataclasses import dataclass
from app.services.bmi_service import BMIResult


# ==========================================
# CalorieResult Dataclass (DTO)
# ==========================================
@dataclass
class CalorieResult:
    """
    PURPOSE: Data Transfer Object (DTO) encapsulating all computed metabolic targets.
    ROLE: Protects systemic boundaries by providing an explicit, unmutated return contract.
    """
    bmr: float
    tdee: float
    target_calories: float
    protein_target_g: float
    fat_target_g: float
    carb_target_g: float
    fiber_target_g: float
    water_target_liters: float
    sleep_target_hours: str

    def to_dict(self) -> dict:
        """
        Serializes data attributes directly into standard dictionary objects.
        """
        return {
            "bmr": self.bmr,
            "tdee": self.tdee,
            "target_calories": self.target_calories,
            "protein_target_g": self.protein_target_g,
            "fat_target_g": self.fat_target_g,
            "carb_target_g": self.carb_target_g,
            "fiber_target_g": self.fiber_target_g,
            "water_target_liters": self.water_target_liters,
            "sleep_target_hours": self.sleep_target_hours
        }


# ==========================================
# CalorieService – Core Calorie & Macro Calculations
# ==========================================
class CalorieService:
    """
    Provides isolated metabolic processing routines using verified clinical equations.
    """

    # Activity coefficient multipliers mapped to incoming payload option strings
    ACTIVITY_MULTIPLIERS = {
        "Sedentary": 1.20,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725,
        "Very Active": 1.90
    }

    # ==========================================
    # Basal Metabolic Rate (BMR) Calculation
    # ==========================================
    @staticmethod
    def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
        """
        Calculates Basal Metabolic Rate via the Mifflin-St Jeor equation.
        """
        gender = gender.strip().lower()

        if gender == "male":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        elif gender == "female":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        else:
            # Context-insulated neutral calculation bounds for alternative classifications
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)

        return round(bmr, 2)

    # ==========================================
    # Total Daily Energy Expenditure (TDEE)
    # ==========================================
    @classmethod
    def calculate_tdee(cls, bmr: float, activity_level: str) -> float:
        """
        Multiplies the static basal rate against kinetic physical activity coefficients.
        """
        multiplier = cls.ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        return round(bmr * multiplier, 2)

    # ==========================================
    # Target Calories (with Goal & BMI Adjustments)
    # ==========================================
    @staticmethod
    def calculate_target_calories(tdee: float, goal: str, gender: str, bmi_result: BMIResult) -> float:
        """
        Adjusts maintenance thresholds against goal deficits/surpluses, safely enforces
        metabolic floor constraints, and applies high-BMI compensation metrics.
        """
        goal = goal.strip().lower()
        target = tdee

        if goal == "weight loss":
            target = tdee - 500
        elif goal == "weight gain":
            target = tdee + 500
        elif goal == "muscle gain":
            target = tdee + 300

        # High-comorbidity safeguard adjustment for individuals with Obese classifications
        if bmi_result.bmi >= 30:
            target -= 200

        gender = gender.lower()

        # Enforce critical calorie floor constraints to protect user physical health
        if gender == "male":
            target = max(target, 1500)
        elif gender == "female":
            target = max(target, 1200)

        return round(target, 2)

    # ==========================================
    # Protein Target (based on weight and goal)
    # ==========================================
    @staticmethod
    def calculate_protein_target(weight_kg: float, goal: str) -> float:
        goal = goal.strip().lower()

        if goal == "muscle gain":
            return round(weight_kg * 2.2, 1)
        if goal == "weight loss":
            return round(weight_kg * 1.8, 1)

        return round(weight_kg * 1.5, 1)

    # ==========================================
    # Fat Target (as 25% of target calories)
    # ==========================================
    @staticmethod
    def calculate_fat_target(target_calories: float) -> float:
        fat_calories = target_calories * 0.25
        return round(fat_calories / 9, 1)

    # ==========================================
    # Carbohydrate Target (remaining calories)
    # ==========================================
    @staticmethod
    def calculate_carb_target(target_calories: float, protein_g: float, fat_g: float) -> float:
        protein_calories = protein_g * 4
        fat_calories = fat_g * 9
        remaining_calories = target_calories - protein_calories - fat_calories
        
        return round(remaining_calories / 4, 1)

    # ==========================================
    # Water Target (35 ml per kg of body weight)
    # ==========================================
    @staticmethod
    def calculate_water_target(weight_kg: float) -> float:
        water_ml = weight_kg * 35
        return round(water_ml / 1000, 1)

    # ==========================================
    # Fiber Target (14g per 1000 calories)
    # ==========================================
    @staticmethod
    def calculate_fiber_target(target_calories: float) -> float:
        fiber = (target_calories / 1000) * 14
        return round(fiber, 1)

    # ==========================================
    # Sleep Target (Standard recommendation)
    # ==========================================
    @staticmethod
    def calculate_sleep_target() -> str:
        return "7-9 Hours"

    # ==========================================
    # Complete Calorie Report Generator
    # ==========================================
    @classmethod
    def generate_calorie_report(
        cls,
        gender: str,
        weight_kg: float,
        height_cm: float,
        age: int,
        activity_level: str,
        goal: str,
        bmi_result: BMIResult
    ) -> CalorieResult:
        """
        Orchestration pipeline execution sequence. Compiles discrete mathematical
        components into a single unified data payload wrapper.
        """
        bmr = cls.calculate_bmr(gender, weight_kg, height_cm, age)
        tdee = cls.calculate_tdee(bmr, activity_level)
        target_calories = cls.calculate_target_calories(tdee, goal, gender, bmi_result)
        
        protein_target = cls.calculate_protein_target(weight_kg, goal)
        fat_target = cls.calculate_fat_target(target_calories)
        carb_target = cls.calculate_carb_target(target_calories, protein_target, fat_target)
        
        fiber_target = cls.calculate_fiber_target(target_calories)
        water_target = cls.calculate_water_target(weight_kg)
        sleep_target = cls.calculate_sleep_target()

        return CalorieResult(
            bmr=bmr,
            tdee=tdee,
            target_calories=target_calories,
            protein_target_g=protein_target,
            fat_target_g=fat_target,
            carb_target_g=carb_target,
            fiber_target_g=fiber_target,
            water_target_liters=water_target,
            sleep_target_hours=sleep_target
        )