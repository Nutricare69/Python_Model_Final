# ============================================================================
# FILE: app/services/ranking_service.py
# ROLE: HEURISTIC RANKING & FALLBACK COMPUTE ENGINE
# ============================================================================

from typing import Dict, List
import pandas as pd


class RankingService:
    GOAL_SCORE_COLUMNS = {
        "weight loss": "weight_loss_score",
        "weight gain": "muscle_gain_score",
        "muscle gain": "muscle_gain_score",
        "maintenance": None
    }

    @staticmethod
    def _safe_float(value, default=0.0) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def calculate_region_match(food_row: dict, user_region: str) -> float:
        if not user_region:
            return 50.0
        if str(food_row.get("region", "")).lower() == user_region.lower():
            return 100.0
        return 50.0

    @staticmethod
    def calculate_state_match(food_row: dict, user_state: str) -> float:
        if not user_state:
            return 50.0
        if str(food_row.get("state", "")).lower() == user_state.lower():
            return 100.0
        return 40.0

    @classmethod
    def calculate_goal_match(cls, food_row: dict, goal: str) -> float:
        score_column = cls.GOAL_SCORE_COLUMNS.get(goal.lower(), None)
        if score_column is None:
            return 75.0
        return min(cls._safe_float(food_row.get(score_column, 5)) * 10, 100)

    @staticmethod
    def calculate_health_match(food_row: dict, medical_conditions: List[str]) -> float:
        if not medical_conditions:
            return 100.0

        scores = []
        for condition in medical_conditions:
            condition = condition.lower()
            if condition == "diabetes":
                scores.append(RankingService._safe_float(food_row.get("diabetes_score", 5)) * 10)
            elif condition in ["heart disease", "hypertension"]:
                scores.append(RankingService._safe_float(food_row.get("heart_health_score", 5)) * 10)

        if not scores:
            return 75.0
        return round(sum(scores) / len(scores), 2)

    @staticmethod
    def calculate_nutrition_score(food_row: dict) -> float:
        protein_score = min((RankingService._safe_float(food_row.get("protein", 0)) / 30) * 100, 100)
        fiber_score = min((RankingService._safe_float(food_row.get("fiber_g", 0)) / 15) * 100, 100)
        
        fullness_score = RankingService._safe_float(food_row.get("fullness_score", 50))
        practicality_score = RankingService._safe_float(food_row.get("practicality_score", 50))

        score = (
            protein_score * 0.30 +
            fiber_score * 0.20 +
            fullness_score * 0.25 +
            practicality_score * 0.25
        )
        return round(score, 2)

    @staticmethod
    def calculate_calorie_match(food_row: dict, goal: str) -> float:
        calories = RankingService._safe_float(food_row.get("calories", 0))
        goal = goal.lower()

        if goal == "weight loss":
            if calories <= 350:
                return 100.0
            if calories <= 500:
                return 80.0
            return 50.0

        if goal in ["muscle gain", "weight gain"]:
            if calories >= 400:
                return 100.0
            if calories >= 250:
                return 80.0
            return 50.0

        return 75.0

    @classmethod
    def calculate_food_score(cls, food_row: dict, user_profile: Dict) -> float:
        nutrition_score = cls.calculate_nutrition_score(food_row)
        goal_match_score = cls.calculate_goal_match(food_row, user_profile["goal"])
        health_match_score = cls.calculate_health_match(food_row, user_profile.get("medical_conditions", []))
        state_match_score = cls.calculate_state_match(food_row, user_profile.get("state", ""))
        region_match_score = cls.calculate_region_match(food_row, user_profile.get("region", ""))
        calorie_match_score = cls.calculate_calorie_match(food_row, user_profile["goal"])

        final_score = (
            nutrition_score * 0.25 +
            goal_match_score * 0.20 +
            health_match_score * 0.20 +
            calorie_match_score * 0.10 +
            state_match_score * 0.15 +
            region_match_score * 0.10
        )

        food_name = str(food_row.get("canonical_food_name", "")).lower()
        food_fat = cls._safe_float(food_row.get("fat", 0.0))
        user_goal = str(user_profile.get("goal", "")).lower()

        if user_goal == "weight loss":
            if "biryani" in food_name:
                final_score -= 50.0
            if food_fat > 15.0:
                final_score -= 30.0

        return round(max(final_score, 0.0), 2)

    @classmethod
    def rank_foods(cls, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        if foods_df.empty:
            return foods_df

        ranked_df = foods_df.copy()
        records = ranked_df.to_dict(orient="records")
        scores = [cls.calculate_food_score(row, user_profile) for row in records]
        
        ranked_df["suitability_score"] = scores
        return ranked_df.sort_values(by="suitability_score", ascending=False).reset_index(drop=True)