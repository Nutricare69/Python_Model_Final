# ============================================================================
# FILE: app/repositories/food_repository.py
# ROLE: INTERNAL ML FEATURE BANK (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This component acts as an in-memory database of food features for the ML model.
# Public frontend features (like search and profile views) are handled by Node.js.
# This file remains backed by a static CSV file because caching the feature matrix
# in RAM allows Python to run real-time recommendation loops with zero network latency.
# ============================================================================

from pathlib import Path
import pandas as pd


class FoodRepository:
    """
    PURPOSE: Ingests, validates, and provisions the core food matrix for machine 
             learning ranking and multi-day meal orchestration.
    """

    # Strict feature requirements needed by FeatureEngineer and RankingService
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

    def __init__(self, dataset_path: str):
        """
        Initializes the repository and loads the food matrix into memory.
        """
        self.dataset_path = Path(dataset_path)
        self.foods_df = pd.DataFrame()
        self.load_dataset()

    def load_dataset(self) -> None:
        """
        Ingests the dataset CSV file into a cached Pandas DataFrame.
        Handles formatting and verifies data integrity boundaries.
        """
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Feature matrix file missing: {self.dataset_path}")

        self.foods_df = pd.read_csv(
            self.dataset_path,
            encoding="utf-8-sig",
            low_memory=False
        )

        self._clean_dataframe()
        self._validate_columns()

    def reload_dataset(self) -> None:
        """
        Reloads the feature matrix. Useful if an admin uploads an updated dataset.
        """
        self.load_dataset()

    def _clean_dataframe(self) -> None:
        """
        Fills missing values (NaN) to prevent machine learning processing loops from crashing.
        """
        object_columns = self.foods_df.select_dtypes(include=["object"]).columns
        numeric_columns = self.foods_df.select_dtypes(include=["number"]).columns

        self.foods_df[object_columns] = self.foods_df[object_columns].fillna("")
        self.foods_df[numeric_columns] = self.foods_df[numeric_columns].fillna(0)

    def _validate_columns(self) -> None:
        """
        Guards structural requirements before passing matrices to the models.
        """
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS if col not in self.foods_df.columns
        ]

        if missing_columns:
            raise ValueError(f"Feature matrix validation failed. Missing keys: {missing_columns}")

    def get_all_foods(self) -> pd.DataFrame:
        """
        Returns a protected memory slice copy of the entire baseline food matrix.
        Used by recommendations.py and meal_generator.py for processing loops.
        """
        return self.foods_df.copy()

    def filter_by_diet(self, foods_df: pd.DataFrame, diet_type: str) -> pd.DataFrame:
        """
        Applies a high-speed vectorized boolean mask to filter a food matrix by diet.
        Supported options: "veg", "eggitarian", "non-veg".
        """
        diet_type = diet_type.strip().lower()

        if diet_type == "veg":
            return foods_df[foods_df["is_veg"] == 1]

        if diet_type == "eggitarian":
            return foods_df[(foods_df["is_veg"] == 1) | (foods_df["contains_egg"] == 1)]

        # For non-veg or any other configuration, pass the dataframe forward as-is
        return foods_df.copy()