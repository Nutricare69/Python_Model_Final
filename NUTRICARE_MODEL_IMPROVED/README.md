# 🍽️ AI-Powered Indian Food Recommendation & Meal Planning System

## Overview

This project is an AI-powered Indian Food Recommendation and Meal Planning System built using:

* FastAPI
* Python
* Pandas
* Scikit-Learn
* Machine Learning
* Rule-Based Recommendation Engine
* MongoDB Ready Architecture

The system generates personalized meal plans based on:

* Age
* Gender
* Height
* Weight
* State
* Region
* Diet Type
* Activity Level
* Goal
* Medical Conditions
* Allergies

---

# Project Structure

```text
NEW_MODEL/
│
├── app/
│   ├── api/
│   ├── ml/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── database/
│
├── datasets/
│
├── requirements.txt
│
└── README.md
```

---

# Installation

## 1. Clone Repository

```bash
git clone <repository_url>

cd NEW_MODEL
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
.\venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install fastapi uvicorn pandas numpy scikit-learn joblib pydantic openpyxl
```

---

# Dataset Setup

Place dataset inside:

```text
datasets/
```

Example:

```text
datasets/
└── Indian_Food_Dataset.csv
```

Update dataset path inside:

```python
app/utils/constants.py
```

Example:

```python
DATASET_PATH = "datasets/Indian_Food_Dataset.csv"
```

---

# Dataset Requirements

Minimum required columns:

```text
food_id
canonical_food_name
state
region
meal_type
calories
protein
fat
carbs
```

Recommended columns:

```text
fiber_g
sodium_mg
iron_mg
calcium_mg
potassium_mg

fullness_score
practicality_score
frequency_score

diabetes_score
heart_health_score
muscle_gain_score
weight_loss_score

is_veg
contains_egg

suitable_diabetes
suitable_hypertension
suitable_heart_disease
suitable_thyroid
suitable_pcos
suitable_kidney_disease
suitable_gerd
```

---

# Application Execution

## Start FastAPI Server

Run from project root:

```bash
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Redoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Machine Learning Pipeline

## File Overview

### preprocessing.py

Purpose:

```text
Dataset cleaning
Missing value handling
Data validation
Duplicate removal
Column normalization
```

Run automatically during training.

---

### feature_engineering.py

Purpose:

```text
Convert food data into ML features
Generate feature vectors
Create prediction features
Build training matrix
```

---

### train_model.py

Purpose:

```text
Train food ranking model
Generate scaler
Save trained model
```

Run:

```bash
python -m app.ml.train_model
```

Generated Files:

```text
app/ml/saved_models/

food_ranker.pkl
scaler.pkl
feature_columns.pkl
```

---

### predict.py

Purpose:

```text
Load trained model
Predict food ranking scores
Generate ML scores
Rank foods
```

---

# Training the Model

From project root:

```bash
python -m app.ml.train_model
```

Expected Output:

```text
Loading dataset...

Rows Loaded: XXXX

Training model...

Training Complete

MAE : X.XXXX

R² : X.XXXX

Model Saved Successfully
```

---

# Services Overview

## bmi_service.py

Calculates:

```text
BMI
BMI Category
```

---

## calorie_service.py

Calculates:

```text
BMR
TDEE
Target Calories
```

---

## nutrition_service.py

Calculates:

```text
Protein Target
Fat Target
Carbohydrate Target
Fiber Target
Water Intake
```

---

## allergy_service.py

Handles:

```text
Gluten
Dairy
Milk
Lactose
Egg
Fish
Soy
Nuts
Peanuts
Shellfish
```

Filters unsafe foods.

---

## disease_service.py

Handles:

```text
Diabetes
Hypertension
Heart Disease
PCOS
Thyroid
Kidney Disease
GERD
```

Filters unsuitable foods.

---

## diversity_service.py

Prevents:

```text
Repeated Foods
Repeated States
Repeated Cuisine Types
Repeated Food Groups
Repeated Staples
```

Improves meal variety.

---

## meal_generator.py

Generates:

```text
Breakfast
Lunch
Snacks
Dinner
```

for each day.

---

# Repository Layer

## food_repository.py

Loads:

```text
Food Dataset
```

Functions:

```text
Load Foods
Search Foods
Filter Foods
```

---

## user_repository.py

Stores:

```text
User Profiles
Meal History
Food Preferences
Feedback History
```

---

## meal_repository.py

Stores:

```text
Generated Meal Plans
Ratings
Favorites
Regeneration Count
```

---

## feedback_repository.py

Stores:

```text
Food Ratings
Likes
Dislikes
Meal Feedback
```

---

# API Modules

## users.py

Endpoints:

```text
Create User
Update User
Get User
Delete User
```

---

## foods.py

Endpoints:

```text
Search Foods
Get Food Details
Filter Foods
```

---

## meal_plans.py

Endpoints:

```text
Generate Meal Plan
Get Meal Plan
Save Meal Plan
```

---

## feedback.py

Endpoints:

```text
Submit Feedback
Like Food
Dislike Food
Rate Food
```

---

## analytics.py

Provides:

```text
Dataset Analytics
Food Analytics
User Analytics
Feedback Analytics
System Statistics
```

---

# Example Request

POST

```text
/api/meal-plans/generate
```

Payload:

```json
{
  "name": "AJ",
  "age": 22,
  "gender": "Male",
  "weight": 75,
  "height": 175,
  "region": "South India",
  "state": "Tamil Nadu",
  "diet_type": "Vegetarian",
  "activity_level": "Moderate",
  "goal": "Weight Loss",
  "days": 7,
  "medical_conditions": [
    "Diabetes"
  ],
  "allergies": [
    "Dairy"
  ]
}
```

---

# Future Improvements

## MongoDB Integration

Replace:

```text
JSON Repositories
```

with:

```text
MongoDB Collections
```

Collections:

```text
users
meal_plans
feedback
```

---

## Feedback Learning

Use:

```text
Likes
Dislikes
Ratings
```

to retrain recommendation models.

---

## Advanced ML

Future models:

```text
Random Forest
XGBoost
LightGBM
Hybrid Recommendation Engine
```

---

# Troubleshooting

## Model Not Found

Run:

```bash
python -m app.ml.train_model
```

---

## Dataset Not Found

Verify:

```python
DATASET_PATH
```

inside:

```text
app/utils/constants.py
```

---

## FastAPI Not Starting

Install:

```bash
pip install fastapi uvicorn
```

Run:

```bash
uvicorn app.main:app --reload
```

---

# Authors

Final Year CSE Project

AI-Based Indian Food Recommendation & Meal Planning System
