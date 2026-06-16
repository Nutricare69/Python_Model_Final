# ============================================================================
# FILE: app/services/allergy_service.py
# ROLE: ALLERGY ELIMINATION & CONSTRAINT SERVICE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This service acts as a stateless, in-memory array modifier. It contains no 
# database footprint. 
#
# THE DATA CONTRACT:
# 1. Node.js sends the full user profile (with an array of allergy strings) 
#    and the food collection rows inside an HTTP POST payload.
# 2. This service standardizes, lowercases, and strips whitespace from those strings.
# 3. It maps terms (e.g., "milk" -> "is_allergen_dairy") and drops matching 
#    rows via vectorized Pandas matrix indexing before ML models score the rest.
# ============================================================================

from typing import Dict, List
import pandas as pd


class AllergyService:
    """
    PURPOSE: Encapsulates allergy normalization, validation, column mapping, 
             and vectorized food matrix elimination.
    """

    # ==========================================
    # ALLERGY → COLUMN MAPPING
    # ==========================================
    # Maps user-provided allergy strings (case-insensitive) to exact binary keys 
    # present within the dataset payload sent from Node.js.
    ALLERGY_COLUMN_MAPPING = {
        "gluten": "is_allergen_gluten",

        "dairy": "is_allergen_dairy",
        "milk": "is_allergen_dairy",
        "lactose": "is_allergen_dairy",

        "nuts": "is_allergen_nuts",
        "peanut": "is_allergen_nuts",
        "peanuts": "is_allergen_nuts",

        "soy": "is_allergen_soy",

        "shellfish": "is_allergen_shellfish",
        "shrimp": "is_allergen_shellfish",
        "prawn": "is_allergen_shellfish",

        "egg": "is_allergen_eggs",
        "eggs": "is_allergen_eggs",

        "fish": "is_allergen_fish"
    }

    # ==========================================
    # ALLERGY NORMALIZATION
    # ==========================================
    @classmethod
    def normalize_allergies(cls, allergies: List[str]) -> List[str]:
        """
        Cleans, standardizes, and deduplicates raw string inputs from the payload.
        Ensures that variations like "  PeanutS  " resolve uniformly to "peanuts".
        """
        if not allergies:
            return []

        normalized = []
        for allergy in allergies:
            if allergy is None:
                continue

            allergy = str(allergy).strip().lower()
            if allergy:
                normalized.append(allergy)

        # dictionary keys extraction guarantees order preservation while deduplicating
        return list(dict.fromkeys(normalized))

    # ==========================================
    # ALLERGEN COLUMN LOOKUP
    # ==========================================
    @classmethod
    def get_allergen_columns(cls, allergies: List[str]) -> List[str]:
        """
        Converts human allergy strings into the corresponding dataset binary feature columns.
        """
        allergies = cls.normalize_allergies(allergies)
        columns = []

        for allergy in allergies:
            column = cls.ALLERGY_COLUMN_MAPPING.get(allergy)
            if column:
                columns.append(column)

        return list(dict.fromkeys(columns))

    # ==========================================
    # ALLERGY VALIDATION
    # ==========================================
    @classmethod
    def validate_allergies(cls, allergies: List[str]) -> Dict[str, List[str]]:
        """
        Separates recognizable allergies from unsupported ones. Node.js can use 
        unrecognized logs to trigger developer alerts for schema expansions.
        """
        allergies = cls.normalize_allergies(allergies)
        recognized = []
        unrecognized = []

        for allergy in allergies:
            if allergy in cls.ALLERGY_COLUMN_MAPPING:
                recognized.append(allergy)
            else:
                unrecognized.append(allergy)

        return {
            "recognized": recognized,
            "unrecognized": unrecognized
        }

    # ==========================================
    # FILTER FOODS BY ALLERGIES
    # ==========================================
    @classmethod
    def filter_foods(cls, foods_df: pd.DataFrame, allergies: List[str]) -> pd.DataFrame:
        """
        Purges rows containing active allergen variables.
        Expects integer indicators: 0 = safe, 1 = item contains allergen.
        """
        if foods_df.empty or not allergies:
            return foods_df

        allergen_columns = cls.get_allergen_columns(allergies)
        filtered_df = foods_df.copy()

        for column in allergen_columns:
            if column not in filtered_df.columns:
                # If a feature column is not provided in the matrix payload, skip processing
                continue

            # Coerce malformed data to float/int and default any null spaces to safe (0)
            filtered_df[column] = pd.to_numeric(filtered_df[column], errors="coerce").fillna(0)

            # High-speed vectorized boolean mask filtering (keep rows where allergen == 0)
            filtered_df = filtered_df[filtered_df[column] == 0]

        return filtered_df

    # ==========================================
    # REMOVED FOOD COUNT
    # ==========================================
    @classmethod
    def get_removed_food_count(cls, original_df: pd.DataFrame, filtered_df: pd.DataFrame) -> int:
        return max(0, len(original_df) - len(filtered_df))

    # ==========================================
    # DETECTED ALLERGENS
    # ==========================================
    @classmethod
    def get_detected_allergens(cls, allergies: List[str]) -> List[str]:
        return cls.get_allergen_columns(allergies)

    # ==========================================
    # GENERATE ALLERGY REPORT
    # ==========================================
    @classmethod
    def generate_allergy_report(cls, original_df: pd.DataFrame, filtered_df: pd.DataFrame, allergies: List[str]) -> dict:
        """
        Compiles execution metrics. Node.js can log this output or forward it 
        to analytics tools to gauge filtering efficiency.
        """
        validation = cls.validate_allergies(allergies)
        removed = cls.get_removed_food_count(original_df, filtered_df)

        return {
            "allergies": cls.normalize_allergies(allergies),
            "recognized_allergies": validation["recognized"],
            "unrecognized_allergies": validation["unrecognized"],
            "allergen_columns": cls.get_detected_allergens(allergies),
            "original_food_count": len(original_df),
            "remaining_food_count": len(filtered_df),
            "removed_food_count": removed
        }