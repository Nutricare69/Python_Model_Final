# ============================================================================
# FILE: app/ml/feature_engineering.py
# ROLE: ML FEATURE ENGINEERING COMPUTE ENGINE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This component acts as a stateless matrix transformer. It does NOT write to
# disk or query collections. It accepts raw memory structures (DataFrames and Dicts)
# originally queried by the Node.js API Gateway from MongoDB, and encodes them
# into dense numerical matrices ready for machine learning model ingestion.
# ============================================================================

from typing import Dict, List
import pandas as pd


class FeatureEngineer:
    """
    PURPOSE:
    Handles serialization and structural vector formatting required for ML operations.
    It maps strings into categorical integer keys, evaluates string alignment matrices 
    (such as geo-location preference matching), and compiles vectors for model scoring.
    
    BACKEND DEVELOPER USAGE:
    Called exclusively inside isolated Python computational loops (e.g., RankingService).
    - For real-time endpoint scoring (Inference), utilize `create_prediction_features()`.
    - For offline dataset extraction (Training), utilize `build_training_dataset()`.
    """

    # ==========================================
    # CATEGORICAL ENCODING MAPPINGS
    # ==========================================
    GOAL_MAPPING = {
        "weight loss": 1,
        "weight gain": 2,
        "maintenance": 3,
        "muscle gain": 4
    }

    ACTIVITY_MAPPING = {
        "sedentary": 1,
        "light": 2,
        "moderate": 3,
        "active": 4,
        "very active": 5
    }

    GENDER_MAPPING = {
        "male": 1,
        "female": 2,
        "other": 3
    }

    # ==========================================
    # HELPER: SAFE FLOAT CONVERSION
    # ==========================================
    @staticmethod
    def safe_float(value, default=0.0) -> float:
        """
        Prevents processing crashes caused by empty fields or structural 
        mismatches during array conversion loops.
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    # ==========================================
    # FEATURE CALCULATIONS
    # ==========================================
    @classmethod
    def calculate_region_match(cls, food_region: str, user_region: str) -> int:
        if not user_region:
            return 0
        return int(str(food_region).lower() == str(user_region).lower())

    @classmethod
    def calculate_state_match(cls, food_state: str, user_state: str) -> int:
        if not user_state:
            return 0
        return int(str(food_state).lower() == str(user_state).lower())

    @classmethod
    def calculate_goal_score(cls, food_row, user_goal: str) -> float:
        goal = str(user_goal).lower()

        if goal == "weight loss":
            return cls.safe_float(food_row.get("weight_loss_score", 5))

        if goal in ["weight gain", "muscle gain"]:
            return cls.safe_float(food_row.get("muscle_gain_score", 5))

        return 5.0

    @classmethod
    def calculate_health_score(cls, food_row, medical_conditions: List[str]) -> float:
        if not medical_conditions:
            return 5.0

        scores = []
        for condition in medical_conditions:
            condition = str(condition).lower()

            if condition == "diabetes":
                scores.append(cls.safe_float(food_row.get("diabetes_score", 5)))
            elif condition in ["heart disease", "hypertension"]:
                scores.append(cls.safe_float(food_row.get("heart_health_score", 5)))

        if not scores:
            return 5.0

        return round(sum(scores) / len(scores), 2)

    # ==========================================
    # CORE FEATURE VECTOR GENERATOR
    # ==========================================
    @classmethod
    def create_feature_vector(cls, food_row, user_profile: Dict) -> Dict:
        """
        PURPOSE: Compiles a unified numerical dictionary for a distinct food/user matrix slice.
        CRITICAL: Field mappings must exactly align with your serialized model input array columns.
        """
        gender = str(user_profile.get("gender", "male")).lower()
        activity = str(user_profile.get("activity_level", "moderate")).lower()
        goal = str(user_profile.get("goal", "maintenance")).lower()

        return {
            # --- USER FEATURES ---
            "user_age": cls.safe_float(user_profile.get("age", 25)),
            "user_weight": cls.safe_float(user_profile.get("weight", 70)),
            "user_height": cls.safe_float(user_profile.get("height", 170)),
            "user_gender": cls.GENDER_MAPPING.get(gender, 1),
            "user_activity": cls.ACTIVITY_MAPPING.get(activity, 3),
            "user_goal": cls.GOAL_MAPPING.get(goal, 3),

            # --- FOOD NUTRITION FEATURES ---
            "calories": cls.safe_float(food_row.get("calories", 0)),
            "protein": cls.safe_float(food_row.get("protein", 0)),
            "fat": cls.safe_float(food_row.get("fat", 0)),
            "carbs": cls.safe_float(food_row.get("carbs", 0)),
            "fiber_g": cls.safe_float(food_row.get("fiber_g", 0)),
            "sodium_mg": cls.safe_float(food_row.get("sodium_mg", 0)),
            "iron_mg": cls.safe_float(food_row.get("iron_mg", 0)),
            "calcium_mg": cls.safe_float(food_row.get("calcium_mg", 0)),
            "potassium_mg": cls.safe_float(food_row.get("potassium_mg", 0)),

            # --- SUBJECTIVE SCORES ---
            "fullness_score": cls.safe_float(food_row.get("fullness_score", 50)),
            "practicality_score": cls.safe_float(food_row.get("practicality_score", 50)),
            "frequency_score": cls.safe_float(food_row.get("frequency_score", 3)),

            # --- CONDITION-SPECIFIC SCORES ---
            "diabetes_score": cls.safe_float(food_row.get("diabetes_score", 5)),
            "heart_health_score": cls.safe_float(food_row.get("heart_health_score", 5)),
            "muscle_gain_score": cls.safe_float(food_row.get("muscle_gain_score", 5)),
            "weight_loss_score": cls.safe_float(food_row.get("weight_loss_score", 5)),

            # --- COMPATIBILITY FEATURES ---
            "state_match": cls.calculate_state_match(
                food_row.get("state", ""), 
                user_profile.get("state", "")
            ),
            "region_match": cls.calculate_region_match(
                food_row.get("region", ""), 
                user_profile.get("region", "")
            ),
            "goal_match_score": cls.calculate_goal_score(food_row, goal),
            "health_match_score": cls.calculate_health_score(
                food_row, 
                user_profile.get("medical_conditions", [])
            ),

            # --- DIETARY BOOLEANS ---
            "is_veg": int(food_row.get("is_veg", 0)),
            "contains_egg": int(food_row.get("contains_egg", 0))
        }

    # ==========================================
    # TRAINING DATASET BUILDER
    # ==========================================
    @classmethod
    def build_training_dataset(cls, foods_df: pd.DataFrame, user_profiles: List[Dict]) -> pd.DataFrame:
        """
        O(N * M) Cross-Join loop matrix builder. Run exclusively offline during training.
        """
        training_rows = []
        for user in user_profiles:
            for _, food_row in foods_df.iterrows():
                training_rows.append(cls.create_feature_vector(food_row, user))
        return pd.DataFrame(training_rows)

    # ==========================================
    # PREDICTION FEATURES BUILDER
    # ==========================================
    @classmethod
    def create_prediction_features(cls, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        """
        Executes structural processing loops for matching a profile frame.
        Called directly by compute routers for model inference.
        """
        rows = []
        for _, food_row in foods_df.iterrows():
            rows.append(cls.create_feature_vector(food_row, user_profile))
        return pd.DataFrame(rows)