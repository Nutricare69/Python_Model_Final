# ============================================================================
# FILE: app/services/bmi_service.py
# ROLE: STATELESS BMI COMPUTE SERVICE (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This service acts as a pure mathematical execution engine. It contains no 
# database components.
#
# THE PIPELINE:
# 1. Node.js fetches raw 'weight' and 'height' fields from MongoDB.
# 2. Node.js fires an internal POST request to the Python compute engine.
# 3. This service executes metabolic parsing and passes structured health risks
#    directly back up the network loop.
# ============================================================================

from dataclasses import dataclass


# ==========================================
# BMIResult Dataclass (DTO)
# ==========================================
@dataclass
class BMIResult:
    """
    PURPOSE: Data Transfer Object (DTO) encapsulating the baseline BMI payload.
    ROLE: Enforces strict schema shape before handing data back to the routing layer.
    """
    bmi: float
    category: str
    health_risk: str  # Added to match the structural requirements of the React dashboard

    def to_dict(self) -> dict:
        """
        Converts the DTO properties into a standard serializable Python dictionary.
        """
        return {
            "bmi": self.bmi,
            "category": self.category,
            "health_risk": self.health_risk
        }


# ==========================================
# BMIService – Core BMI Logic
# ==========================================
class BMIService:
    """
    Provides isolated, stateless utility methods for processing physiological metrics.
    Uses standard World Health Organization (WHO) threshold classifications.
    """

    # ==========================================
    # BMI Calculation Method (FIXED INDENTATION)
    # ==========================================
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> BMIResult:
        r"""
        PURPOSE: Compiles numeric weight and height data into a unified health risk assessment.
        
        MATHEMATICAL FORMULA:
        The logic processes metric scale transformations using standard body mass indexing:
        
        $$BMI = \frac{\text{weight}_{\text{kg}}}{\left(\frac{\text{height}_{\text{cm}}}{100}\right)^2}$$
        
        RAISES:
            ValueError: If metric variable parameters are sub-zero or zero.
        """
        if weight_kg <= 0:
            raise ValueError("Weight parameter must be a positive non-zero value.")

        if height_cm <= 0:
            raise ValueError("Height parameter must be a positive non-zero value.")

        # Transform scale metrics from centimeters into meters
        height_m = height_cm / 100

        # Execute core indexing equation
        bmi = weight_kg / (height_m * height_m)
        bmi = round(bmi, 2)

        # Map metric ranges to textual categories and evaluate health risk tiers
        category = BMIService.get_bmi_category(bmi)
        health_risk = BMIService.get_health_risk(bmi)

        return BMIResult(
            bmi=bmi,
            category=category,
            health_risk=health_risk
        )

    # ==========================================
    # BMI Category Determination
    # ==========================================
    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal Weight"
        elif bmi < 30:
            return "Overweight"
        elif bmi < 35:
            return "Obese Class I"
        elif bmi < 40:
            return "Obese Class II"
        return "Obese Class III"

    # ==========================================
    # Boolean BMI Checks (Convenience Methods)
    # ==========================================
    @staticmethod
    def is_underweight(bmi: float) -> bool:
        return bmi < 18.5

    @staticmethod
    def is_normal_weight(bmi: float) -> bool:
        return 18.5 <= bmi < 25

    @staticmethod
    def is_overweight(bmi: float) -> bool:
        return 25 <= bmi < 30

    @staticmethod
    def is_obese(bmi: float) -> bool:
        return bmi >= 30

    # ==========================================
    # Health Risk Assessment
    # ==========================================
    @staticmethod
    def get_health_risk(bmi: float) -> str:
        """
        Evaluates comorbidity trends based on dimensional weight profiles.
        """
        if bmi < 18.5:
            return "Nutritional Risk"
        elif bmi < 25:
            return "Low Risk"
        elif bmi < 30:
            return "Moderate Risk"
        elif bmi < 35:
            return "High Risk"
        elif bmi < 40:
            return "Very High Risk"
        return "Extremely High Risk"