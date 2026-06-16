# ============================================================================
# FILE: app/ml/train_model.py
# ROLE: ML MODEL TRAINING PIPELINE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This component acts as an isolated mathematical orchestration pipeline. 
# It does NOT interface with MongoDB. Instead, it accepts raw records forwarded 
# by the Node.js backend over an administrative endpoint, cleanses the data frame 
# in memory, compiles the feature space, and overwrites the core binary objects.
# ============================================================================

from pathlib import Path
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# In-memory scrubbing filter dependency
from app.ml.preprocessing import DataPreprocessor


class FoodRankerTrainer:
    """
    Orchestrates training loops, performance tracking, and filesystem serialization
    for the specialized RandomForest ranking engine.
    """

    # Local binary persistence bounds
    MODEL_DIR = Path("app/ml/saved_models")
    MODEL_PATH = MODEL_DIR / "food_ranker.pkl"
    SCALER_PATH = MODEL_DIR / "scaler.pkl"
    FEATURES_PATH = MODEL_DIR / "feature_columns.pkl"

    RANDOM_STATE = 42

    # ==========================================
    # HELPER: SAFE COLUMN ACCESS
    # ==========================================
    @staticmethod
    def safe_column(df: pd.DataFrame, column: str, default=0) -> pd.Series:
        if column not in df.columns:
            return pd.Series([default] * len(df), index=df.index)
        return df[column]

    # ==========================================
    # TARGET LABEL GENERATION
    # ==========================================
    @classmethod
    def create_training_label(cls, df: pd.DataFrame) -> pd.Series:
        """
        Calculates the baseline composite target vector matrix profile [0.0, 100.0]
        based on weighted physiological utility metrics.
        """
        label = (
            cls.safe_column(df, "weight_loss_score", 5) * 15 +
            cls.safe_column(df, "muscle_gain_score", 5) * 15 +
            cls.safe_column(df, "diabetes_score", 5) * 15 +
            cls.safe_column(df, "heart_health_score", 5) * 15 +
            cls.safe_column(df, "fullness_score", 50) * 0.20 +
            cls.safe_column(df, "practicality_score", 50) * 0.10 +
            cls.safe_column(df, "frequency_score", 3) * 5
        )
        return label.clip(lower=0, upper=100)

    # ==========================================
    # FEATURE MATRIX CONSTRUCTION (FIXED)
    # ==========================================
    @classmethod
    def build_feature_matrix(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        CRITICAL FIX: Removed pre-calculated score columns to prevent data leakage.
        The model must learn strictly from the raw nutritional data and dietary flags.
        """
        candidate_features = [
            "calories", 
            "protein", 
            "fat", 
            "carbs", 
            "fiber_g", 
            "sodium_mg",
            "iron_mg", 
            "calcium_mg", 
            "potassium_mg", 
            "is_veg", 
            "contains_egg", 
            "suitable_diabetes", 
            "suitable_hypertension",
            "suitable_heart_disease", 
            "suitable_thyroid", 
            "suitable_pcos",
            "suitable_kidney_disease", 
            "suitable_gerd"
        ]
        available_features = [col for col in candidate_features if col in df.columns]
        return df[available_features].copy()

    # ==========================================
    # MAIN TRAINING PIPELINE
    # ==========================================
    @classmethod
    def train(cls, raw_data_frame: pd.DataFrame) -> dict:
        """
        Executes structural preprocessing, optimization splits, matrix normalization,
        and saves the finalized model binary configuration vectors back to local disk.
        """
        print("\nIngesting in-memory data matrix...")
        
        # Step 1: Scrub the dataframe layer using the preprocessing filter
        df = DataPreprocessor.preprocess_dataset(raw_data_frame)
        print(f"Operational data rows after cleaning: {len(df)}")

        if len(df) < 10:
            raise ValueError("Insufficient data pool remaining after validation filtering to safely execute training splits.")

        # Step 2: Build matrices
        X = cls.build_feature_matrix(df)
        y = cls.create_training_label(df)

        # Step 3: Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=cls.RANDOM_STATE
        )

        # Step 4: Scale transformation matrix calibration
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Step 5: Initialize the Regressor Core
        model = RandomForestRegressor(
            n_estimators=500,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=cls.RANDOM_STATE,
            n_jobs=-1
        )

        print("Executing architectural training loops...")
        model.fit(X_train_scaled, y_train)

        # Step 6: Vector validation diagnostics
        predictions = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        print(f"Metrics Captured -> MAE: {mae:.4f} | R2: {r2:.4f}")

        # Step 7: Persistence write execution
        cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, cls.MODEL_PATH)
        joblib.dump(scaler, cls.SCALER_PATH)
        joblib.dump(list(X.columns), cls.FEATURES_PATH)

        print("Model configuration blocks successfully updated on filesystem.")
        
        return {
            "rows_processed": len(df),
            "mean_absolute_error": round(float(mae), 4),
            "r2_score": round(float(r2), 4)
        }

    # ==========================================
    # PUBLIC RUN METHOD
    # ==========================================
    @classmethod
    def run(cls, df: pd.DataFrame) -> dict:
        return cls.train(df)


# ==========================================
# LOCALIZED STANDALONE SCRIPT FALLBACK
# ==========================================
if __name__ == "__main__":
    # Provides fallback CLI execution capabilities for local developers using disk CSV data
    fallback_path = Path("datasets/Cleaned_Indian_Food_Dataset_Enriched_UTF8.csv")
    if fallback_path.exists():
        raw_df = pd.read_csv(fallback_path)
        FoodRankerTrainer.run(raw_df)
    else:
        print("Localized testing array csv path not found. Standalone train execution aborted.")