# ============================================================================
# FILE: app/services/disease_service.py
# ROLE: MEDICAL SUITABILITY & CONSTRAINT SERVICE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This service is a pure, stateless mathematical filter. It contains no database 
# access layers.
#
# THE DATA CONTRACT:
# 1. Node.js fetches the User Profile from MongoDB (containing medical_conditions).
# 2. Node.js passes that profile and the raw food records to the Python engine.
# 3. This service standardizes the medical strings, maps them to dataset flags,
#    and clips out non-compliant rows (where suitability == 0) from the matrix 
#    before the ML ranking model processes the final candidates.
# ============================================================================

from typing import Dict, List
import pandas as pd


class DiseaseService:
    """
    PURPOSE: Encapsulates medical condition string normalization, validation, 
             and high-speed vectorized dataframe suitability filtering.
    """

    # ==========================================
    # CONDITION → COLUMN MAPPING
    # ==========================================
    # Maps user-submitted pathology strings to the exact binary fields present
    # in the data matrix payload forwarded by Node.js.
    # Matrix Expectations: 0 = Unsuitable/Harmful, 1 = Safe/Suitable.
    CONDITION_COLUMN_MAPPING = {
        "diabetes": "suitable_diabetes",
        "type 2 diabetes": "suitable_diabetes",
        "type 1 diabetes": "suitable_diabetes",

        "hypertension": "suitable_hypertension",
        "high blood pressure": "suitable_hypertension",
        "bp": "suitable_hypertension",

        "heart disease": "suitable_heart_disease",
        "cardiovascular disease": "suitable_heart_disease",
        "heart problem": "suitable_heart_disease",

        "thyroid": "suitable_thyroid",
        "hypothyroidism": "suitable_thyroid",
        "hyperthyroidism": "suitable_thyroid",

        "pcos": "suitable_pcos",
        "pcod": "suitable_pcos",

        "kidney disease": "suitable_kidney_disease",
        "ckd": "suitable_kidney_disease",
        "renal disease": "suitable_kidney_disease",

        "gerd": "suitable_gerd",
        "acid reflux": "suitable_gerd",
        "gastric reflux": "suitable_gerd"
    }

    # ==========================================
    # NORMALIZATION
    # ==========================================
    @classmethod
    def normalize_conditions(cls, conditions: List[str]) -> List[str]:
        """
        Cleans and sanitizes incoming medical condition array strings.
        Ensures variations like "  Diabetes " resolve uniformly to "diabetes".
        """
        if not conditions:
            return []

        normalized = []
        for condition in conditions:
            if condition is None:
                continue

            condition = str(condition).strip().lower()
            if condition:
                normalized.append(condition)

        return list(dict.fromkeys(normalized))

    # ==========================================
    # VALIDATION
    # ==========================================
    @classmethod
    def validate_conditions(cls, conditions: List[str]) -> Dict[str, List[str]]:
        """
        Differentiates supported pathologies from unmapped entries.
        """
        conditions = cls.normalize_conditions(conditions)
        recognized = []
        unrecognized = []

        for condition in conditions:
            if condition in cls.CONDITION_COLUMN_MAPPING:
                recognized.append(condition)
            else:
                unrecognized.append(condition)

        return {
            "recognized": recognized,
            "unrecognized": unrecognized
        }

    # ==========================================
    # GET CONDITION COLUMNS
    # ==========================================
    @classmethod
    def get_condition_columns(cls, conditions: List[str]) -> List[str]:
        """
        Resolves condition strings into the corresponding dataset feature columns.
        """
        conditions = cls.normalize_conditions(conditions)
        columns = []

        for condition in conditions:
            column = cls.CONDITION_COLUMN_MAPPING.get(condition)
            if column:
                columns.append(column)

        return list(dict.fromkeys(columns))

    # ==========================================
    # FILTER FOODS BY MEDICAL CONDITIONS
    # ==========================================
    @classmethod
    def filter_foods(cls, foods_df: pd.DataFrame, conditions: List[str]) -> pd.DataFrame:
        """
        Vectorized row elimination loop. Purges any recipes flagged as unsafe.
        Retains rows where target suitability criteria evaluate strictly to 1.
        """
        if foods_df.empty or not conditions:
            return foods_df

        condition_columns = cls.get_condition_columns(conditions)
        filtered_df = foods_df.copy()

        for column in condition_columns:
            if column not in filtered_df.columns:
                # If an expected feature criteria column is omitted in the payload, bypass it
                continue

            # Force column values to numeric and safely handle null/NaN spaces as unsafe (0)
            filtered_df[column] = pd.to_numeric(filtered_df[column], errors="coerce").fillna(0)

            # High-speed vectorized boolean mask filtering (keep rows where suitability == 1)
            filtered_df = filtered_df[filtered_df[column] == 1]

        return filtered_df

    # ==========================================
    # HEALTH MATCH SCORE FOR A SINGLE FOOD
    # ==========================================
    @classmethod
    def calculate_health_match_score(cls, food_row, conditions: List[str]) -> float:
        """
        Calculates a real-time relative compatibility percentage (0.0 to 100.0) 
        for isolated items against a user profile array block.
        """
        if not conditions:
            return 100.0

        columns = cls.get_condition_columns(conditions)
        if not columns:
            return 100.0

        matched = 0
        for column in columns:
            try:
                if int(food_row.get(column, 0)) == 1:
                    matched += 1
            except (ValueError, TypeError):
                pass

        score = (matched / len(columns)) * 100
        return round(score, 2)

    # ==========================================
    # REMOVED FOOD COUNT
    # ==========================================
    @classmethod
    def get_removed_food_count(cls, original_df: pd.DataFrame, filtered_df: pd.DataFrame) -> int:
        return max(0, len(original_df) - len(filtered_df))

    # ==========================================
    # GENERATE DISEASE REPORT
    # ==========================================
    @classmethod
    def generate_disease_report(cls, original_df: pd.DataFrame, filtered_df: pd.DataFrame, conditions: List[str]) -> dict:
        """
        Compiles pipeline execution telemetry for tracking and diagnostics.
        """
        validation = cls.validate_conditions(conditions)
        removed = cls.get_removed_food_count(original_df, filtered_df)

        return {
            "medical_conditions": cls.normalize_conditions(conditions),
            "recognized_conditions": validation["recognized"],
            "unrecognized_conditions": validation["unrecognized"],
            "condition_columns": cls.get_condition_columns(conditions),
            "original_food_count": len(original_df),
            "remaining_food_count": len(filtered_df),
            "removed_food_count": removed
        }