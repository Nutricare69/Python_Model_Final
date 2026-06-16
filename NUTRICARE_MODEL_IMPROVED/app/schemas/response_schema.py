# ============================================================================
# FILE: app/schemas/response_schema.py
# ROLE: STANDARDIZED API RESPONSE ENVELOPE contracts (Pydantic v2 Core)
# ============================================================================

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.schemas.food_schema import FoodRecommendationSchema
from app.schemas.meal_plan_schema import MealPlanResponseSchema


class BaseResponseSchema(BaseModel):
    success: bool
    message: str


class ErrorResponseSchema(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None


class SuccessResponseSchema(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class PaginationSchema(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int


class PaginatedResponseSchema(BaseModel):
    success: bool = True
    message: str
    pagination: PaginationSchema
    data: List[Any]


class FoodResponseWrapperSchema(BaseModel):
    success: bool = True
    message: str
    foods: List[Dict]


class RecommendationResponseSchema(BaseModel):
    success: bool = True
    message: str
    total_recommendations: int
    recommendations: List[FoodRecommendationSchema]


class MealPlanWrapperSchema(BaseModel):
    success: bool = True
    message: str
    meal_plan: MealPlanResponseSchema


class FeedbackResponseSchema(BaseModel):
    success: bool = True
    message: str
    feedback_id: Optional[str] = None


class AnalyticsResponseSchema(BaseModel):
    success: bool = True
    message: str
    analytics: Dict


class HealthCheckSchema(BaseModel):
    app_name: str
    version: str
    engine_status: str


class ModelInfoSchema(BaseModel):
    model_name: str
    model_version: str
    training_rows: int
    feature_count: int
    last_trained_at: str