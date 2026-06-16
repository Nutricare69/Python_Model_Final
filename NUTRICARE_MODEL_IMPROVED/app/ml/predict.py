# ============================================================================
# FILE: app/ml/predict.py
# ROLE: ML INFERENCE & SCORING PIPELINE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This component handles stateless machine learning model execution. It reads 
# trained binary models (.pkl) from local disk storage and scores numerical feature 
# matrices generated from the data objects passed into the POST request body 
# by the Node.js API Gateway.
# ============================================================================

from pathlib import Path
from typing import Dict
import joblib
import pandas as pd

# FeatureEngineering converts raw food matrices + user profiles into numerical feature vectors
from app.ml.feature_engineering import FeatureEngineer


class FoodRankerPredictor:
    """
    PURPOSE: Main orchestrator for ML-based food ranking.
    Handles artifact ingestion, feature array normalization via scalers, real-time 
    inference loops, and score bounds restriction.
    """

    # Paths to local model storage blocks inside the container/filesystem
    MODEL_PATH = Path("app/ml/saved_models/food_ranker.pkl")
    SCALER_PATH = Path("app/ml/saved_models/scaler.pkl")

    def __init__(self):
        """
        Initializes the inference wrapper and attempts to load the ML assets.
        If loading crashes or files are missing, it falls back to standard heuristics.
        """
        self.model = None
        self.scaler = None
        self.load_artifacts()

    def load_artifacts(self):
        """
        Ingests the trained serialized machine learning objects from disk.
        Fails safely without dropping the main application runtime thread if assets are absent.
        """
        try:
            if self.MODEL_PATH.exists():
                self.model = joblib.load(self.MODEL_PATH)

            if self.SCALER_PATH.exists():
                self.scaler = joblib.load(self.SCALER_PATH)

        except Exception as e:
            print(f"CRITICAL: Failed to load core machine learning engines: {e}")
            self.model = None
            self.scaler = None

    def is_available(self) -> bool:
        """
        Verifies if both matching model and feature array layers are active.
        """
        return self.model is not None and self.scaler is not None

    def build_prediction_matrix(self, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        """
        Transforms string profiles and raw metrics into numerical matrices.
        Columns must match the training matrix columns exactly or the model will crash.
        """
        return FeatureEngineer.create_prediction_features(foods_df, user_profile)

    def predict_scores(self, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        """
        Applies feature scaling and executes real-time inference on the food matrix.
        Returns a copy of the food frame containing a localized float index 'ml_score'.
        """
        result_df = foods_df.copy()

        # If data matrix slice is empty, abort execution immediately
        if foods_df.empty:
            result_df["ml_score"] = []
            return result_df

        # Fallback to an aligned median score if model layers are missing
        if not self.is_available():
            result_df["ml_score"] = 50.0
            return result_df

        try:
            # Stage 1: Structure raw vectors into a mathematical frame
            feature_df = self.build_prediction_matrix(foods_df, user_profile)

            # Stage 2: Execute scale transformation matrix normalization
            scaled_features = self.scaler.transform(feature_df)

            # Stage 3: Process scaled matrix through model prediction layer
            predicted_scores = self.model.predict(scaled_features)
            result_df["ml_score"] = predicted_scores

            # Stage 4: Enforce valid range containment limits [0.0, 100.0]
            result_df["ml_score"] = result_df["ml_score"].clip(lower=0, upper=100)

        except Exception as e:
            print(f"WARNING: Pipeline compute error. Triggering fallback configuration safety: {e}")
            result_df["ml_score"] = 50.0

        return result_df

    def rank_foods(self, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        """
        Processes real-time prediction and sorts elements descending based on calculated performance weight.
        """
        ranked_df = self.predict_scores(foods_df, user_profile)
        ranked_df = ranked_df.sort_values(by="ml_score", ascending=False)
        return ranked_df.reset_index(drop=True)

    def get_top_foods(self, foods_df: pd.DataFrame, user_profile: Dict, top_n: int = 100) -> pd.DataFrame:
        """
        Slices the peak performance slice out of the sorted matrix block.
        """
        ranked_df = self.rank_foods(foods_df, user_profile)
        return ranked_df.head(top_n)

    def get_food_score(self, food_row, user_profile: Dict) -> float:
        """
        Isolates a single record row item array block for discrete prediction scoring.
        """
        food_df = pd.DataFrame([food_row])
        result_df = self.predict_scores(food_df, user_profile)
        return float(result_df.iloc[0]["ml_score"])