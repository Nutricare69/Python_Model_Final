# ============================================================================
# FILE: app/schemas/user_schema.py
# ROLE: USER PROFILE INPUT VALIDATION SCHEMA (Pydantic v2 Core)
# ============================================================================

from typing import List
from pydantic import BaseModel, Field

class UserProfileSchema(BaseModel):
    """
    PURPOSE: Validates the incoming user profile JSON payload sent from the 
             Node.js gateway or frontend client.
    """
    name: str = Field(..., description="User's full name")
    age: int = Field(..., ge=1, le=120, description="Age in years")
    gender: str = Field(..., description="Gender option string")
    height_cm: float = Field(..., ge=30.0, le=300.0, description="Height in centimeters")
    weight_kg: float = Field(..., ge=10.0, le=500.0, description="Weight in kilograms")
    region: str = Field(..., description="Geographic region name")
    state: str = Field(..., description="Indian state name")
    diet_preference: str = Field(..., description="Options: 'Veg', 'Eggitarian', 'Non-Veg'")
    activity_level: str = Field(..., description="Options: 'Sedentary', 'Light', 'Moderate', 'Active', 'Very Active'")
    goal: str = Field(..., description="Target objective string")
    medical_conditions: List[str] = Field(default_factory=list, description="List of health pathologies")
    allergies: List[str] = Field(default_factory=list, description="List of dietary constraints")
    plan_duration_days: int = Field(default=7, ge=1, le=30, description="Number of days to compute layout for")