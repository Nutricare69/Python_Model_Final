# ============================================================================
# FILE: app/utils/validators.py
# ROLE: CENTRALIZED VALIDATION LOGIC (Case-Insensitive & Service-Aligned)
# ============================================================================

from typing import List
from app.utils.constants import (
    MAX_PLAN_DAYS,
    MIN_PLAN_DAYS,
    SUPPORTED_DIET_TYPES,
    SUPPORTED_GOALS
)

# Import the services directly to validate against their master dictionary mappings
from app.services.disease_service import DiseaseService
from app.services.allergy_service import AllergyService


class ValidationError(Exception):
    """Custom exception class for validation failures."""
    pass


class Validators:
    """A collection of static methods for validating user profile fields."""

    @staticmethod
    def validate_name(name: str) -> None:
        if not isinstance(name, str):
            raise ValidationError("Name must be a string.")
        if not name.strip():
            raise ValidationError("Name cannot be empty.")

    @staticmethod
    def validate_age(age: int) -> None:
        if not isinstance(age, int):
            raise ValidationError("Age must be an integer.")
        if age < 5 or age > 120:
            raise ValidationError("Age must be between 5 and 120.")

    @staticmethod
    def validate_weight(weight_kg: float) -> None:
        if weight_kg <= 0:
            raise ValidationError("Weight must be greater than zero.")
        if weight_kg > 500:
            raise ValidationError("Weight appears invalid.")

    @staticmethod
    def validate_height(height_cm: float) -> None:
        if height_cm <= 0:
            raise ValidationError("Height must be greater than zero.")
        if height_cm > 300:
            raise ValidationError("Height appears invalid.")

    @staticmethod
    def validate_gender(gender: str) -> None:
        valid_genders = {"male", "female", "other"}
        if gender.strip().lower() not in valid_genders:
            raise ValidationError("Invalid gender.")

    @staticmethod
    def validate_diet_type(diet_type: str) -> None:
        if diet_type not in SUPPORTED_DIET_TYPES:
            raise ValidationError(f"Supported diet types: {SUPPORTED_DIET_TYPES}")

    @staticmethod
    def validate_goal(goal: str) -> None:
        if goal not in SUPPORTED_GOALS:
            raise ValidationError(f"Supported goals: {SUPPORTED_GOALS}")

    @staticmethod
    def validate_plan_days(days: int) -> None:
        if days < MIN_PLAN_DAYS or days > MAX_PLAN_DAYS:
            raise ValidationError(f"Plan days must be between {MIN_PLAN_DAYS} and {MAX_PLAN_DAYS}.")

    @staticmethod
    def validate_activity_level(activity_level: str) -> None:
        valid_levels = {"Sedentary", "Light", "Moderate", "Active", "Very Active"}
        if activity_level not in valid_levels:
            raise ValidationError(f"Supported activity levels: {valid_levels}")

    # ==========================================
    # FIXED: CASE-INSENSITIVE MEDICAL VALIDATION
    # ==========================================
    @staticmethod
    def validate_medical_conditions(conditions: List[str]) -> None:
        """Validates conditions against the master DiseaseService mapping keys."""
        for condition in conditions:
            normalized = condition.strip().lower()
            if normalized not in DiseaseService.CONDITION_COLUMN_MAPPING:
                raise ValidationError(f"Unsupported medical condition: {condition}")

    # ==========================================
    # FIXED: CASE-INSENSITIVE ALLERGY VALIDATION
    # ==========================================
    @staticmethod
    def validate_allergies(allergies: List[str]) -> None:
        """Validates allergies against the master AllergyService mapping keys."""
        for allergy in allergies:
            normalized = allergy.strip().lower()
            if normalized not in AllergyService.ALLERGY_COLUMN_MAPPING:
                raise ValidationError(f"Unsupported allergy: {allergy}")

    @classmethod
    def validate_user_profile(cls, profile: dict) -> bool:
        """Orchestrates the validation of a complete user profile dictionary."""
        cls.validate_name(profile["name"])
        cls.validate_age(profile["age"])
        cls.validate_gender(profile["gender"])
        cls.validate_weight(profile["weight"])
        cls.validate_height(profile["height"])
        cls.validate_diet_type(profile["diet_type"])
        cls.validate_goal(profile["goal"])
        cls.validate_activity_level(profile["activity_level"])
        cls.validate_plan_days(profile["days"])
        cls.validate_medical_conditions(profile.get("medical_conditions", []))
        cls.validate_allergies(profile.get("allergies", []))
        return True