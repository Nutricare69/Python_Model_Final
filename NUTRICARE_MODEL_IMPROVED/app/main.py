# ============================================================================
# FILE: app/main.py
# ROLE: CORE ENTRY POINT & ROUTE GATEWAY (Microservices Architecture)
# 
# ARCHITECTURE NOTE:
# This file initializes the ASGI server for the stateless Python compute core. 
# It configures CORS middleware to secure processing boundaries and mounts the 
# high-performance calculation routers.
#
# THE DATAFLOW CONTRACT:
# 1. React Frontend sends data or actions to the Node.js API Gateway.
# 2. Node.js processes permissions, auth states, and queries MongoDB collections.
# 3. Node.js forwards JSON payloads internally via HTTP to this FastAPI gateway.
# 4. Python processes vectors, ranks candidates via ML models, and responds 
#    directly back to Node.js without writing to any database.
# ============================================================================
from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ===== Import API Compute Routers =====
# Each router maps pure vector compute endpoints to the Node.js backend.
from app.api.users import router as users_router
from app.api.foods import router as foods_router
from app.api.recommendations import router as recommendations_router
from app.api.meal_plans import router as meal_plans_router
from app.api.analytics import router as analytics_router
from app.api.feedback import router as feedback_router

# Import application metadata constants
from app.utils.constants import APP_NAME, APP_VERSION

load_dotenv()  # Load environment variables from .env file

# ==========================================
# FASTAPI APP INSTANCE
# ==========================================
# Initialized as a pure stateless compute cluster engine
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Stateless ML Matrix Processing & Nutrition Analytics Compute Engine"
)

# ==========================================
# CORS MIDDLEWARE configuration
# ==========================================
# Allows safe internal network packet transactions from your Node.js Gateway.

raw_origins = os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Handles http:// and https:// origins cleanly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==========================================
# TELEMETRY & HEARTBEAT ENDPOINTS
# ==========================================
@app.get("/")
def root():
    """
    Verifies cluster runtime availability status.
    """
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "engine_status": "stateless_compute_core_operational"
    }


@app.get("/health")
def health_check():
    """
    Kubernetes liveness probes or DevOps monitoring tools can hit this path 
    to verify compute cluster health independently.
    """
    return {
        "status": "healthy"
    }


# ==========================================
# ROUTER MOUNTING MATRIX
# ==========================================

# === HEALTH SUMMARY COMPUTE ===
# Prefix: /api/users/summary
# Primary Function: POST /summary calculates metabolic targets from raw dictionaries.
app.include_router(
    users_router,
    prefix="/api/users",
    tags=["Health Summary Compute Engine"]
)

# === FOOD DATA MATRIX ===
# Prefix: /api/foods
# Primary Function: Processes array groupings and feature columns.
app.include_router(
    foods_router,
    prefix="/api/foods",
    tags=["Food Feature Vectors"]
)

# === PERSONALIZED ML RECOMMENDATIONS ===
# Prefix: /api/recommendations
# Primary Function: POST / runs inference loops across models (food_ranker.pkl).
app.include_router(
    recommendations_router,
    prefix="/api/recommendations",
    tags=["Personalized ML Recommendation Pipeline"]
)

# === ALGORITHMIC MEAL PLAN GENERATION ===
# Prefix: /api/meal-plans
# Primary Function: Generates deep daily loops (1-day, 7-day, 14-day) with diversity caps.
app.include_router(
    meal_plans_router,
    prefix="/api/meal-plans",
    tags=["Meal Plan Orchestration Engine"]
)

# === DATA ANALYTICS & METRIC PROCESSING ===
# Prefix: /api/analytics
# Primary Function: Computes statistical distributions for administrative panels.
app.include_router(
    analytics_router,
    prefix="/api/analytics",
    tags=["Analytics Compute Engine"]
)

# === REINFORCEMENT FEEDBACK LOGS ===
# Prefix: /api/feedback
# Primary Function: Normalizes explicit evaluation scores to refine ranking matrices.
app.include_router(
    feedback_router,
    prefix="/api/feedback",
    tags=["Feedback Metric Processing"]
)