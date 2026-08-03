# ============================================================================
# FILE: app/repositories/food_repository.py
# ROLE: INTERNAL ML FEATURE BANK (Microservices Architecture)
# ============================================================================

from pathlib import Path
import pandas as pd


class FoodRepository:
    """
    In-memory feature bank for ML scoring. Uses a class-level Singleton 
    cache to prevent reading the CSV file on every request.
    """

    _cached_df: pd.DataFrame = None

    REQUIRED_COLUMNS = [
        "food_id", "canonical_food_name", "state", "region",
        "meal_type", "calories", "protein", "fat", "carbs"
    ]

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        if FoodRepository._cached_df is None:
            self.load_dataset()

    def load_dataset(self) -> None:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Feature matrix file missing: {self.dataset_path}")

        df = pd.read_csv(
            self.dataset_path,
            encoding="utf-8-sig",
            low_memory=False
        )

        obj_cols = df.select_dtypes(include=["object"]).columns
        num_cols = df.select_dtypes(include=["number"]).columns

        df[obj_cols] = df[obj_cols].fillna("")
        df[num_cols] = df[num_cols].fillna(0)

        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Feature matrix validation failed. Missing keys: {missing}")

        FoodRepository._cached_df = df

    def get_all_foods(self) -> pd.DataFrame:
        return FoodRepository._cached_df.copy()

    def filter_by_diet(self, foods_df: pd.DataFrame, diet_type: str) -> pd.DataFrame:
        diet_type = diet_type.strip().lower()

        if diet_type == "veg":
            return foods_df[foods_df["is_veg"] == 1]

        if diet_type == "eggitarian":
            return foods_df[(foods_df["is_veg"] == 1) | (foods_df["contains_egg"] == 1)]

        return foods_df.copy()