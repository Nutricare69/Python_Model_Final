# ============================================================================
# FILE: app/ml/preprocessing.py
# ROLE: DATA CLEANING & NORMALIZATION ENGINE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This component acts as a stateless data scrubbing filter. It contains no 
# direct database connections. 
#
# THE DATASET PIPELINE:
# 1. Admin uploads a raw CSV file via the React Frontend dashboard.
# 2. Node.js captures the file stream and transmits the records over to Python.
# 3. Python converts the records into a DataFrame, runs DataPreprocessor to 
#    standardize types/fill nulls, and sends the clean array back to Node.js.
# 4. Node.js performs a bulk write (`insertMany`) to update MongoDB.
# ============================================================================

from typing import List
import pandas as pd


class DataPreprocessor:
    """
    PURPOSE:
    A collection of static methods to clean, parse, and normalize dataframes.
    Transforms raw input (handling structural errors, bad types, and missing fields)
    into a mathematically predictable, ML-ready input matrix.
    """

    # Columns required to be present for feature engineering models to parse safely
    REQUIRED_COLUMNS = [
        "food_id",
        "canonical_food_name",
        "state",
        "region",
        "meal_type",
        "calories",
        "protein",
        "fat",
        "carbs"
    ]

    # Target features cleaned as strict binary elements (clipped between 0 and 1)
    BOOLEAN_COLUMNS = [
        "is_veg",
        "contains_egg",
        "is_allergen_gluten",
        "is_allergen_dairy",
        "is_allergen_nuts",
        "is_allergen_soy",
        "is_allergen_shellfish",
        "is_allergen_eggs",
        "is_allergen_fish",
        "suitable_diabetes",
        "suitable_hypertension",
        "suitable_heart_disease",
        "suitable_thyroid",
        "suitable_pcos",
        "suitable_kidney_disease",
        "suitable_gerd"
    ]

    # Continuous variables normalized to float types with median imputation bounds
    NUMERIC_COLUMNS = [
        "calories",
        "protein",
        "fat",
        "carbs",
        "fiber_g",
        "sodium_mg",
        "iron_mg",
        "calcium_mg",
        "potassium_mg",
        "fullness_score",
        "practicality_score",
        "frequency_score",
        "diabetes_score",
        "heart_health_score",
        "muscle_gain_score",
        "weight_loss_score",
        "region_confidence"
    ]

    # Descriptive text targets formatted using case-insulated string strips
    TEXT_COLUMNS = [
        "canonical_food_name",
        "local_name",
        "english_name",
        "state",
        "region",
        "cuisine_type",
        "meal_type",
        "food_category",
        "meal_role",
        "food_group",
        "staple_type"
    ]

    # ==========================================
    # VALIDATION
    # ==========================================
    @classmethod
    def validate_columns(cls, df: pd.DataFrame):
        """
        Hard boundary checker. Throws an exception back to Node.js if incoming 
        data models are missing fundamental features.
        """
        missing = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Structural validation failed. Missing required keys: {missing}")

    # ==========================================
    # COLUMN CLEANING
    # ==========================================
    @classmethod
    def clean_column_names(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [str(col).strip() for col in df.columns]
        return df

    # ==========================================
    # DUPLICATE REMOVAL
    # ==========================================
    @classmethod
    def remove_duplicate_foods(cls, df: pd.DataFrame) -> pd.DataFrame:
        if "food_id" not in df.columns:
            return df
        return df.drop_duplicates(subset=["food_id"]).reset_index(drop=True)

    # ==========================================
    # NUMERIC NORMALIZATION
    # ==========================================
    @classmethod
    def normalize_numeric_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Coerces strings or empty cells to NaN numbers, then applies median 
        imputation to maintain mathematical integrity across array items.
        """
        df = df.copy()
        for column in cls.NUMERIC_COLUMNS:
            if column not in df.columns:
                continue

            df[column] = pd.to_numeric(df[column], errors="coerce")
            median = df[column].median()
            if pd.isna(median):
                median = 0.0

            df[column] = df[column].fillna(median)
        return df

    # ==========================================
    # BOOLEAN NORMALIZATION
    # ==========================================
    @classmethod
    def normalize_boolean_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for column in cls.BOOLEAN_COLUMNS:
            if column not in df.columns:
                continue

            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)
            df[column] = df[column].clip(lower=0, upper=1)
        return df

    # ==========================================
    # TEXT CLEANING
    # ==========================================
    @classmethod
    def clean_text_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for column in cls.TEXT_COLUMNS:
            if column not in df.columns:
                continue
            df[column] = df[column].fillna("").astype(str).str.strip()
        return df

    # ==========================================
    # INVALID ROW REMOVAL
    # ==========================================
    @classmethod
    def remove_invalid_rows(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drops physically impossible rows (negative values or items with zero calories).
        """
        df = df.copy()
        numeric_checks = ["calories", "protein", "fat", "carbs"]

        for column in numeric_checks:
            if column in df.columns:
                df = df[df[column] >= 0]

        if "calories" in df.columns:
            df = df[df["calories"] > 0]

        return df.reset_index(drop=True)

    # ==========================================
    # FULL PREPROCESSING PIPELINE
    # ==========================================
    @classmethod
    def preprocess_dataset(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes sequential cleansing operations. Call this directly from ingestion 
        routers before passing frames to training loops or storage.
        """
        df = cls.clean_column_names(df)
        cls.validate_columns(df)
        df = cls.remove_duplicate_foods(df)
        df = cls.normalize_numeric_columns(df)
        df = cls.normalize_boolean_columns(df)
        df = cls.clean_text_columns(df)
        df = cls.remove_invalid_rows(df)
        return df

    # ==========================================
    # DIRECT CSV LOAD + PREPROCESS
    # ==========================================
    @classmethod
    def load_and_preprocess(cls, csv_path: str) -> pd.DataFrame:
        """
        Utility endpoint for handling localized file testing environments.
        """
        df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
        return cls.preprocess_dataset(df)