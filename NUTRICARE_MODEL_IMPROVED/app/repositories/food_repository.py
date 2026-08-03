from pathlib import Path
import pandas as pd


class FoodRepository:
    """
    PURPOSE: In-memory feature matrix provider for ML models.
    USES CLASS-LEVEL SINGLETON CACHING to eliminate disk I/O latency on API hits.
    """

    _cached_df: pd.DataFrame = None  # Class-level memory cache

    REQUIRED_COLUMNS = [
        "food_id", "canonical_food_name", "state", "region",
        "meal_type", "calories", "protein", "fat", "carbs"
    ]

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        
        # Load from disk ONLY if not already cached in memory
        if FoodRepository._cached_df is None:
            self._load_and_cache_dataset()

    def _load_and_cache_dataset(self) -> None:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Feature matrix missing: {self.dataset_path}")

        df = pd.read_csv(
            self.dataset_path,
            encoding="utf-8-sig",
            low_memory=False
        )

        # Clean missing values
        obj_cols = df.select_dtypes(include=["object"]).columns
        num_cols = df.select_dtypes(include=["number"]).columns
        df[obj_cols] = df[obj_cols].fillna("")
        df[num_cols] = df[num_cols].fillna(0)

        # Validate required columns
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Feature matrix validation failed. Missing: {missing}")

        # Save to class memory cache
        FoodRepository._cached_df = df

    def get_all_foods(self) -> pd.DataFrame:
        """Returns a copy of the pre-loaded memory dataframe instantly."""
        return FoodRepository._cached_df.copy()

    def filter_by_diet(self, foods_df: pd.DataFrame, diet_type: str) -> pd.DataFrame:
        diet_type = diet_type.strip().lower()

        if diet_type == "veg":
            return foods_df[foods_df["is_veg"] == 1]

        if diet_type == "eggitarian":
            return foods_df[(foods_df["is_veg"] == 1) | (foods_df["contains_egg"] == 1)]

        return foods_df.copy()