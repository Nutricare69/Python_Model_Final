# ============================================================================
# FILE: app/services/diversity_service.py
# ROLE: DIETARY VARIETY & DIVERSITY ENGINE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This service is an entirely stateless matrix modifier. It contains no database 
# access layers.
#
# THE DATA CONTRACT:
# 1. Node.js fetches the past day plans for a user from MongoDB.
# 2. Node.js packages those historical plans as an array of JSON objects 
#    and forwards them to Python alongside the candidate food pool.
# 3. This service extracts historical keys, calculates overlap penalties, 
#    and sorts the output pool descending based on a dynamic diversity score:
#    diversity_score = suitability_score - diversity_penalty
# ============================================================================

from collections import defaultdict
from typing import Dict, List, Set
import pandas as pd


class DiversityService:
    """
    PURPOSE: Encapsulates processing logic for enforcing menu diversity.
    KEY FEATURES:
        - Extracts recently consumed food IDs to prevent short-term repetition.
        - Audits category usage trends (cuisine, state, food group, staple).
        - Computes rolling score deduplication penalties to ensure varied menus.
    """

    # ==========================================
    # CONFIGURATION CONSTANTS
    # ==========================================
    # Rolling lookback window threshold for food repetition checks
    FOOD_GAP_DAYS = 3

    # Structural deduction modifiers applied per category repetition instance
    STATE_PENALTY = 2.0
    CUISINE_PENALTY = 1.5
    FOOD_GROUP_PENALTY = 1.0
    STAPLE_PENALTY = 1.0

    # ==========================================
    # 1. EXTRACT RECENT FOOD IDs
    # ==========================================
    @staticmethod
    def get_recent_foods(previous_days: List[dict], current_day: int, gap_days: int = FOOD_GAP_DAYS) -> Set[str]:
        """
        PURPOSE: Compiles a historical set of unique food IDs used within the gap window.
        INPUT EXPECTATION: Historical meal arrays passed over HTTP from the Node.js Gateway.
        """
        recent_foods = set()
        start_day = max(1, current_day - gap_days)

        for day_plan in previous_days:
            day_number = day_plan.get("day_number", 0)

            # Only analyze days that fall completely within our rolling gap window
            if start_day <= day_number < current_day:
                for meal_name in ["breakfast", "lunch", "snacks", "dinner"]:
                    foods = day_plan.get(meal_name, {}).get("foods", [])
                    
                    for food in foods:
                        food_id = food.get("food_id")
                        if food_id:
                            recent_foods.add(str(food_id))

        return recent_foods

    # ==========================================
    # 2. REMOVE RECENT FOODS FROM CANDIDATES
    # ==========================================
    @staticmethod
    def remove_recent_foods(candidate_foods: pd.DataFrame, recent_food_ids: Set[str]) -> pd.DataFrame:
        """
        PURPOSE: Drops rows from the candidate matrix containing recently consumed food IDs.
        SAFEGUARD: Fallback system returns original pool if filtering completely depletes options.
        """
        if candidate_foods.empty or not recent_food_ids:
            return candidate_foods

        # High-speed vectorized inverse string-match evaluation mask
        filtered = candidate_foods[
            ~candidate_foods["food_id"].astype(str).isin(recent_food_ids)
        ]

        if filtered.empty:
            return candidate_foods

        return filtered

    # ==========================================
    # 3. TRACK USAGE FREQUENCY OF A CATEGORY
    # ==========================================
    @staticmethod
    def track_usage(previous_days: List[dict], field_name: str) -> Dict[str, int]:
        """
        PURPOSE: Generates historical repetition counters for category grouping buckets.
        """
        counter = defaultdict(int)

        for day_plan in previous_days:
            for meal_name in ["breakfast", "lunch", "snacks", "dinner"]:
                foods = day_plan.get(meal_name, {}).get("foods", [])
                
                for food in foods:
                    value = food.get(field_name)
                    if value:
                        counter[str(value)] = counter[str(value)] + 1

        return dict(counter)

    # ==========================================
    # 4. APPLY DIVERSITY PENALTIES
    # ==========================================
    @classmethod
    def add_diversity_penalty(
        cls,
        candidate_foods: pd.DataFrame,
        state_usage: Dict,
        cuisine_usage: Dict,
        food_group_usage: Dict,
        staple_usage: Dict
    ) -> pd.DataFrame:
        """
        PURPOSE: Loops candidates to attach a composite 'diversity_penalty' score metric.
        """
        candidate_foods = candidate_foods.copy()
        penalties = []

        for _, row in candidate_foods.iterrows():
            state = str(row.get("state", ""))
            cuisine = str(row.get("cuisine_type", ""))
            food_group = str(row.get("food_group", ""))
            staple = str(row.get("staple_type", ""))

            # Accumulate historical category repetition penalties
            penalty = (
                state_usage.get(state, 0) * cls.STATE_PENALTY +
                cuisine_usage.get(cuisine, 0) * cls.CUISINE_PENALTY +
                food_group_usage.get(food_group, 0) * cls.FOOD_GROUP_PENALTY +
                staple_usage.get(staple, 0) * cls.STAPLE_PENALTY
            )
            penalties.append(penalty)

        candidate_foods["diversity_penalty"] = penalties
        return candidate_foods

    # ==========================================
    # 5. CALCULATE DIVERSITY SCORE
    # ==========================================
    @staticmethod
    def calculate_diversity_score(candidate_foods: pd.DataFrame) -> pd.DataFrame:
        """
        PURPOSE: Subtracts the usage penalties directly from the baseline suitability score.
        """
        candidate_foods = candidate_foods.copy()

        if "suitability_score" not in candidate_foods.columns:
            candidate_foods["suitability_score"] = 50.0

        if "diversity_penalty" not in candidate_foods.columns:
            candidate_foods["diversity_penalty"] = 0.0

        candidate_foods["diversity_score"] = (
            candidate_foods["suitability_score"] - candidate_foods["diversity_penalty"]
        )
        return candidate_foods

    # ==========================================
    # 6. COMPLETE DIVERSITY PIPELINE
    # ==========================================
    @classmethod
    def apply_diversity_rules(
        cls,
        candidate_foods: pd.DataFrame,
        previous_days: List[dict],
        current_day: int
    ) -> pd.DataFrame:
        """
        PURPOSE: Orchestrates the unified diversification execution cycle.
        Returns candidate food items ordered descending by the final diversity matrix calculation.
        """
        if candidate_foods.empty:
            return candidate_foods

        # Stage 1: Absolute exclusion filter layer
        recent_food_ids = cls.get_recent_foods(previous_days, current_day)
        filtered_foods = cls.remove_recent_foods(candidate_foods, recent_food_ids)

        # Stage 2: Track structural category frequency matrices
        state_usage = cls.track_usage(previous_days, "state")
        cuisine_usage = cls.track_usage(previous_days, "cuisine_type")
        food_group_usage = cls.track_usage(previous_days, "food_group")
        staple_usage = cls.track_usage(previous_days, "staple_type")

        # Stage 3: Calculate relative weighted performance penalties
        filtered_foods = cls.add_diversity_penalty(
            filtered_foods, state_usage, cuisine_usage, food_group_usage, staple_usage
        )

        # Stage 4: Deduct penalties from baseline ML model scores
        filtered_foods = cls.calculate_diversity_score(filtered_foods)

        # Stage 5: Finalized descending vector serialization sorting
        return filtered_foods.sort_values(by="diversity_score", ascending=False).reset_index(drop=True)